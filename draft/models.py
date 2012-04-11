from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.db import models
from django.template.loader import get_template
from django.template.context import Context
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as ug

from lib import fields


class FakeRelatedManager(object):

    def __init__(self, values):
        self.values = values

    def all(self, *args, **kwargs):
        return self.values

    def filter(self, *args, **kwargs):
        return self.values


class ContentDraft(models.Model):
    """
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField(null=True)
    content_date = models.DateTimeField(auto_now=True)
    content = fields.PickleField(default='')
    object = generic.GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User)

    def __unicode__(self):
        return ug("%s %s - %s by %s") % (
            self.object,
            self.content_type,
            self.content_date.strftime("%d/%m/%Y %H:%M"),
            self.user
        )

    def render(self):
        model = self.content_type.model_class()
        template = get_template(model.template_view)
        varname = model.template_varname

        # Overriding related managers with None - hack
        relmanagers = {}
        for key, value in self.get_content_object().items():
            if key == '__rel_fields__':
                for relname in value.keys():
                    relmanagers[relname] = getattr(model, relname)
                    relmodel = getattr(model, relname).related.model
                    setattr(model, relname, relmodel)

        obj = model()
        for key, value in self.get_content_object().items():
            if key == '__rel_fields__':
                for relname, values in value.items():
                    relmodel = getattr(obj, relname)
                    vals = []
                    for d in values:
                        obj = relmodel()
                        for attr, v in d.items():
                            setattr(obj, attr, v)
                        vals.append(obj)
                    manager = FakeRelatedManager(vals)
                    setattr(obj, relname, manager)
            else:
                setattr(obj, key, value)
        c = {varname: obj}
        rendered = template.render(Context(c))
        # Restoring managers to class - hack
        for relname, relmanager in relmanagers.items():
            setattr(model, relname, relmanager)
        return rendered