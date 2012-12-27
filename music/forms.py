# -*- coding: utf-8; Mode: Python -*-

import time
from datetime import datetime

from django import forms
from django.utils import simplejson

from models import Repertory, Album, Artist, Song, AlbumStyle, AlbumGenre, \
                   Composer, ComposerRole
from photo.image import ImageHandlerAlbumCoverTemp

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
    composers_info = forms.BooleanField(initial=True)
    track_list_enumeration = forms.BooleanField(initial=True)


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
        if not new:
            return song
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


class RepertoryForm(forms.ModelForm):

    class Meta:
        model = Repertory


class ArtistForm(forms.Form):
    name = forms.CharField(max_length=128)
    description = forms.CharField(max_length=256, required=False)
    about = forms.CharField(required=False)

    def __init__(self, metadata, *args, **kwargs):
        super(ArtistForm, self).__init__(*args, **kwargs)
        self.metadata = metadata

    def save(self):
        data = self.cleaned_data
        new = True
        name = data['name']
        try:
            artist = Artist.objects.get(name=name)
            new = False
        except Artist.DoesNotExist:
            artist = Artist.objects.create(**data)
        if not new:
            return artist
        artist.set_metadata_object(self.metadata)
        artist.save()
        return artist


class AlbumForm(forms.Form):
    name = forms.CharField(max_length=128)
    description = forms.CharField(max_length=255, required=False)
    artist_name = forms.CharField(max_length=255)
    about = forms.CharField(required=False)
    thumb = forms.CharField(max_length=255)
    year = forms.IntegerField()
    style = forms.CharField(max_length=1024, required=False)
    genre = forms.CharField(max_length=1024, required=False)

    def __init__(self, metadata, *args, **kwargs):
        super(AlbumForm, self).__init__(*args, **kwargs)
        self.metadata = metadata
        self.artist_form = None

    def is_valid(self):
        is_valid = super(AlbumForm, self).is_valid()
        data = self.data
        self.artist_form = ArtistForm({}, {'name': data['artist_name']})
        is_valid = is_valid and self.artist_form.is_valid()
        return is_valid

    def save(self):
        data = self.cleaned_data
        name = data['name']
        handler = ImageHandlerAlbumCoverTemp()
        handler.load_by_url(data['thumb'])
        new_handler = handler.store()
        new_handler.save_thumbnails()
        artist = self.artist_form.save()
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
        if not new:
            return album
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
