#!/usr/bin/env python

from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.auth.management import create_superuser
from django.db.models import signals

# Prevent interactive question about wanting a superuser created.  (This code
# has to go in this otherwise empty "models" module so that it gets processed by
# the "syncdb" command during database creation.)
signals.post_syncdb.disconnect(create_superuser, sender=auth_models,
                dispatch_uid='django.contrib.auth.management.create_superuser')


# Create our own test user automatically.

def create_testuser(app, created_models, verbosity, **kwargs):
    if not settings.DEBUG:
        return
    try:
        auth_models.User.objects.get(username='rogerhil')
    except auth_models.User.DoesNotExist:
        username = 'rogerhil'
        email = 'rogerhil@gmail.com'
        password = 'alabama'
        print '*' * 80
        print 'Creating test user -- login: %s, password: %s' % (username,
                                                                 password)
        print '*' * 80
        assert auth_models.User.objects.create_superuser(username, email,
                                                         password)
    else:
        print 'rogerhil user already exists.'

signals.post_syncdb.connect(create_testuser, sender=auth_models,
                            dispatch_uid='common.models.create_testuser')