# -*- coding: utf-8; Mode: Python -*-

from django.db import models
from django.contrib.auth.models import User

from lib.fields import JSONField
from event.models import Event
from photo.image import ImageHandlerAlbumCover


class Composer(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=256, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    discogs_resource_url = models.CharField(max_length=256, null=True,
                                            blank=True)
    metadata = JSONField(null=True, blank=True)

    def __unicode__(self):
        return self.name


class ComposerRole(models.Model):
    role = models.CharField(max_length=128)
    composer = models.ForeignKey(Composer)

    class Meta:
        unique_together = ('role', 'composer')

    def __unicode__(self):
        return "%s %s" % (self.role, self.composer)


class Artist(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=256, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    metadata = JSONField(null=True, blank=True)

    def __unicode__(self):
        return self.name_display

    @property
    def name_display(self):
        splited = self.name.split(', ')
        if len(splited) > 1:
            end = splited[-1].strip()
            if end.lower() in ['the', 'a']:
                n = ', '.join(splited[:-1])
                return "%s %s" % (end, n)
        else:
            return self.name


class AlbumStyle(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __unicode__(self):
        return self.name


class AlbumGenre(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __unicode__(self):
        return self.name


class Album(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=255, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    artist = models.ForeignKey(Artist, related_name='albums')
    thumb = models.CharField(max_length=255)
    year = models.IntegerField()
    metadata = JSONField(null=True, blank=True)
    style = models.ManyToManyField(AlbumStyle)
    genre = models.ManyToManyField(AlbumGenre)


    class Meta:
        unique_together = ('name', 'artist')

    def __unicode__(self):
        return self.name_display

    def __init__(self, *args, **kwargs):
        super(Album, self).__init__(*args, **kwargs)
        self.image_handler = ImageHandlerAlbumCover()
        self.image_handler.load(self.thumb)

    @property
    def name_display(self):
        splited = self.name.split(' - ')
        if len(splited) > 1:
            artist = splited[0]
            album = ' - '.join(splited[1:])
            return album
        else:
            return self.name

    @property
    def thumb_url(self):
        return self.image_handler.url('thumb')

    @property
    def icon_url(self):
        return self.image_handler.url('icon')

    @property
    def genre_display(self):
        return ', '.join(map(str, self.genre.all()))

    @property
    def style_display(self):
        return ', '.join(map(str, self.style.all()))


class AlbumCoverType(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __unicode__(self):
        return self.name


class Size(models.Model):
    width = models.IntegerField()
    height = models.IntegerField()

    class Meta:
        unique_together = ('width', 'height')

    def __unicode__(self):
        return "%s X %s" % (self.width, self.height)


class AlbumCover(models.Model):
    album = models.ForeignKey(Album)
    type = models.ForeignKey(AlbumCoverType, null=True, blank=True)
    size = models.ForeignKey(Size, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    filename = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        t = " - %s" % self.type if self.type else ""
        return "Cover: %s (%s)%s" % (self.album, self.size, t)


class Tempo:

    adagio = 1
    andante = 2
    moderato = 3
    allegro = 4
    presto = 5

    @classmethod
    def choices(cls):
        choices = [(getattr(cls, k), k.title()) for k in dir(cls)
                                                if not k.startswith('__')]
        return choices

    @classmethod
    def display(cls, t):
        return dict(cls.choices()).get(t)


class Song(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=255, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    album = models.ForeignKey(Album, related_name='songs')
    lyrics = models.TextField(null=True, blank=True)
    duration = models.IntegerField()
    position = models.CharField(max_length=5, null=True, blank=True)
    composer = models.ManyToManyField(ComposerRole)
    tempo = models.IntegerField(choices=Tempo.choices(),
                                default=Tempo.moderato)

    class Meta:
        unique_together = ('name', 'album')

    def __unicode__(self):
        duration = " (%s)" % self.duration_display if self.duration else ""
        return "%s - %s%s" % (self.position, self.name, duration)

    @property
    def tempo_display(self):
        return Tempo.display(self.tempo)

    @property
    def duration_display(self):
        if not self.duration:
            return ""
        z = lambda x: str(x).zfill(2)
        return "%s:%s" % (z(self.duration / 60), z(self.duration % 60))

    @property
    def composer_display(self):
        return ', '.join([str(c.composer) for c in self.composer.all()])


class Repertory(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    event = models.ForeignKey(Event, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True)

    MAIN_NAME = 'Main'

    def __unicode__(self):
       return self.name

    class Meta:
        unique_together = ('name', 'event')

    @classmethod
    def get_main_repertory(cls):
        return cls.objects.get(name=cls.MAIN_NAME)

    @property
    def is_main(self):
        return self.name == self.MAIN_NAME


class RepertoryGroup(models.Model):
    name = models.CharField(max_length=128)
    repertory = models.ForeignKey(Repertory, related_name='groups')
    order = models.IntegerField()

    class Meta:
        unique_together = ('repertory', 'order')

    @property
    def is_main(self):
        return self.repertory.name == self.repertory.MAIN_NAME

    @property
    def ordered_items(self):
        return self.items.all().order_by('number')


class RepertoryGroupItem(models.Model):
    song = models.ForeignKey(Song)
    group = models.ForeignKey(RepertoryGroup, related_name='items')
    number = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        unique_together = (('song', 'group'), ('group', 'number'))

    def __unicode__(self):
        return "%s - %s" % (self.number, self.song)

    @property
    def number_display(self):
        return str(self.number).zfill(2)


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

