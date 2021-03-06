# -*- coding: utf-8; Mode: Python -*-

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
from music.tablature import TablatureCode

add_introspection_rules([], ["^lib\.fields\.PickleField"])


class Rehearsal(models.Model):
    band = models.ForeignKey('Band', editable=False, related_name="rehearsals")
    studio = models.ForeignKey(Location)
    date = models.DateTimeField()
    duration = models.IntegerField(default=120)
    paid_by = models.ForeignKey(User, null=True, blank=True)
    cost = models.DecimalField(max_digits=6, decimal_places=2, null=True,
                               blank=True)
    notes = models.TextField(null=True, blank=True)

    def __unicode__(self):
        temp = get_template_from_string("{{ date }}")
        date = temp.render(Context({'date': self.date}))
        kwargs = dict(studio=unicode(self.studio), date=date)
        return u"Ensaio no %(studio)s, %(date)s" % kwargs
        #return _(u"Rehearsal in %(studio)s, %(date)s" % kwargs)

    def duration_display(self):
        return TimeDuration.display(self.duration)

    @property
    def is_upcoming(self):
        return self.date > datetime.now()

    @property
    def url(self):
        return reverse("rehearsal", args=(self.id,))

    @classmethod
    def pre_save(cls, instance, **kwargs):
        if not instance.id:
            band = instance.band
            band.rehearsals_count += 1
            band.save()

    @classmethod
    def pre_delete(cls, instance, **kwargs):
        from music.models import EventRepertory
        band = instance.band
        band.rehearsals_count -= 1
        band.save()
        repertories = EventRepertory.objects.filter(rehearsal=instance)
        # make sure all repertories related will go on too
        repertories.delete()
        ct = ContentType.objects.get_for_model(type(instance))
        notifications = Notification.objects.filter(content_type=ct,
                                                    object_id=instance.id)
        notifications.delete()

pre_save.connect(Rehearsal.pre_save, Rehearsal)
pre_delete.connect(Rehearsal.pre_delete, Rehearsal)


class Band(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=256, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    leader = models.ForeignKey(User)
    members = models.ManyToManyField(User, related_name='bands')
    artists = models.ManyToManyField('Artist', through='BandArtist')
    enable_inactive_members = models.BooleanField(default=False)

    # counts
    rehearsals_count = models.IntegerField(default=0)
    shows_count = models.IntegerField(default=0)

    ACTIVE_BAND_SESSION_KEY = 'active_band'
    ENABLE_INACTIVE_MEMBERS_SESSION_KEY = 'enable_inactive_band_members'


    def __unicode__(self):
        return self.name

    @property
    def active_members(self):
        return self.members.filter(is_active=True)

    @property
    def inactive_members(self):
        return self.members.filter(is_active=False)

    @classmethod
    def get_active_band(cls, request):
        band = request.session.get(cls.ACTIVE_BAND_SESSION_KEY)
        return band

    @classmethod
    def set_active_band(cls, request, band):
        request.session[cls.ACTIVE_BAND_SESSION_KEY] = band

    def reload_band_cache(self, request):
        band = Band.objects.get(id=self.id)
        request.session[self.ACTIVE_BAND_SESSION_KEY] = band

    @classmethod
    def clear_active_band(cls, request):
        request.session[cls.ACTIVE_BAND_SESSION_KEY] = None

    @property
    def occurred_rehearsals(self):
        now = datetime.now()
        return self.rehearsals.filter(date__lte=now)

    def update_counts(self):
        rehearsals = self.rehearsals.all()
        self.rehearsals_count = rehearsals.count()
        stats = {}
        for rehearsal in rehearsals:
            for rep in rehearsal.repertories.all():
                for ritem in rep.all_items.all():
                    if not ritem.item:
                        # inteval
                        continue
                    if ritem.item.id not in stats:
                        stats[ritem.item.id] = ritem.item
                        stats[ritem.item.id].in_rehearsals_count = 0
                        stats[ritem.item.id].in_shows_count = 0
                    stats[ritem.item.id].in_rehearsals_count += 1
        events = self.events.all()
        self.shows_count = events.count()
        self.save()

        for event in events:
            for rep in event.repertories.all():
                for ritem in rep.all_items.all():
                    if not ritem.item:
                        # inteval
                        continue
                    if ritem.item.id not in stats:
                        stats[ritem.item.id] = ritem.item
                        stats[ritem.item.id].in_rehearsals_count = 0
                        stats[ritem.item.id].in_shows_count = 0
                    stats[ritem.item.id].in_shows_count += 1

        for item in stats.values():
            item.save()

        for item in self.repertory.all_items.all():
            if item.id in stats.keys():
                continue
            item.in_shows_count = 0
            item.in_rehearsals_count = 0
            item.save()


class BandArtist(models.Model):
    band = models.ForeignKey(Band)
    artist = models.ForeignKey('Artist', related_name='bands')
    enable_inactive_artist_members = models.BooleanField(default=False)

    class Meta:
        unique_together = ('band', 'artist')


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


class ImageType(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __unicode__(self):
        return self.name

    @classmethod
    def primary(cls):
        return cls.objects.get(name='primary')


class Size(models.Model):
    width = models.IntegerField()
    height = models.IntegerField()

    class Meta:
        unique_together = ('width', 'height')

    def __unicode__(self):
        return "%s X %s" % (self.width, self.height)


class ImageBase(models.Model):
    type = models.ForeignKey(ImageType, null=True, blank=True)
    size = models.ForeignKey(Size, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    filename = models.CharField(max_length=255, null=True, blank=True)

    IMAGE_HANDLER = None

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(ImageBase, self).__init__(*args, **kwargs)
        if not self.IMAGE_HANDLER:
            return
        self.image_handler = self.IMAGE_HANDLER()
        if self.filename:
            self.image_handler.load(self.filename)

    @property
    def thumb_url(self):
        return self.image_handler.url('thumb')

    @property
    def icon_url(self):
        return self.image_handler.url('icon')

    @property
    def huge_url(self):
        return self.image_handler.url('huge')


class Artist(models.Model):
    discogs_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=256, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    metadata = JSONField(null=True, blank=True)
    membership = models.ManyToManyField('Artist', through='ArtistMembership')
    is_group = models.BooleanField(default=False)
    image = models.CharField(max_length=256, null=True, blank=True)
    active_members_count = models.IntegerField(default=0)
    inactive_members_count = models.IntegerField(default=0)
    albums_count = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name_display

    def __init__(self, *args, **kwargs):
        super(Artist, self).__init__(*args, **kwargs)
        self.image_handler = ImageHandlerArtist()
        if self.image:
            self.image_handler.load(self.image)

    @property
    def thumb_url(self):
        if self.image:
            return self.image_handler.url('thumb')
        else:
            return '/media/img/user.thumb.png'

    @property
    def icon_url(self):
        if self.image:
            return self.image_handler.url('icon')
        else:
            return '/media/img/user.icon.png'

    @property
    def huge_url(self):
        if self.image:
            return self.image_handler.url('huge')
        else:
            return '/media/img/user.huge.png'

    @property
    def short_name(self):
        name = self.name_display
        splited = name.split(' ')
        if splited[0].lower() in ['the', 'a']:
            return ' '.join(splited[1:])
        else:
            return name

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

    @property
    def metadata_display(self):
        return metadata_display(self.get_metadata_object() or {})

    @property
    def active_members(self):
        return [i.member for i in
                ArtistMembership.objects.filter(active=True, artist=self)]

    @property
    def inactive_members(self):
        return [i.member for i in
                ArtistMembership.objects.filter(active=False, artist=self)]

    @property
    def albums_by_year(self):
        return self.albums.all().order_by('year')


class ArtistImage(ImageBase):
    artist = models.ForeignKey(Artist, related_name='images')

    IMAGE_HANDLER = ImageHandlerArtist

    def __unicode__(self):
        t = " - %s" % self.type if self.type else ""
        return "Artist Image: %s (%s)%s" % (self.artist, self.size, t)


class ArtistMembership(models.Model):
    artist = models.ForeignKey(Artist, related_name="members")
    member = models.ForeignKey(Artist, related_name="groups")
    date_joined = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)

    @classmethod
    def pre_save(cls, instance, **kwargs):
        if instance.id:
            return
        if instance.active:
            instance.artist.active_members_count += 1
        else:
            instance.artist.inactive_members_count += 1
        instance.artist.save()

    @classmethod
    def pre_delete(cls, instance, **kwargs):
        if instance.active:
            instance.artist.active_members_count -= 1
        else:
            instance.artist.inactive_members_count -= 1
        instance.artist.save()



pre_save.connect(ArtistMembership.pre_save, ArtistMembership)
pre_delete.connect(ArtistMembership.pre_delete, ArtistMembership)


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
        if self.thumb:
            self.image_handler.load(self.thumb)

    @property
    def name_display(self):
        splited = self.name.split(' - ')
        if len(splited) > 1:
            album = ' - '.join(splited[1:])
            return album
        else:
            return self.name

    @property
    def ordered_songs(self):
        songs = list(self.songs.all().order_by('position'))
        zf = lambda x: str(x.position).zfill(3)
        songs.sort(lambda a, b: 1 if zf(a) > zf(b) else -1)
        return songs

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

    @classmethod
    def pre_save(cls, instance, **kwargs):
        if instance.id:
            return
        instance.artist.albums_count += 1
        instance.artist.save()

    @classmethod
    def pre_delete(cls, instance, **kwargs):
        instance.artist.albums_count -= 1
        instance.artist.save()


pre_save.connect(Album.pre_save, Album)
pre_delete.connect(Album.pre_delete, Album)


class AlbumCover(ImageBase):
    album = models.ForeignKey(Album)

    def __unicode__(self):
        t = " - %s" % self.type if self.type else ""
        return "Cover: %s (%s)%s" % (self.album, self.size, t)


class Song(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=255, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    album = models.ForeignKey(Album, related_name='songs')
    lyrics = models.TextField(null=True, blank=True)
    duration = models.IntegerField()
    position = models.CharField(max_length=5, null=True, blank=True)
    composer = models.ManyToManyField(ComposerRole)
    signature = models.CharField(max_length=10, null=True, blank=True)
    tempo = models.IntegerField(choices=Tempo.choices(), null=True, blank=True)
    tonality = models.CharField(max_length=10, null=True, blank=True,
                                choices=Tonality.choices())
    audio = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('name', 'album')

    def __unicode__(self):
        duration = " (%s)" % self.duration_display if self.duration else ""
        return "%s - %s%s" % (self.position, self.name, duration)

    def __init__(self, *args, **kwargs):
        super(Song, self).__init__(*args, **kwargs)
        self.audio_handler = FileHandlerSongAudio()
        if self.audio:
            self.audio_handler.load(self.audio)

    @property
    def audio_url(self):
        if not self.audio:
            return
        if not self.audio_handler:
            self.audio_handler = FileHandlerSongAudio()
        return self.audio_handler.single_url()

    @property
    def lyrics_html_display(self):
        return '<br />'.join(self.lyrics.splitlines())

    @property
    def tempo_display(self):
        if self.tempo and self.tempo >= 10:
            return "%s bpm"% Tempo.display(self.tempo)
        else:
            return "N/A"

    @property
    def tempo_html_display(self):
        d = self.tempo_display
        tempo = self.tempo or 0
        return '<span class="tempo%s">%s</span>' % (tempo, d)

    @property
    def signature_html_display(self):
        return self.signature

    @property
    def signature_tuple(self):
        if not self.signature:
            return (4, 4)
        return tuple(map(int, self.signature.split('/')))

    @property
    def signature_beats(self):
        return self.signature_tuple[0]

    @property
    def signature_value(self):
        return self.signature_tuple[1]

    @property
    def signature_beats_range(self):
        return range(self.signature_tuple[0])

    @property
    def tonality_html_display(self):
        return Tonality.html_display(self.tonality)

    @property
    def duration_display(self):
        if not self.duration:
            return ""
        z = lambda x: str(x).zfill(2)
        return "%s:%s" % (z(self.duration / 60), z(self.duration % 60))

    @property
    def composer_display(self):
        return ', '.join([str(c.composer) for c in self.composer.all()])


class RepertoryBase(models.Model):

    class Meta:
        abstract = True

    def is_free(self):
        return self.user_lock is None

    def is_editable(self, user):
        if isinstance(self, Repertory):
            has_perm = user.has_perm('music.manage_main_repertory')
        elif isinstance(self, EventRepertory):
            has_perm = user.has_perm('music.manage_event_repertories')
        else:
            has_perm = True
        return self.user_lock == user and has_perm

    def is_locked(self, user):
        return self.user_lock is None or self.user_lock != user

    def lock(self, user):
        self.user_lock = user
        self.save()

    def unlock(self):
        self.user_lock = None
        self.save()


class Repertory(RepertoryBase):
    band = models.OneToOneField(Band, null=True, related_name='repertory')
    date = models.DateTimeField(auto_now_add=True, null=True)
    user_lock = models.ForeignKey(User, null=True,
                                  related_name="main_repertories")

    def __unicode__(self):
       return "%s Main Repertory" % self.band

    @property
    def active_items(self):
        statuses = [RepertoryItemStatus.ready, RepertoryItemStatus.working]
        return self.items.filter(status__in=statuses).order_by('order')

    @property
    def trash(self):
        deleted = RepertoryItemStatus.deleted
        return self.all_items.filter(status=deleted)

    @property
    def items(self):
        deleted = RepertoryItemStatus.deleted
        return self.all_items.all().exclude(status=deleted)


class RepertoryItem(models.Model):
    song = models.ForeignKey(Song)
    repertory = models.ForeignKey(Repertory, related_name='all_items')
    date = models.DateField(auto_now_add=True, null=True)
    notes = models.TextField(null=True, blank=True)
    tempo = models.IntegerField(choices=Tempo.choices(), null=True,
                                blank=True)
    mode = models.IntegerField(choices=SongMode.choices(), null=True,
                               blank=True)
    tonality = models.CharField(max_length=10, null=True, blank=True,
                                choices=Tonality.choices())
    status = models.SmallIntegerField(default=RepertoryItemStatus.new,
                                      choices=RepertoryItemStatus.choices())
    # counts
    in_rehearsals_count = models.IntegerField(default=0)
    in_shows_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('song', 'repertory')

    def __unicode__(self):
        return self.song.name

    @property
    def tonality_html_display(self):
        tonality = self.tonality or self.song.tonality
        original = self.tonality_is_original
        return Tonality.html_display(tonality, original=original)

    @property
    def tonality_is_original(self):
        return self.tonality is None or self.tonality == self.song.tonality

    @property
    def mode_html_display(self):
        mode_display = SongMode.display(self.mode)
        if mode_display:
            mode = mode_display[0]
        else:
            mode =  'N/A'
        return '<span class="song_mode mode%s" title="%s">%s</span>' % (
                                                self.mode, mode_display,  mode)

    @property
    def status_html_display(self):
        status_display = RepertoryItemStatus.display(self.status)
        if status_display:
            status = status_display[:9]
        else:
            status =  'N/A'
        return '<span class="song_status status%s" title="%s">%s</span>' % (
                                           self.status, status_display, status)

    @property
    def ratings(self):
        rates = self.users_ratings.all().values_list('rate', flat=True)
        if not len(rates):
            return 0
        average = int(math.ceil(float(sum(rates)) / len(rates)))
        return average

    @property
    def ratings_range(self):
        r = [{'rate': i + 1,
              'active': self.ratings > i} for i in xrange(Rating.length())]
        return r

    def instruments(self):
        instruments = []
        for player in self.players.all():
            if player.player.instrument not in instruments:
                instruments.append(player.player.instrument)
        return instruments

    def users_players(self):
        users = []
        for player in self.players.all():
            if player.player.user not in users:
                users.append(player.player.user)
        return users

    def has_voted(self, user):
        return bool(self.users_ratings.filter(user=user).count())

    def user_votes(self, user):
        votes = self.users_ratings.filter(user=user)
        if votes:
            return votes[0]

    def user_votes_range(self, user):
        vote = self.user_votes(user)
        rate = vote.rate if vote else 0
        r = [{'rate': i + 1,
              'active': rate > i} for i in xrange(Rating.length())]
        return r

    @property
    def frequency_in_rehearsals(self):
        band = self.repertory.band
        if band.rehearsals_count:
            return float(self.in_rehearsals_count) / band.rehearsals_count
        else:
            return 0.0

    @property
    def percentage_in_rehearsals(self):
        return "%.2f%%" % round(self.frequency_in_rehearsals * 100, 2)

    @property
    def frequency_in_shows(self):
        band = self.repertory.band
        if band.shows_count:
            return float(self.in_shows_count) / band.shows_count
        else:
            return 0.0

    @property
    def percentage_in_shows(self):
        return "%.2f%%" % round(self.frequency_in_shows * 100, 2)

    def to_trash(self):
        self.status = RepertoryItemStatus.deleted
        self.save()

    def restore(self):
        self.status = RepertoryItemStatus.restored
        self.save()


class EventRepertory(RepertoryBase):
    event = models.ForeignKey(Event, null=True, blank=True,
                              related_name='repertories')
    rehearsal = models.ForeignKey(Rehearsal, null=True, blank=True,
                                  related_name='repertories')
    user_lock = models.ForeignKey(User, null=True, blank=True,
                                  related_name="event_repertories")
    band = models.ForeignKey(Band, related_name="event_repertories", null=True)

    def __unicode__(self):
        return u"Repertório do %s" % (unicode(self.event) if self.event else
                                     unicode(self.rehearsal))

    @property
    def slug(self):
        if self.event:
            d = self.event.starts_at.strftime("%d-%m-%Y")
            return "repertorio_show_%s" % d
        else:
            d = self.rehearsal.starts_at.strftime("%d-%m-%Y")
            return "repertorio_ensaio_%s" % d

    def import_items_from(self, base):
        for item in base.items.all():
            new_item = item.clone_object(self)
            new_item.save()

    @classmethod
    def get_last_new_repertory(cls):
        event = Event.get_last_new_event()
        if event:
            try:
                return cls.objects.filter(event=event).order_by('-id')[0]
            except IndexError:
                return

    @property
    def items(self):
        deleted = RepertoryItemStatus.deleted
        return self.all_items.all().exclude(item__status=deleted)\
                                   .order_by('order')

    @property
    def url(self):
        return reverse("event_repertory", args=(self.id,))

    @classmethod
    def pre_delete(cls, instance, **kwargs):
        ct = ContentType.objects.get_for_model(type(instance))
        notifications = Notification.objects.filter(content_type=ct,
                                                    object_id=instance.id)
        notifications.delete()


pre_delete.connect(EventRepertory.pre_delete, EventRepertory)


class EventRepertoryItem(models.Model):
    repertory = models.ForeignKey(EventRepertory, related_name='all_items')
    item = models.ForeignKey(RepertoryItem, related_name='events_items',
                             null=True)
    order = models.IntegerField(null=True)
    times_played = models.IntegerField(default=1)

    # used for empty intervals
    empty_duration = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('repertory', 'item')

    @property
    def order_display(self):
        return str(self.order).zfill(2)

    def clone_object(self, repertory):
        item = EventRepertoryItem(item=self.item, repertory=repertory,
                                  order=self.order,
                                  empty_duration=self.empty_duration)
        return item

    def empty_duration_display(self):
        if not self.empty_duration:
            return ""
        return TimeDuration.custom_display(self.empty_duration)

    @classmethod
    def pre_save(cls, instance, **kwargs):
        try:
            repertory = instance.repertory
        except:
            return
        if not instance.id and (repertory.event or repertory.rehearsal):
            if not instance.item:
                return
            if repertory.event:
                instance.item.in_shows_count += 1
            elif repertory.rehearsal:
                instance.item.in_rehearsals_count += 1
            instance.item.save()

    @classmethod
    def pre_delete(cls, instance, **kwargs):
        try:
            repertory = instance.repertory
        except:
            return
        if repertory.event or repertory.rehearsal:
            if not instance.item:
                return
            if repertory.event:
                instance.item.in_shows_count -= 1
            elif repertory.rehearsal:
                instance.item.in_rehearsals_count -= 1
            instance.item.save()


pre_delete.connect(EventRepertoryItem.pre_delete, EventRepertoryItem)
pre_save.connect(EventRepertoryItem.pre_save, EventRepertoryItem)


class Instrument(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Instrument, self).__init__(*args, **kwargs)
        self.image_handler = ImageHandlerInstrument()
        if self.image:
            self.image_handler.load(self.image)

    @property
    def thumb_url(self):
        return self.image_handler.url('thumb')

    @property
    def icon_url(self):
        return self.image_handler.url('icon')

    @property
    def huge_url(self):
        return self.image_handler.url('huge')

    @property
    def is_vocal(self):
        return self.name.lower() == 'vocal'


class Player(models.Model):
    instrument = models.ForeignKey(Instrument, related_name="users")
    user = models.ForeignKey(User, related_name="instruments")
    image = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('instrument', 'user')

    def __unicode__(self):
        kwargs = dict(
            user=self.user.nick,
            instrument=self.instrument
        )
        if self.instrument.is_vocal:
            return "%(user)s sings" % kwargs
        else:
            return "%(user)s plays %(instrument)s" % kwargs


class InstrumentTagType(models.Model):
    name = models.CharField(max_length=64)
    friendly_name = models.CharField(max_length=15)
    level = models.SmallIntegerField()
    instrument = models.ForeignKey(Instrument, related_name='tag_types')

    def __unicode__(self):
        return "%s %s" % (self.name, self.instrument)

    class Meta:
        unique_together = (('name', 'instrument'), ('level', 'instrument'))

    @property
    def name_display(self):
        return self.friendly_name or self.name

    @property
    def html_display(self):
        template = loader.get_template('music/tag_type.html')
        return template.render(Context(dict(tag_type=self)))


class PlayerEventRepertory(models.Model):
    player = models.ForeignKey(Player, related_name="event_repertories",
                               null=True, blank=True)
    item = models.ForeignKey(EventRepertoryItem)

    class Meta:
        unique_together = ('player', 'item')


class PlayerRepertoryItem(models.Model):
    player = models.ForeignKey(Player, related_name="repertory_items",
                               null=True, blank=True)
    item = models.ForeignKey(RepertoryItem, related_name="players")
    as_member = models.ForeignKey(Artist, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    tag_types = models.ManyToManyField(InstrumentTagType, blank=True)
    is_lead = models.BooleanField(default=False)

    class Meta:
        unique_together = ('player', 'item')

    def __unicode__(self):
        kwargs = dict(
            user=self.player.user.nick,
            instrument=self.player.instrument,
            song=self.item,
            as_member=self.as_member
        )
        if self.as_member:
            if self.player.instrument.is_vocal:
                return _('%(user)s sings "%(song)s" as %(as_member)s' % kwargs)
            else:
                return _('%(user)s plays %(instrument)s in "%(song)s" as '
                         '%(as_member)s' % kwargs)
        else:
            if self.player.instrument.is_vocal:
                return _('%(user)s sings "%(song)s"' % kwargs)
            else:
                return _('%(user)s plays %(instrument)s in "%(song)s"'% kwargs)

    @property
    def ratings(self):
        rates = self.users_ratings.all().values_list('rate', flat=True)
        if not len(rates):
            return 0
        average = int(math.ceil(float(sum(rates)) / len(rates)))
        return average

    @property
    def ratings_range(self):
        r = [{'rate': i + 1,
              'active': self.ratings > i} for i in xrange(Rating.length())]
        return r

    def has_voted(self, user):
        return bool(self.users_ratings.filter(user=user).count())

    @property
    def has_tag_types(self):
        return bool(self.tag_types.all().count())


class Tablature(models.Model):
    item = models.ForeignKey(RepertoryItem, related_name="tablatures")
    instrument = models.ForeignKey(Instrument)
    code = PickleField()

    def __unicode__(self):
        return _("Tablature for %s" % self.instrument)

    def generate_tablature_by_lyrics(self):
        lyrics = self.item.song.lyrics or ''
        tablature = TablatureCode.generate_by_lyrics(lyrics)
        self.code = tablature.serialize()

    def generate_tablature_by_data(self, data):
        tablature = TablatureCode.generate(data)
        self.code = tablature.serialize()

    def render(self):
        template = loader.get_template('music/tablature.html')
        c = dict(tablature=self)
        return template.render(Context(c))


class MusicScoreSegment(models.Model):
    name = models.CharField(max_length=64)
    player_repertory_item = models.ForeignKey(PlayerRepertoryItem)
    score = JSONField()
    notes = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('name', 'player_repertory_item')

    def __unicode__(self):
        return "%s - %s" % (self.name, self.player_repertory_item)


class MusicAudioSegment(models.Model):
    name = models.CharField(max_length=64)
    player_repertory_item = models.ForeignKey(PlayerRepertoryItem)
    audio = models.CharField(max_length=255)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('name', 'player_repertory_item')

    def __unicode__(self):
        return "%s - %s" % (self.name, self.player_repertory_item)


class DocumentPlayerRepertoryItem(models.Model):
    name = models.CharField(max_length=64)
    player_repertory_item = models.ForeignKey(PlayerRepertoryItem,
                                              related_name='documents')
    document = models.CharField(max_length=255)
    notes = models.TextField(null=True, blank=True)
    type = models.SmallIntegerField(default=DocumentType.other)

    class Meta:
        unique_together = ('name', 'player_repertory_item')

    def __unicode__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(DocumentPlayerRepertoryItem, self).__init__(*args, **kwargs)
        self.file_handler = FileHandlerDocument()
        if self.document:
            self.file_handler.load(self.document)

    @property
    def is_image(self):
        return self.type == DocumentType.image

    @property
    def url(self):
        return self.file_handler.single_url()

    @property
    def icon_url(self):
        if self.is_image:
            return self.file_handler.url('icon')
        else:
            return "/media/img/document_icon_16.png"

    @classmethod
    def pre_delete(cls, instance, **kwargs):
        instance.file_handler.delete()


pre_delete.connect(DocumentPlayerRepertoryItem.pre_delete,
                   DocumentPlayerRepertoryItem)


class DocumentRepertoryItem(models.Model):
    name = models.CharField(max_length=64)
    item = models.ForeignKey(RepertoryItem)
    document = models.CharField(max_length=255)

    class Meta:
        unique_together = ('name', 'item')

    def __unicode__(self):
        return self.name


class VideoPlayerRepertoryItem(VideoBase):
    name = models.CharField(max_length=255, null=True, blank=True)
    player_repertory_item = models.ForeignKey(PlayerRepertoryItem)

    def __unicode__(self):
        title = self.name or self.url
        return "%s - %s" % (title, self.player_repertory_item)


class VideoRepertoryItem(VideoBase):
    name = models.CharField(max_length=255, null=True, blank=True)
    player_repertory_item = models.ForeignKey(PlayerRepertoryItem)

    def __unicode__(self):
        title = self.name or self.url
        return "%s - %s" % (title, self.player_repertory_item)


class UserRepertoryItemRating(models.Model, Rating):
    user = models.ForeignKey(User, related_name="repertory_items_ratings")
    item = models.ForeignKey(RepertoryItem, related_name="users_ratings")
    rate = models.SmallIntegerField(choices=Rating.choices())

    class Meta:
        unique_together = ('user', 'item')

    @property
    def ratings_range(self):
        r = [{'rate': i + 1,
              'active': self.rate > i} for i in xrange(Rating.length())]
        return r


class PlayerRepertoryItemRating(models.Model, Rating):
    user = models.ForeignKey(User,
                             related_name="player_repertory_items_ratings")
    player_repertory_item = models.ForeignKey(PlayerRepertoryItem,
                                              related_name="users_ratings")
    rate = models.SmallIntegerField(choices=Rating.choices())

    class Meta:
        unique_together = ('user', 'player_repertory_item')


class MusicHistoryChanges(models.Model):
    user = models.ForeignKey(User, related_name="music_history")
    summary = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField(null=True)
    content_date = models.DateTimeField(auto_now=True)
    content = PickleField(default='')
    object = generic.GenericForeignKey()
    created = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s by %s in %s" % (self.summary, self.user.first_name,
                                  self.content_date.strftime("%d/%m/%Y %H:%M"))
