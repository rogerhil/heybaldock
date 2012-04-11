from copy import copy

from django.core.validators import ValidationError
from django.utils.translation import ugettext as _

from draft import forms
from lib.youtube import validate_youtube_url, youtube_small_info_by_url
from models import VideoAlbum


class AlbumForm(forms.CmsForm):
    """
    """

    class Meta:
        model = VideoAlbum
        fields = ('name', 'description', 'listable', 'event')


    class Media:
        js = ('/media/js/videoalbumform.js',)


    def __init__(self, *args, **kwargs):
        super(AlbumForm, self).__init__(*args, **kwargs)
        self._js_fields['url'] = []
        content = None
        if self.draft:
            content = self.draft.get_content_object()
        if content and not self.data:
            urls = [v['url'] for v in content['__rel_fields__']['videos']]
            self._js_fields['url'] = [{'value': url} for url in urls]
        elif self.instance and self.instance.id and not self.data:
            urls = self.instance.videos.all().values_list('url', flat=True)
            self._js_fields['url'] = [{'value': url} for url in urls]
        elif self.data:
            urls = self.data.getlist('url')
            self._js_fields['url'] = [{'value': url} for url in urls]

    def js_is_valid(self, data):
        success = True
        if not 'url' in data:
            msg = _("A video album must have at least one video url")
            self._js_fields['url']['__all__']['error'] = msg
            return False
        if not self._js_fields['url']:
            self._js_fields['url'] = [{'value': u} for u in \
                                      data.getlist('url')]
        urls = data.getlist('url')
        for i, url in enumerate(urls):
            try:
                self._js_fields['url'][i]
            except IndexError:
                self._js_fields['url'].append({'value': url})
            if not url.strip():
                msg = _("Url cannot be empty")
                self._js_fields['url'][i]['error'] = msg
                success = False
                continue
            try:
                info = validate_youtube_url(url)
                self._js_fields['url'][i]['value'] = info['url']
            except ValidationError, err:
                self._js_fields['url'][i]['error'] = err.messages[0]
                success = False
        urls = [i['value'] for i in self._js_fields['url']]
        for i, url in enumerate(urls):
            l = copy(urls)
            l.pop(i)
            if url in l:
                if not self._js_fields['url'][i].get('error'):
                    msg = _('This video is provided more than once')
                    self._js_fields['url'][i]['error'] = msg
                    success = False
        return success

    def save(self, *args, **kwargs):
        reldata = []
        for url in self._js_fields['url']:
            info = youtube_small_info_by_url(url['value'])
            reldata.append(info)
        self._set_rel_fields({'videos': reldata})
        super(AlbumForm, self).save(*args, **kwargs)


