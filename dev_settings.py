DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        #'NAME': 'data.db',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
        'NAME': 'heybaldock',
        'PASSWORD': 'postgres',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

S3_STORAGE = False
S3_BUCKET_NAME = 'heybaldock-dev'

COMMING_SOON = False
UNDER_MAINTENANCE = False

DEBUG = True

ENABLE_REPERTORY_FEATURES = True