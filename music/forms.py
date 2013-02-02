# -*- coding: utf-8; Mode: Python -*-

import time
from datetime import datetime

from django import forms
from django.utils import simplejson

from models import EventRepertory, Album, Artist, Song, AlbumStyle, \
                   AlbumGenre, Composer, ComposerRole, Instrument, Player, \
                   PlayerRepertoryItem, ArtistImage, Size, ImageType, \
                   ArtistMembership, InstrumentTagType, Band, Rehearsal, \
                   DocumentPlayerRepertoryItem
from event.models import Location, LocationType
from photo.image import ImageHandlerAlbumCoverTemp, ImageHandlerInstrument, \
                        ImageHandlerArtist, FileHandlerDocument
from utils import generate_filename
from defaults import DocumentType, TimeDuration
from discogs import Discogs

COUNTRIES = [
    'All of: US, UK, Europe',
    'All countries (very slow search)',
    'US',
    'UK',
    'UK & Europe',
    'Europe',
    'Brazil',
    'Canada',
    'Italy',
    'France',
    'Argentina',
    'Venezuela',
    'Australia',
    'Germany',
    'Spain',
    'Netherlands',
    'Denmark',
    'Poland',
    'Sweden',
    'Switzerland',
    'New Zealand',
    'Russia',
    'Mexico',
    'Yugoslavia',
    'Colombia',
    'Greece',
    'Japan',
    'Taiwan'
]

class AlbumInfoForm(forms.Form):
    """Album Info form search
    """

    COUNTRY_CHOICES = [(i, i) for i in COUNTRIES]

    YEAR_CHOICES = [(i, i) for i in range(1955, datetime.now().year)]

    artist = forms.CharField(max_length=128, required=True)
    album = forms.CharField(max_length=128, required=True)
    country = forms.ChoiceField(choices=COUNTRY_CHOICES)
    from_year = forms.ChoiceField(choices=YEAR_CHOICES, initial=1960)
    #composers_info = forms.BooleanField(initial=True)
    #track_list_enumeration = forms.BooleanField(initial=True)


class SongForm(forms.Form):
    name = forms.CharField(max_length=128)
    description = forms.CharField(max_length=256, required=False)
    about = forms.CharField(required=False)
    lyrics = forms.CharField(required=False)
    duration = forms.CharField()
    position = forms.CharField(max_length=5)
    composer = forms.CharField(required=False)

    def clean_duration(self):
        data = self.cleaned_data
        t = time.strptime(data['duration'].strip(), "%M:%S")
        value = t.tm_min * 60 + t.tm_sec
        return value

    def save(self, album):
        data = self.cleaned_data
        name = data['name']
        new = True
        try:
            song = Song.objects.get(name=name, album=album)
            new = False
        except Song.DoesNotExist:
            d = data.copy()
            del d['composer']
            song = Song.objects.create(album=album, **d)
        composers = []
        if data['composer']:
            for d in simplejson.loads(data['composer']):
                composer, created = Composer.objects.get_or_create(
                    name=d.get('anv') or d['name']
                )
                if created:
                    if d.get('resource_url'):
                        composer.discogs_resource_url = d['resource_url']
                        composer.save()
                composer_role, created = ComposerRole.objects.get_or_create(
                    role=d['role'],
                    composer=composer)
                composers.append(composer_role)
            song.composer = composers
        song.save()
        return song


class BandForm(forms.ModelForm):

    class Meta:
        model = Band
        exclude = ('rehearsals_count', 'shows_count')


class RehearsalForm(forms.ModelForm):

    duration = forms.ChoiceField(initial=120)

    class Meta:
        model = Rehearsal

    def __init__(self, band, *args, **kwargs):
        super(RehearsalForm, self).__init__(*args, **kwargs)
        locations = Location.objects.filter(location_type=LocationType.studio)
        self.fields['studio'].choices = [(i.id, str(i)) for i in locations]
        self.fields['duration'].choices = TimeDuration.choices()
        self.instance.band = band


class EventRepertoryForm(forms.ModelForm):

    class Meta:
        model = EventRepertory
        exclude = ('user_lock')


class InstrumentForm(forms.ModelForm):

    image = forms.ImageField(required=True)

    class Meta:
        model = Instrument

    def save(self):
        data = self.cleaned_data
        filename = generate_filename(data['image'].name)
        handler = ImageHandlerInstrument()
        handler.load(filename, data['image'])
        handler.save_thumbnails('PNG')
        instrument = Instrument.objects.create(
            name=data['name'],
            description=data.get('description'),
            image=filename
        )
        self.instance = instrument


class InstrumentTagTypeForm(forms.ModelForm):

    level = forms.ChoiceField()

    class Meta:
        model = InstrumentTagType

    def __init__(self, *args, **kwargs):
        super(InstrumentTagTypeForm, self).__init__(*args, **kwargs)
        self.fields['level'].choices = [(i, i) for i in range(1, 9)]


class PlayerForm(forms.ModelForm):

    class Meta:
        model = Player


class PlayerRepertoryItemForm(forms.ModelForm):

    class Meta:
        model = PlayerRepertoryItem


class DocumentPlayerRepertoryItemForm(forms.Form):
    file = forms.FileField(required=True)
    player_repertory_item = forms.IntegerField(required=True)

    def save(self):
        data = self.cleaned_data
        filename = generate_filename(data['file'].name)
        handler = FileHandlerDocument()
        handler.load(filename, data['file'])
        document = DocumentPlayerRepertoryItem(name=data['file'].name,
                        document=filename,
                        player_repertory_item_id=data['player_repertory_item'])
        if handler.is_image():
            handler.save_thumbnails('PNG')
            document.type = DocumentType.image
        document.save()
        return document


class ArtistForm(forms.Form):
    resource_url = forms.CharField(max_length=128)
    description = forms.CharField(max_length=256, required=False)
    about = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(ArtistForm, self).__init__(*args, **kwargs)
        self.is_new = False

    def _remove_metadata_keys(self, metadata):
        if metadata.has_key('members'):
            del metadata['members']
        if metadata.has_key('name'):
            del metadata['name']
        if metadata.has_key('data_quality'):
            del metadata['data_quality']
        if metadata.has_key('profile'):
            del metadata['profile']
        return metadata

    def _save_images(self, artist, metadata):
        for i in metadata.get('images', []):
            itype = ImageType.objects.get_or_create(name=i['type'])[0]
            size = Size.objects.get_or_create(width=i['width'],
                                              height=i['height'])[0]
            handler = ImageHandlerArtist()
            handler.load_by_url(i['uri'])
            handler.save_thumbnails('PNG')
            filename = handler.storage.filename
            ArtistImage.objects.create(type=itype, size=size,
                                       filename=filename, artist=artist)
            if i['type'] == 'primary':
                artist.image = filename
                artist.save()

        if metadata.has_key('images'):
            del metadata['images']
        return metadata

    def _save_members(self, artist, metadata):
        for d in metadata.get('members', []):
            member_metadata = Discogs.get_resource(d['resource_url'])
            try:
                member = Artist.objects.get(discogs_id=int(d['id']))
            except Artist.DoesNotExist:
                member = Artist.objects.create(discogs_id=int(d['id']),
                                        name=d['name'])
            member_metadata = self._save_images(member, member_metadata)
            member.about = member_metadata.get('profile')
            member_metadata = self._remove_metadata_keys(member_metadata)
            member.set_metadata_object(member_metadata)
            member.save()
            ArtistMembership.objects.create(artist=artist, member=member,
                                            active=d['active'])
        artist.save()
        metadata = self._remove_metadata_keys(metadata)
        return metadata

    def save(self):
        data = self.cleaned_data
        new = True
        metadata = Discogs.get_resource(data['resource_url'])
        try:
            artist = Artist.objects.get(discogs_id=metadata['id'])
            new = False
        except Artist.DoesNotExist:
            artist = Artist.objects.create(discogs_id=metadata['id'],
                                           name=metadata['name'],
                                           about=metadata.get('profile'))
        self.is_new = new
        if not new:
            return artist
        metadata = self._save_images(artist, metadata)
        metadata = self._save_members(artist, metadata)
        artist.set_metadata_object(metadata)
        artist.save()
        return artist


class AlbumForm(forms.Form):
    name = forms.CharField(max_length=128)
    description = forms.CharField(max_length=255, required=False)
    about = forms.CharField(required=False)
    thumb = forms.CharField(max_length=255)
    year = forms.IntegerField()
    style = forms.CharField(max_length=1024, required=False)
    genre = forms.CharField(max_length=1024, required=False)

    def __init__(self, metadata, artist, *args, **kwargs):
        super(AlbumForm, self).__init__(*args, **kwargs)
        self.metadata = metadata
        self.artist = artist
        self.is_new = False

    def save(self):
        data = self.cleaned_data
        name = data['name']
        handler = ImageHandlerAlbumCoverTemp()
        handler.load_by_url(data['thumb'])
        new_handler = handler.store()
        new_handler.save_thumbnails()
        artist = self.artist
        new = True
        try:
            album = Album.objects.get(name=name, artist=artist)
            new = False
        except Album.DoesNotExist:
            album = Album.objects.create(
                name=name,
                year=data['year'],
                artist=artist
            )
        self.is_new = new
        styles = []
        for style in simplejson.loads(data['style']):
            styles.append(AlbumStyle.objects.get_or_create(name=style)[0])
        genres = []
        for genre in simplejson.loads(data['genre']):
            genres.append(AlbumGenre.objects.get_or_create(name=genre)[0])
        album.set_metadata_object(self.metadata)
        album.artist = artist
        album.style = styles
        album.genre = genres
        album.year = data['year']
        album.thumb = handler.storage.filename
        album.save()
        return album
