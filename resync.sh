#!/bin/bash
rm data.db
rm -rf media/upload/draft
rm -rf media/upload/album
mkdir media/upload/draft
mkdir media/upload/draft/new
mkdir media/upload/album
dropdb -U postgres heybaldock
createdb -U postgres heybaldock
python manage.py syncdb
python manage.py migrate section
python manage.py migrate draft
python manage.py migrate event
python manage.py migrate video
python manage.py migrate photo
python manage.py migrate event
DJANGO_SETTINGS_MODULE=settings
PYTHONPATH=.
export DJANGO_SETTINGS_MODULE
export PYTHONPATH
python scripts/populatedb.py
