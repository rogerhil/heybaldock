#!/bin/bash
rm data.db
rm -rf media/upload/draft
rm -rf media/upload/album
mkdir media/upload/draft
mkdir media/upload/draft/new
mkdir media/upload/album
python manage.py syncdb
DJANGO_SETTINGS_MODULE=settings
PYTHONPATH=.
export DJANGO_SETTINGS_MODULE
export PYTHONPATH
python scripts/populatedb.py
