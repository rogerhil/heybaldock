# -*- coding: utf-8; Mode: Python -*-

import math
from south.modelsinspector import add_introspection_rules

from django.db import models
from django.db.models.signals import pre_delete, pre_save, post_save,\
                                     post_delete
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template import loader, Context

from lib.fields import JSONField, PickleField
from defaults import Tonality, Rating, Tempo, DocumentType, SongMode
from event.models import Event
from photo.image import ImageHandlerAlbumCover, ImageHandlerInstrument, \
                        ImageHandlerArtist, FileHandlerDocument, \
                        FileHandlerSongAudio
from video.models import VideoBase
from utils import metadata_display

add_introspection_rules([], ["^lib\.fields\.PickleField"])


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
        return self.songs.all().order_by('position')

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
        return self.audio_handler.single_url()

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

    @classmethod
    def get_last_new_repertory(cls):
        event = Event.get_last_new_event()
        if event:
            try:
                return cls.objects.filter(event=event).order_by('-id')[0]
            except IndexError:
                return


class RepertoryGroup(models.Model):
    name = models.CharField(max_length=128)
    repertory = models.ForeignKey(Repertory, related_name='groups')
    order = models.IntegerField()

    class Meta:
        unique_together = ('repertory', 'order')

    @property
    def is_main(self):
        return self.repertory.name == self.repertory.MAIN_NAME

    @classmethod
    def get_main_group(cls):
        main = Repertory.get_main_repertory()
        return main.groups.all()[0]

    @property
    def ordered_items(self):
        return self.items.all().order_by('number')


class RepertoryGroupItem(models.Model):
    song = models.ForeignKey(Song)
    group = models.ForeignKey(RepertoryGroup, related_name='items')
    number = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True, null=True)
    tempo = models.IntegerField(choices=Tempo.choices(), null=True,
                                blank=True)
    mode = models.IntegerField(choices=SongMode.choices(), null=True,
                               blank=True)
    tonality = models.CharField(max_length=10, null=True, blank=True,
                                choices=Tonality.choices())

    class Meta:
        unique_together = (('song', 'group'), ('group', 'number'))

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
    def number_display(self):
        return str(self.number).zfill(2)

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

    def get_correspond_main_item(self):
        main_group = RepertoryGroup.get_main_group()
        return main_group.items.get(song=self.song)

    def get_last_new_correspond_items(self):
        last_new_repertory = Repertory.get_last_new_repertory()
        if not last_new_repertory:
            return []
        items = []
        for group in last_new_repertory.groups.all():
            try:
                item = group.items.get(song=self.song)
            except RepertoryGroupItem.DoesNotExist:
                continue
            items.append(item)
        return items

    @classmethod
    def post_save(cls, instance, created, **kwargs):
        """ All new RepertoryGroupItems will inherit all properties from
        main repertory.
        """
        if not created or instance.group.is_main:
            return
        main_item = instance.get_correspond_main_item()
        for player_rep_item in main_item.players.all():
            new_player_rep_item, rels = player_rep_item.clone_object()
            new_player_rep_item.repertory_item = instance
            new_player_rep_item.save()
            for attr, values in rels.items():
                many = getattr(new_player_rep_item, attr)
                many.clear()
                for value in values:
                    many.add(value)
            new_player_rep_item.save()


post_save.connect(RepertoryGroupItem.post_save, RepertoryGroupItem)


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

    @property
    def verb(self):
        return "sings" if self.is_vocal else "plays"

    @property
    def verb_past(self):
        return "sang" if self.is_vocal else "played"

    @property
    def verb_past_participle(self):
        return "sung" if self.is_vocal else "played"


class Player(models.Model):
    instrument = models.ForeignKey(Instrument, related_name="users")
    user = models.ForeignKey(User, related_name="instruments")
    image = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('instrument', 'user')

    def __unicode__(self):
        if self.instrument.is_vocal:
            return "%s %s" % (self.user, self.instrument.verb)
        else:
            return "%s %s %s" % (self.user.first_name, self.instrument.verb,
                                 self.instrument)


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


class PlayerRepertoryItem(models.Model):
    player = models.ForeignKey(Player, related_name="repertory_items",
                               null=True, blank=True)
    repertory_item = models.ForeignKey(RepertoryGroupItem,
                                       related_name="players")
    as_member = models.ForeignKey(Artist, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    tag_types = models.ManyToManyField(InstrumentTagType, blank=True)
    is_lead = models.BooleanField(default=False)

    class Meta:
        unique_together = ('player', 'repertory_item')

    def __unicode__(self):
        return "%s %s as %s" % (self.player, self.repertory_item,
                                self.as_member)

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

    def clone_object(self, through=None):
        if through is None:
            through = PlayerRepertoryItem()
        player_repertory_item = through
        player_repertory_item.player = self.player
        player_repertory_item.as_member = self.as_member
        player_repertory_item.notes = self.notes
        player_repertory_item.is_lead = self.is_lead
        tag_types = self.tag_types.all() if self.id else []
        return player_repertory_item, dict(tag_types=tag_types)

    def get_correspond_main_player(self):
        main_item = self.repertory_item.get_correspond_main_item()
        try:
            main_player_ri = main_item.players.get(player=self.player)
        except PlayerRepertoryItem.DoesNotExist:
            return
        return main_player_ri

    def get_last_new_correspond_players(self):
        items = self.repertory_item.get_last_new_correspond_items()
        players = []
        for item in items:
            try:
                player = item.players.get(player=self.player)
            except PlayerRepertoryItem.DoesNotExist:
                continue
            players.append(player)
        return players

    @classmethod
    def pre_save(cls, instance, **kwargs):
        """ If the current PlayerRepertoryItem belongs to a repertory of an
        Event (not the main one), so replicate all information to the main
        repertory.
        """
        return
        try:
            instance
            instance.repertory_item
            instance.repertory_item.group
            instance.repertory_item.group.is_main
        except:
            return
        if instance.id:
            current = PlayerRepertoryItem.objects.get(id=instance.id)
        else:
            current = instance
        if instance.repertory_item.group.is_main:

            players = current.get_last_new_correspond_players()
            for player in players:
                pl, rels = instance.clone_object(player)
                pl.save()
                for attr, values in rels.items():
                    many = getattr(pl, attr)
                    many.clear()
                    for value in values:
                        many.add(value)
            if not instance.id:
                items = current.repertory_item.get_last_new_correspond_items()
                for item in items:
                    pls = [i.player for i in item.players.all()]
                    if instance.player in pls:
                        continue
                    pl, rels = instance.clone_object()
                    pl.repertory_item = item
                    pl.save()
                    for attr, values in rels.items():
                        many = getattr(pl, attr)
                        many.clear()
                        for value in values:
                            many.add(value)
                    item.players.add(pl)
            return
        main_player_ri = current.get_correspond_main_player()
        if not main_player_ri:
            return
        main_player_ri, rels = instance.clone_object(main_player_ri)
        main_player_ri.save()
        for attr, values in rels.items():
            many = getattr(main_player_ri, attr)
            for value in values:
                many.add(value)
        main_player_ri.save()

    @classmethod
    def post_delete(cls, instance, **kwargs):
        """ If the current PlayerRepertoryItem belongs to a repertory of an
        Event (not the main one), so replicate all information to the main
        repertory.
        """
        return
        try:
            instance.repertory_item
        except RepertoryGroupItem.DoesNotExist:
            return
        if instance.repertory_item.group.is_main:
            return
        main_player_rep_item = instance.get_correspond_main_player()
        main_player_rep_item.delete()


pre_save.connect(PlayerRepertoryItem.pre_save, PlayerRepertoryItem)
post_delete.connect(PlayerRepertoryItem.post_delete, PlayerRepertoryItem)


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
    repertory_item = models.ForeignKey(RepertoryGroupItem)
    document = models.CharField(max_length=255)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('name', 'repertory_item')

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
    repertory_item = models.ForeignKey(PlayerRepertoryItem)

    def __unicode__(self):
        title = self.name or self.url
        return "%s - %s" % (title, self.repertory_item)


class UserRepertoryItemRating(models.Model, Rating):
    user = models.ForeignKey(User, related_name="repertory_items_ratings")
    repertory_item = models.ForeignKey(RepertoryGroupItem,
                                       related_name="users_ratings")
    rate = models.SmallIntegerField(choices=Rating.choices())

    class Meta:
        unique_together = ('user', 'repertory_item')


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
    object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return "%s by %s in %s" % (self.summary, self.user.first_name,
                                   self.content_date.strftime("%d/%m/%Y %H:%M"))