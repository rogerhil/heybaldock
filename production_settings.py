DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        #'NAME': 'data.db',                      # Or path to database file if using sqlite3.
        'USER': 'rogerhil_heybaldock',                      # Not used with sqlite3.
        'NAME': 'rogerhil_heybaldock',
        'PASSWORD': 'supertogether',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

DEBUG = True

COMMING_SOON = True
UNDER_MAINTENANCE = False

S3_STORAGE = False
S3_BUCKET_NAME = 'heybaldock'

SITE_DOMAIN = "heybaldock.com.br"

#import dj_database_url
#DATABASES = {'default': dj_database_url.config(default='postgres://localhost')}