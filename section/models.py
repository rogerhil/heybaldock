from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.template.loader import get_template_from_string
from django.template.context import RequestContext

from draft.models import ContentDraft

SECTIONS = {
    'home': {},
    'eventos': {'types': [15]},
    'fotos': {},
    'videos': {},
    'contato': {}
}


class Section(models.Model):
    """
    """
    menu_title = models.CharField(_("Menu title"), max_length=24)
    title = models.CharField(_("Title"), max_length=64)
    description = models.CharField(_("Description"), max_length=255)
    slug = models.CharField(_("Menu title"), max_length=16, unique=True)
    content = models.TextField(_("Content"))
    updated = models.DateField(auto_now=True)
    user_updated = models.ForeignKey(User)
    order = models.IntegerField()
    active = models.BooleanField(default=True)

    template_view = "section/section_content.html"
    template_varname = 'section'

    def __unicode__(self):
        return self.menu_title

    def content_rendered(self, request):
        content = "{% load wysiwygtags %}\n" + self.content
        template = get_template_from_string(content)
        c = dict()
        return template.render(RequestContext(request, c))

    def draft_data(self):
        data = {
            'menu_title': self.menu_title,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'content_rendered': self.content_rendered
        }
        return data

    def url(self):
        return reverse('section_view', args=(self.slug,))

    @property
    def media(self):
        if self.slug == 'videos':
            return {'scripts': ['/media/js/videos.js']}
        if self.slug == 'fotos':
            return {'scripts': ['/media/js/photos.js']}
        if self.slug == 'contato':
            return {'styles': ['/media/css/form.css']}

    @staticmethod
    def form():
        from forms import SectionForm
        return SectionForm

    @property
    def config(self):
        return SECTIONS[self.slug]

    def drafts_related(self):
        models = [settings.SECTION_CT_ID] + self.config.get('types', [])
        drafts = ContentDraft.objects.filter(content_type__in=models,
                                             object_id=self.id)
        return  drafts
