from django.utils.translation import ugettext as _

from draft import forms
from models import PhotoAlbum
from image import ImageHandler, ImageHandlerException

class AlbumForm(forms.CmsForm):
    """
    """

    class Meta:
        model = PhotoAlbum
        fields = ('name', 'description', 'listable', 'flyer', 'event')


    class Media:
        js = ('/media/js/jquery/jquery.ui.widget.js',
              '/media/js/jquery/jquery.iframe-transport.js',
              '/media/js/jquery/jquery.fileupload.js',
              '/media/js/photoalbumform.js')

    def __init__(self, *args, **kwargs):
        super(AlbumForm, self).__init__(*args, **kwargs)
        self._js_fields['photo'] = []
        content = None
        if self.draft:
            content = self.draft.get_content_object()
        if content and not self.data:
            photos = [self._build_img_data(v['image'], v['description']) \
                                  for v in content['__rel_fields__']['photos']]
            self._js_fields['photo'] = photos
        elif self.instance and self.instance.id and not self.data:
            qs = self.instance.photos.all()
            photos = qs.values_list('image', 'description')
            self._js_fields['photo'] = [self._build_img_data(n, d) for n, d
                                                                    in photos]
        elif self.data:
            self._js_fields['photo'] = self._load_from_data(self.data)

    def _build_img_data(self, name, description):
        handler = ImageHandler()
        if self.draft and self.draft.id:
            handler.load_by_draft(name, self.draft)
        elif self.instance and self.instance.id:
            if self.user:
                handler.load_by_filename_album(name, self.instance, self.user)
            else:
                handler.load_by_filename_album(name, self.instance)
        else:
            handler.load_by_filename_user(name, self.user)

        if not handler.urls():
            handler.load_by_filename_user(name, self.user)
            if not handler.urls():
                raise ImageHandlerException("Image %s not found." % name)

        img = {
            'name': {'value': name},
            'description': {'value': description},
            'url': handler.url('small'),
            'url_view': handler.url('big')
        }
        return img

    def _load_from_data(self, data):
        names_descriptions = zip(data.getlist('image_name'),
                                 data.getlist('image_description'))
        photo_data = []
        for n, d in names_descriptions:
            img = self._build_img_data(n, d)
            photo_data.append(img)
        return photo_data

    def js_is_valid(self, data):
        success = True
        if not 'image_name' in data:
            msg = _("A photo album must have at least one photo")
            self._js_fields['__all__'] = {'error': msg}
            return False

        photo_data = self._load_from_data(data)
        if not self._js_fields['photo']:
            self._js_fields['photo'] = photo_data

        for i, d in enumerate(photo_data):
            try:
                self._js_fields['photo'][i]
            except IndexError:
                self._js_fields['photo'].append(d)
            if not d['description']['value'].strip():
                msg = _("Photo description cannot be empty")
                self._js_fields['photo'][i]['description']['error'] = msg
                success = False
                continue
        return success

    def _prepare_data_to_publish(self, data):
        cleandata = super(AlbumForm, self)._prepare_data_to_publish(data)
        handler = ImageHandler()
        handler.load_by_filename_album(cleandata['name'], self.instance)
        handler.delete_path()
        return cleandata

    def _prepare_rel_data_to_publish(self, rel, data):
        cleandata = super(AlbumForm, self)._prepare_rel_data_to_publish(rel,
                                                                         data)
        handler = ImageHandler()
        handler.load_by_filename_album(cleandata['image'], self.instance)
        handler.copy_images_to_album(self.draft)
        return cleandata

    def save(self, *args, **kwargs):
        super(AlbumForm, self).save(*args, **kwargs)
        reldata = []
        for photo in self._js_fields['photo']:
            handler = ImageHandler()
            handler.load_by_draft(photo['name']['value'], self.draft)
            handler.copy_new_images_to_draft(self.user)
            handler.copy_album_images_to_draft(self.user)
            info = {
                'description': photo['description']['value'],
                'image': photo['name']['value']
            }
            info.update(handler.urls())
            reldata.append(info)
        self._set_rel_fields({'photos': reldata})
        self.draft.set_content_object(self.cleaned_data)
        self.draft.save()
        newhandler = ImageHandler()
        newhandler.load_by_filename_user('', self.user)
        newhandler.delete_path()
        ImageHandler.delete_junk(self.draft)
