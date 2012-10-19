import os
from shutil import copy, rmtree
from boto.s3.connection import S3Connection

from django.conf import settings

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

S3_CONNECTION = None
BUCKET = None
S3_BUCKET_URL_PATH = None

if settings.S3_STORAGE:
    S3_CONNECTION = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    BUCKET = S3_CONNECTION.get_bucket(settings.S3_BUCKET_NAME, validate=False)
    S3_BUCKET_URL_PATH = BUCKET.generate_url(0).split('?')[0]

class BaseStorageBackend(object):
    """ Abstract class
    """
    def __init__(self, path, subpath, filename=None):
        self.path = os.path.join(path, subpath)
        self.base_path = None
        self.base_url_path = None
        self.filename = filename

    def make_dir(self, path):
        raise NotImplementedError

    def remove_base_path(self):
        raise NotImplementedError

    def remove_file(self, filename):
        raise NotImplementedError

    def remove_files(self, filenames):
        raise NotImplementedError

    def is_file(self, filename):
        raise NotImplementedError

    def list_dir(self, path):
        raise NotImplementedError

    def save_file(self, stream, filename=None, binary=False):
        raise NotImplementedError

    def copy_files(self, paths):
        raise NotImplementedError

    def get_filepath(self, filename):
        raise NotImplementedError

    def get_url(self, filename=None):
        raise NotImplementedError


class FileSystemStorageBackend(BaseStorageBackend):

    def __init__(self, *args, **kwargs):
        super(FileSystemStorageBackend, self).__init__(*args, **kwargs)
        self.base_path = os.path.join(settings.UPLOAD_PATH, self.path)
        self.base_url_path = "%s/%s" % (settings.UPLOAD_URLPATH, self.path)

        try:
            self.make_dir(self.base_path)
        except:
            pass

    def _p(self, path):
        return os.path.join(self.base_path, path)

    def make_dir(self, path):
        path = self._p(path)
        os.mkdir(path)

    def remove_base_contents(self, except_files=[]):
        if os.path.isdir(self.base_path):
            for filename in os.listdir(self.base_path):
                if filename in except_files:
                    continue
                self.remove_file(filename)

    def remove_base_path(self):
        if os.path.isdir(self.base_path):
            rmtree(self.base_path)

    def remove_file(self, filename):
        path = self._p(filename)
        if os.path.isfile(path):
            os.remove(path)

    def remove_files(self, filenames):
        for filename in filenames:
            self.remove_file(filename)

    def is_file(self, filename):
        return os.path.isfile(self._p(filename))

    def list_dir(self, path):
        path = self._p(path)
        return os.listdir(path)

    def save_file(self, stream, filename=None, binary=False):
        if not filename:
            filename = self.filename
        path = self._p(filename)
        mode = 'w'
        if binary:
            mode += 'b'
        afile = open(path, mode)
        afile.write(stream)
        afile.close()

    def copy_files(self, paths):
        for path in paths:
            if os.path.isfile(path):
                dirname, filename = os.path.split(path)
                filepath = os.path.join(self.base_path, filename)
                copy(path, filepath)

    def get_filepath(self, filename=None):
        if not filename:
            filename = self.filename
        return os.path.join(self.base_path, filename)

    def get_url(self, filename=None):
        if not filename:
            filename = self.filename
        url = "%s/%s" % (self.base_url_path, filename)
        return url


class S3StorageBackend(BaseStorageBackend):

    base_keys = {}
    global_keys = {}

    def __init__(self, *args, **kwargs):
        super(S3StorageBackend, self).__init__(*args, **kwargs)
        self.conn = S3_CONNECTION
        self.bucket = BUCKET
        self.base_path = self._p(self.path)
        self.policy = getattr(settings, 'S3_POLICY', 'public-read')
        self.base_key = self.get_or_make_dir(self.base_path)
        self.base_url_path = "%s%s" % (S3_BUCKET_URL_PATH, self.base_path)

    def _p(self, path):
        if path.strip().endswith('/'):
            return path
        else:
            return "%s/" % path

    def _pf(self, filename):
        return os.path.join(self.base_path, filename)

    def get_key(self, path):
        if self.global_keys.get(path):
            return self.global_keys[path]
        key = self.bucket.get_key(path)
        if key:
            S3StorageBackend.global_keys[path] = key
        return key

    def get_or_make_dir(self, path):
        path = self._p(path)
        if self.base_keys.get(path):
            return self.base_keys[path]
        key = self.bucket.get_key(path)
        if not key:
            splited = path.split('/')
            bkey_name = ''

            for key_name in splited:
                key_name = bkey_name + self._p(key_name)
                bkey_name = key_name
                key = self.bucket.get_key(key_name)
                if not key:
                    key = self.make_dir(key_name)
        S3StorageBackend.base_keys[path] = key
        return key

    def make_dir(self, path):
        path = self._p(path)
        key = self.bucket.new_key(path)
        key.set_contents_from_string('', policy=self.policy)
        return key


    def remove_base_contents(self, except_files=[]):
        keys = self.list_dir(self.base_path)
        except_files = [self._pf(f) for f in except_files]
        keys_names = [key.name for key in keys if key.name not in except_files]
        result = self.bucket.delete_keys(keys_names)
        if result.errors:
            print result.errors

    def remove_base_path(self):
        keys = self.list_dir(self.base_path)
        keys_names = [key.name for key in keys]
        result = self.bucket.delete_keys(keys_names)
        if result.errors:
            print result.errors

    def remove_file(self, filename):
        path = self._pf(filename)
        key = self.get_key(path)
        if key:
            bucket.delete_key(key)

    def remove_files(self, filenames):
        result = self.bucket.delete_keys([self._pf(f) for f in filenames])
        if result.errors:
            print result.errors

    def is_file(self, filename):
        path = self._pf(filename)
        return bool(self.get_key(path))

    def list_dir(self, path):
        path = self._p(path)
        return self.bucket.list(prefix=path)

    def save_file(self, stream, filename=None, binary=False):
        if not filename:
            filename = self.filename
        path = self._pf(filename)
        key = self.bucket.new_key(path)
        key.set_contents_from_string(stream, policy=self.policy)
        S3StorageBackend.global_keys[path] = key

    def copy_files(self, paths):
        for path in paths:
            key = self.get_key(path)
            if key:
                dirname, filename = os.path.split(key.name)
                filepath = self._pf(filename)
                try:
                    key.copy(self.bucket.name, filepath, preserve_acl=True)
                except:
                    key = self.bucket.get_key(path)
                    if key:
                        key.copy(self.bucket.name, filepath, preserve_acl=True)

    def get_filepath(self, filename=None):
        if not filename:
            filename = self.filename
        return self._pf(filename)

    def _url_by_key(self, key):
        return os.path.join(self.base_url_path, key.name.split('/')[-1])

    def get_url(self, filename=None):
        if not filename:
            filename = self.filename
        return os.path.join(self.base_url_path, filename)
