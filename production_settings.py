DEBUG = True

COMMING_SOON = True
UNDER_MAINTENANCE = False

S3_BUCKET_NAME = 'heybaldock'

import dj_database_url
DATABASES = {'default': dj_database_url.config(default='postgres://localhost')}