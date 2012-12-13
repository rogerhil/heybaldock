# -*- coding: utf-8; Mode: Python -*-

from datetime import datetime

from django import forms

from models import Repertory, Album, Artist, Song

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
    till_year = forms.ChoiceField(choices=YEAR_CHOICES, initial=1970)
    composers_info = forms.BooleanField(initial=True)
    track_list_enumeration = forms.BooleanField(initial=True)


class RepertoryForm(forms.ModelForm):

    class Meta:
        model = Repertory


class SongForm(forms.Form):
    name = forms.CharField(max_length=128)
    description = forms.CharField(max_length=256, required=False)
    about = forms.CharField(required=False)
    album = forms.IntegerField()
    lyrics = forms.CharField(required=False)
    duration = forms.IntegerField()
    position = forms.CharField(max_length=5)

    def save(self):
        data = self.cleaned_data
        song = Song.objects.create(**data)
        return song


class ArtistForm(forms.Form):
    discogsid = forms.IntegerField()
    name = forms.CharField(max_length=128)
    description = forms.CharField(max_length=256, required=False)
    about = forms.CharField(required=False)

    def __init__(self, metadata, *args, **kwargs):
        super(ArtistForm, self).__init__(*args, **kwargs)
        self.metadata = metadata

    def save(self):
        data = self.cleaned_data
        artist = Artist.objects.create(**data)
        artist.set_metadata_object(self.metadata)
        return album


class AlbumForm(forms.Form):
    discogsid = forms.IntegerField()
    catno = forms.CharField(max_length=128)
    name = forms.CharField(max_length=128)
    description = forms.CharField(max_length=255, required=False)
    about = forms.CharField(required=False)
    artist = forms.IntegerField()
    thumb = forms.CharField(max_length=255)
    uri = forms.CharField(max_length=255)
    year = forms.IntegerField()

    def __init__(self, metadata, *args, **kwargs):
        super(AlbumForm, self).__init__(*args, **kwargs)
        self.metadata = metadata

    def save(self):
        data = self.cleaned_data
        album = Album.objects.create(**data)
        album.set_metadata_object(self.metadata)
        return album
