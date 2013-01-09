# Django settings for heybaldock project.
import os
from ConfigParser import ConfigParser

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
cfg = ConfigParser()
cfg.read(os.path.join(PROJECT_ROOT, 'settings.ini'))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

SECTION_CT_ID = 9

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pt-br'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = 'media'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

UPLOAD_PATH = os.path.join(PROJECT_ROOT, 'media/upload/')
UPLOAD_URLPATH = '/media/upload/'

ALBUM_UPLOAD_PATH = os.path.join(UPLOAD_PATH, 'album/')
ALBUM_UPLOAD_URLPATH = os.path.join(UPLOAD_PATH, 'album/')

DRAFT_UPLOAD_PATH = os.path.join(UPLOAD_PATH, 'draft/')
DRAFT_UPLOAD_PATH_NEW = os.path.join(DRAFT_UPLOAD_PATH, 'new/')
DRAFT_UPLOAD_URLPATH = "%s/draft" % UPLOAD_URLPATH
DRAFT_UPLOAD_URLPATH_NEW = "%s/new" % DRAFT_UPLOAD_URLPATH

TEMP_UPLOAD_PATH = os.path.join(UPLOAD_PATH, 'tmp/')
DISCOGS_TEMP_UPLOAD_PATH = os.path.join(TEMP_UPLOAD_PATH, 'discogs/')
TEMP_UPLOAD_URLPATH = "%s/tmp" % UPLOAD_URLPATH
DISCOGS_TEMP_UPLOAD_URLPATH = "%s/discogs" % TEMP_UPLOAD_URLPATH

# Make this unique, and don't share it with anybody.
SECRET_KEY = '*b!$#a0-$ije!=yd!b3gat*ibxz6%x#w0j!cdnoi#qa1n*s2r^'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'auth.middleware.ComingSoonMiddleware',
    'auth.middleware.UnderMaintenanceMiddleware',
    'music.middleware.MusicMiddleware',
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.webdesign',
    'south',
    'auth',
    'section',
    'photo',
    'video',
    'event',
    'draft',
    'music'

    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'context_processors.main'
)


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

IMAGE_SIZES = {
    'icon': (40, 30),
    'list_quadruplet': (136, 102),
    'list_triplet': (184, 138),
    'list_pair': (285, 213),
    'small': (120, 90),
    'medium': (240, 180),
    'big': (480, 360),
    'huge': (960, 720)
}

SIMPLE_IMAGE_SIZES = {
    'icon': (25, 25),
    'thumb': (90, 90),
    'huge': (1920, 1920)
}

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT =  587
MAIL_USER = "heybaldock@heybaldock.com.br"
MAIL_PASSWORD = cfg.get('gmail', 'specific_password')

MAX_DRAFTS_PER_OBJECT = 20

FACEBOOK_APP_ID = 407367935973504
FACEBOOK_SECRET_KEY = "29613824f0098dbf6ffe85324052a36d"

SITE_DOMAIN = "localhost:8000"

COMMING_SOON = False
UNDER_MAINTENANCE = False

S3_STORAGE = False
S3_BUCKET_NAME = 'heybaldock'

ENABLE_REPERTORY_FEATURES = True

import os
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')  # dev, production, qa, etc
exec('from %s_settings import *' % ENVIRONMENT)
