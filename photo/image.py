import os
import Image
from StringIO import StringIO

from django.conf import settings

if settings.S3_STORAGE:
    from storage import S3StorageBackend as StorageBackend
else:
    from storage import FileSystemStorageBackend as StorageBackend

class ImageHandlerException(Exception):
    pass


class ImageHandler(object):

    def __init__(self):
        self._rimage = None
        self.user = None
        self.draft = None
        self.album = None
        self.storage = None
        self.storage_new = None
        self._images = {}

    def load_by_image_user(self, image, user):
        self._rimage = image
        self.user = user
        self.storage = StorageBackend('draft/new', user.username, image.name)

    def load_by_filename_user(self, filename, user):
        self.user = user
        self.storage = StorageBackend('draft/new', user.username, filename)

    def load_by_draft(self, filename, draft):
        self.draft = draft
        self.user = draft.user
        self.storage = StorageBackend('draft', str(draft.id), filename)
        self.storage_new = StorageBackend('draft/new', self.user.username,
                                          filename)

    def load_by_filename_album(self, filename, album, user=None):
        self.album = album
        self.storage = StorageBackend('album', str(self.album.id), filename)
        if user:
            self.user = user
            self.storage_new = StorageBackend('draft/new', user.username,
                                              filename)

    def load_by_album(self, album):
        self.album = album
        self.storage = StorageBackend('album', str(self.album.id))

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

        if self._images:
            return self._images

        images = {
            'original': {
                'filename': self.storage.filename,
                'filepath': self.storage.get_filepath(),
                'urlpath': self.storage.get_url(),
            }
        }
        for key, size in settings.IMAGE_SIZES.items():
            filename = ImageHandler.name(self.storage.filename, key)
            filepath = self.storage.get_filepath(filename)
            urlpath = self.storage.get_url(filename)
            if not self.storage.is_file(filename):
                # test in new path .../new/
                if self.storage_new:
                    urlpath = self.storage_new.get_url(filename)
                    filepath = self.storage_new.get_filepath(filename)
                    if not self.storage_new.is_file(filename):
                        continue
                else:
                    continue
            images[key] = {
                'filename': filename,
                'filepath': filepath,
                'urlpath': urlpath,
                'size': size
            }
        self._images = images
        return images

    def save_thumbnails(self):
        if not self._rimage or not (self.storage and self.storage.filename):
            msg = 'ImageHandler is not loaded by image buffer.'
            raise ImageHandlerException(msg)
        stream = self._rimage.read()
        self.storage.save_file(stream, binary=True)
        self._rimage.close()
        for key, size in settings.IMAGE_SIZES.items():
            ffile = StringIO(stream)
            ffile.seek(0)
            img = Image.open(ffile)
            img.thumbnail(size, Image.ANTIALIAS)
            filename = ImageHandler.name(self.storage.filename, key)
            ffile = StringIO()
            img.save(ffile, format='JPEG')
            buffer = ffile.getvalue()
            self.storage.save_file(buffer, filename, binary=False)

    def copy_new_images_to_draft(self, user):
        newhandler = ImageHandler()
        newhandler.load_by_filename_user(self.storage.filename, user)
        self.storage.copy_files(newhandler.paths())

    def copy_album_images_to_draft(self, album):
        newhandler = ImageHandler()
        newhandler.load_by_filename_album(self.storage.filename, album)
        self.storage.copy_files(newhandler.paths())

    def copy_images_to_album(self, draft):
        newhandler = ImageHandler()
        newhandler.load_by_draft(self.storage.filename, draft)
        self.storage.copy_files(newhandler.paths())

    def delete(self):
        if not self.storage.filename:
            msg = 'ImageHandler is not loaded'
            raise ImageHandlerException(msg)
        filenames = [i['filename'] for i in self.images().values()]
        self.storage.remove_files(filenames)

    def delete_path(self):
        self.storage.remove_base_path()

    @staticmethod
    def delete_junk(draft):
        files = []
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
                files += handler.files()

        storage = StorageBackend('draft', str(draft.id))
        storage.remove_base_contents(except_files=files)

    def paths(self):
        values = self.images().values()
        paths = [n['filepath'] for n in values if n.get('filename')]
        return paths

    def files(self):
        values = self.images().values()
        files = [n['filename'] for n in values if n.get('filename')]
        return files

    def url(self, key):
        return self.urls()['image_%s_url' % key]

    def urls(self):
        items = self.images().items()
        val = lambda k, n: ('image_%s_url' % k, n['urlpath'])
        u = [val(k, n) for k, n in items if n.get('filename')]
        return dict(u)
