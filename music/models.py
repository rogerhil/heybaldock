# -*- coding: utf-8; Mode: Python -*-

from django.db import models
from django.contrib.auth.models import User

from lib.fields import JSONField
from event.models import Event


class Composer(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=256)
    about = models.TextField(null=True, blank=True)


class Artist(models.Model):
    discogsid = models.IntegerField(unique=True)
    name = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=256, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    metadata = JSONField(null=True, blank=True)


class Album(models.Model):
    discogsid = models.IntegerField(unique=True)
    catno = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=255, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    artist = models.ForeignKey(Artist)
    thumb = models.CharField(max_length=255)
    uri = models.CharField(max_length=255)
    year = models.IntegerField()
    metadata = JSONField(null=True, blank=True)


class SongStyle(models.Model):
    VALUE_CHOICES = [
        (1, 'Muito calma'),
        (2, 'Calma'),
        (3, 'Normal'),
        (4, 'Alegre'),
        (5, 'Agitada')
    ]
    name = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    value = models.IntegerField(choices=VALUE_CHOICES)


class Song(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=255, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    album = models.ForeignKey(Album)
    lyrics = models.TextField(null=True, blank=True)
    duration = models.IntegerField()
    position = models.CharField(max_length=5, null=True, blank=True)
    composer = models.ManyToManyField(Composer)
    style = models.ForeignKey(SongStyle)

    class Meta:
        unique_together = ('name', 'album')


class Repertory(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    event = models.ForeignKey(Event, null=True, blank=True)

    def __unicode__(self):
       return self.name

    class Meta:
        unique_together = ('name', 'event')


class RepertoryGroup(models.Model):
    name = models.CharField(max_length=128)
    repertory = models.ForeignKey(Repertory, related_name='groups')
    order = models.IntegerField()

    class Meta:
        unique_together = ('repertory', 'order')


class RepertoryGroupItem(models.Model):
    song = models.ForeignKey(Song)
    group = models.ForeignKey(RepertoryGroup, related_name='songs')
    number = models.IntegerField()

    class Meta:
        unique_together = (('song', 'group'), ('group', 'number'))


class Instrument(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    is_lead = models.BooleanField(default=False)


class UserInstrumentSong(models.Model):
    instrument = models.ForeignKey(Instrument)
    song = models.ForeignKey(Song)
    user = models.ForeignKey(User)

    class Meta:
        unique_together = ('instrument', 'song', 'user')


class Rating(object):
    RATING_CHOICES = [(i, i) for i in range(1, 5)]


class UserSongRating(models.Model, Rating):
    user = models.ForeignKey(User)
    song = models.ForeignKey(Song)
    rate = models.SmallIntegerField(choices=Rating.RATING_CHOICES)

    class Meta:
        unique_together = ('song', 'user', 'rate')


class UserInstrumentSongRating(models.Model, Rating):
    user_instrument_song = models.ForeignKey(UserInstrumentSong)
    rate = models.SmallIntegerField(choices=Rating.RATING_CHOICES)

    class Meta:
        unique_together = ('user_instrument_song', 'rate')

