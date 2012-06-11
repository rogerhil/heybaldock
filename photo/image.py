import os
import Image
from shutil import copy, rmtree

from django.conf import settings


class ImageHandlerException(Exception):
    pass


class ImageHandler(object):

    def __init__(self):
        self._rimage = None
        self._filename = None
        self.user = None
        self.draft = None
        self.album = None
        self.path = None
        self.urlpath = None
        self.pathnew = None
        self.urlpathnew = None

    def load_by_image_user(self, image, user):
        self._rimage = image
        self._filename = image.name
        self.user = user
        self._set_path_by_user()

    def load_by_filename_user(self, filename, user):
        self._filename = filename
        self.user = user
        self._set_path_by_user()

    def load_by_draft(self, filename, draft):
        self.draft = draft
        self.user = draft.user
        self._filename = filename
        self._set_path_by_draft()

    def load_by_filename_album(self, filename, album):
        self._filename = filename
        self.album = album
        self._set_path_by_album()

    def load_by_album(self, album):
        self.album = album
        self._set_path_by_album()

    def _set_path_by_user(self):
        self.path = os.path.join(settings.DRAFT_UPLOAD_PATH_NEW,
                                 self.user.username)
        self.urlpath = "%s/%s" % (settings.DRAFT_UPLOAD_URLPATH_NEW,
                                  self.user.username)

    def _set_path_by_draft(self):
        self.path = os.path.join(settings.DRAFT_UPLOAD_PATH,
                                 str(self.draft.id))
        self.urlpath = "%s/%s" % (settings.DRAFT_UPLOAD_URLPATH,
                                  str(self.draft.id))
        self.pathnew = os.path.join(settings.DRAFT_UPLOAD_PATH_NEW,
                                    self.user.username)
        self.urlpathnew = "%s/%s" % (settings.DRAFT_UPLOAD_URLPATH_NEW,
                                     self.user.username)

    def _set_path_by_album(self):
        self.path = os.path.join(settings.UPLOAD_PATH,
                                 str(self.album.id))
        self.urlpath = "%s/%s" % (settings.UPLOAD_URLPATH,
                                  str(self.album.id))

    @staticmethod
    def raw_name(name):
        return ".".join(name.split('.')[:-1])

    @staticmethod
    def name(name, sufix):
        name = "%s.%s.jpg" % (ImageHandler.raw_name(name), sufix)
        return name

    def original_filename(self):
        return self._rimage.name

    def images(self):
        images = {}
        filepath = os.path.join(self.path, self._filename)
        if os.path.isfile(filepath):
            images['original'] = {'filepath': filepath}
        for key, size in settings.IMAGE_SIZES.items():
            name = ImageHandler.name(self._filename, key)
            filepath = os.path.join(self.path, name)
            urlpath = "%s/%s" % (self.urlpath, name)
            if not os.path.isfile(filepath):
                # test in new path .../new/
                if self.draft and self.pathnew:
                    filepath = os.path.join(self.pathnew, name)
                    urlpath = "%s/%s" % (self.urlpathnew, name)
                    if not os.path.isfile(filepath):
                        continue
                else:
                    continue
            images[key] = {
                'filepath': filepath,
                'urlpath': urlpath,
                'name': name,
                'size': size
            }
        return images

    def save_thumbnails(self):
        if not self._rimage or not self._filename:
            msg = 'ImageHandler is not loaded by image buffer.'
            raise ImageHandlerException(msg)
        try:
            os.mkdir(self.path)
        except:
            pass
        pathfile = os.path.join(self.path, self._filename)
        img_file = open(pathfile, 'wb')
        img_file.write(self._rimage.read())
        img_file.close()
        self._rimage.close()
        for key, size in settings.IMAGE_SIZES.items():
            img = Image.open(pathfile)
            img.thumbnail(size, Image.ANTIALIAS)
            name = ImageHandler.name(self._filename, key)
            p = os.path.join(self.path, name)
            img.save(p)

    def _copy_images(self, newhandler):
        paths = newhandler.paths()
        try:
            os.mkdir(self.path)
        except:
            pass
        for path in paths:
            dirname, filename = os.path.split(path)
            filepath = os.path.join(self.path, filename)
            copy(path, filepath)

    def copy_new_images_to_draft(self, user):
        newhandler = ImageHandler()
        newhandler.load_by_filename_user(self._filename, user)
        self._copy_images(newhandler)

    def copy_album_images_to_draft(self, album):
        newhandler = ImageHandler()
        newhandler.load_by_filename_album(self._filename, album)
        self._copy_images(newhandler)

    def copy_images_to_album(self, draft):
        newhandler = ImageHandler()
        newhandler.load_by_draft(self._filename, draft)
        self._copy_images(newhandler)

    def delete(self):
        if not self._filename:
            msg = 'ImageHandler is not loaded'
            raise ImageHandlerException(msg)
        for image in self.images().values():
            os.remove(image['filepath'])

    def delete_path(self):
        if not self.path:
            msg = 'ImageHandler is not loaded'
            raise ImageHandlerException(msg)
        if os.path.isdir(self.path):
            rmtree(self.path)

    @staticmethod
    def delete_junk(draft):
        path = os.path.join(settings.DRAFT_UPLOAD_PATH,
                                 str(draft.id))
        paths = []
        content = draft.get_content_object()
        rel_fields = content.get('__rel_fields__', {})
        photos = rel_fields.get('photos', [])
        if not photos:
            return
        for img in photos:
            image = img.get('image')
            if image:
                handler = ImageHandler()
                handler.load_by_draft(image, draft)
                paths += handler.paths()
        for f in os.listdir(path):
            p = os.path.join(path, f)
            if p not in paths:
                os.remove(p)

    def paths(self):
        p = [n['filepath'] for n in self.images().values() if n.get('name')]
        return p

    def url(self, key):
        return self.urls()['image_%s_url' % key]

    def urls(self):
        u = [('image_%s_url' % k, n['urlpath']) \
                        for k, n in self.images().items() if n.get('name')]
        return dict(u)
