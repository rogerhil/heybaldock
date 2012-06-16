DEBUG = False

COMMING_SOON = True
UNDER_MAINTENANCE = False

import dj_database_url
DATABASES = {'default': dj_database_url.config(default='postgres://localhost')}