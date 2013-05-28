# -*- coding: utf-8; Mode: Python -*-

import cPickle
import math
from datetime import datetime
from south.modelsinspector import add_introspection_rules

from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.template import loader, Context
from django.template.loader import get_template_from_string
from django.utils.translation import ugettext as _, ugettext_lazy as l_

from lib.fields import JSONField, PickleField
from contact.models import Notification
from defaults import Tonality, Rating, Tempo, DocumentType, SongMode, \
                     TimeDuration, RepertoryItemStatus
from event.models import Event, Location
from photo.image import ImageHandlerAlbumCover, ImageHandlerInstrument, \
                        ImageHandlerArtist, FileHandlerDocument, \
                        FileHandlerSongAudio
from video.models import VideoBase
from utils import metadata_display


class TablatureCode(object):

    def __init__(self):
        self.lines = []

    def serialize(self):
        return cPickle.dumps(self)

    @staticmethod
    def generate_by_lyrics(lyrics):
        lines = [i for i in lyrics.splitlines() if i]
        tablature = TablatureCode()
        for line in lines:
            tablature.lines.append(TablatureLine(line))
        return tablature

    @staticmethod
    def generate(lines):
        tablature = TablatureCode()
        for line in lines:
            tline = TablatureLine(line['lyrics'])
            for user in line['users']:
                tlinecode = TablatureLineCode(user['user_id'])
                tlinecode.code = user['code']
                tline.users.append(tlinecode)
            tablature.lines.append(tline)
        return tablature


class TablatureLine(object):

    def __init__(self, lyrics):
        self.lyrics = lyrics
        self.users = []

    def serialize(self):
        return cPickle.dumps(self)


class TablatureLineCode(object):

    def __init__(self, user_id):
        self.user_id = user_id
        self.code = ''

    def serialize(self):
        return cPickle.dumps(self)
