from django.contrib.contenttypes.models import ContentType
from django import forms
from django.utils import simplejson

from models import ContentDraft

class CmsForm(forms.ModelForm):

    class Media:
        css = {
            'all': ('/media/css/cleditor/jquery.cleditor.css',
                    '/media/css/cleditor/jquery.cleditor.cmsplugin.css')
        }
        js = ('/media/js/jquery/jquery.fileupload.js',
              '/media/js/jquery/cleditor/jquery.cleditor.js',
              '/media/js/jquery/cleditor/jquery.cleditor.cmsplugin.js',
              '/media/js/jquery/cleditor/jquery.cleditor.addimageplugin.js',
              '/media/js/jquery/cleditor/jquery.cleditor.slideshowplugin.js',
              '/media/js/hbeditor.js',
              '/media/js/draftform.js')


    def __init__(self, user, draft=None, *args, **kwargs):
        self.user = user
        self.draft = draft
        self._js_fields = {}
        super(CmsForm, self).__init__(*args, **kwargs)
        if not self.draft:
            self.draft = ContentDraft()
        else:
            self.initial = draft.get_content_object()

    def publish(self):
        data = self.draft.get_content_object()
        self.cleaned_data = self._prepare_data_to_publish(data)
        self._errors = {}
        self._post_clean()
        self.draft.object_id = super(CmsForm, self).save().id
        self.draft.save()
        self._publish_rel_fields()
        return self.instance

    def _publish_rel_fields(self):
        cleaned_data = self.draft.get_content_object()
        if not cleaned_data.get('__rel_fields__'):
            return
        for relname, datalist in cleaned_data['__rel_fields__'].items():
            rel = getattr(self.instance, relname)
            rel.all().delete()
            for data in datalist:
                cleandata = self._prepare_rel_data_to_publish(rel, data)
                rel.create(**cleandata)

    def _prepare_data_to_publish(self, data):
        return data

    def _prepare_rel_data_to_publish(self, rel, data):
        names = [i.name for i in rel.model._meta.fields]
        cleandata = dict([(k, v) for k, v in data.items() if k in names])
        return cleandata

    def js_is_valid(self, data):
        return True

    def js_fields(self):
        return self._js_fields

    @property
    def js_fields_json(self):
        return simplejson.dumps(self._js_fields)

    def _set_rel_fields(self, reldata):
        self.cleaned_data['__rel_fields__'] = reldata

    def save(self, *args, **kwargs):
        ct = ContentType.objects.get_for_model(self._meta.model)
        self.draft.content_type = ct
        self.draft.set_content_object(self.cleaned_data)
        self.draft.user = self.user
        if self.instance:
            self.draft.object_id = self.instance.id
        self.draft.save()

