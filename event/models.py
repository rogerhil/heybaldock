# -*- coding: utf-8; Mode: Python -*-

from datetime import datetime

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext, ugettext_lazy as _

STATE_CHOICES = [
    (u'AC', u'Acre'),
    (u'AL', u'Alagoas'),
    (u'AP', u'Amapá'),
    (u'AM', u'Amazonas'),
    (u'BA', u'Bahia'),
    (u'CE', u'Ceará'),
    (u'DF', u'Distrito Federal'),
    (u'ES', u'Espírito Santo'),
    (u'GO', u'Goiás'),
    (u'MA', u'Maranhão'),
    (u'MT', u'Mato Grosso'),
    (u'MS', u'Mato Grosso do Sul'),
    (u'MG', u'Minas Gerais'),
    (u'PB', u'Paraiba'),
    (u'PR', u'Paraná'),
    (u'PA', u'Pará'),
    (u'PE', u'Pernambuco'),
    (u'PI', u'Piauí'),
    (u'RN', u'Rio Grande do Norte'),
    (u'RS', u'Rio Grande do Sul'),
    (u'RJ', u'Rio de Janeiro'),
    (u'RO', u'Rondônia'),
    (u'RR', u'Roraima'),
    (u'SC', u'Santa Catarina'),
    (u'SE', u'Sergipe'),
    (u'SP', u'São Paulo'),
    (u'TO', u'Tocantins')
]

class Location(models.Model):
    """
    """
    name = models.CharField(_("Name"), max_length=64)
    description = models.CharField(_("Description"), max_length=255, null=True, blank=True)
    zipcode = models.CharField(_("Zip code"), max_length=8)
    street = models.CharField(_("Street"), max_length=128)
    district = models.CharField(_("District"), max_length=128)
    number = models.IntegerField(_("Number"))
    complement = models.CharField(_("Complement"), max_length=32, null=True, blank=True)
    city = models.CharField(_("City"), max_length=128)
    state = models.CharField(_("State"), max_length=5, choices=STATE_CHOICES)
    country = models.CharField(_("Country"), max_length=128, default='Brazil')
    latitude = models.FloatField()
    longitude = models.FloatField()
    album = models.ForeignKey('photo.PhotoAlbum', verbose_name=_("Album"), null=True)
    phone1 = models.IntegerField(_("Phone 1"))
    phone2 = models.IntegerField(_("Phone 2"), null=True, blank=True)
    phone3 = models.IntegerField(_("Phone 3"), null=True, blank=True)

    template_view = "event/location.html"
    template_varname = "location"
    media = {'scripts': ['/media/js/maps.js',
                         'https://maps.google.com/maps/api/js?sensor=true']}

    def __unicode__(self):
        return "%s - %s" % (self.name, self.address)

    @property
    def address(self):
        return "%s, %s %s - %s" % (self.street, self.number, self.complement,
                                self.district)

    def url(self):
        return reverse('location_details', args=(self.id,))

    @staticmethod
    def form():
        from forms import LocationForm
        return LocationForm



class Event(models.Model):
    """
    """
    name = models.CharField(_("Name"), max_length=64)
    description = models.CharField(_("Description"), max_length=255, null=True)
    content = models.TextField(_("Content"), blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    location = models.ForeignKey(Location, verbose_name=_("Location"))

    template_view = "event/details.html"
    template_varname = "event"
    media = {'scripts': ['/media/js/maps.js',
                         'https://maps.google.com/maps/api/js?sensor=true',
                         '/media/js/jquery/jquery.ui.timepicker.addon.js',
                         '/media/js/eventform.js']}

    def __unicode__(self):
        return "%s - %s" % (self.name, self.datetime)

    @property
    def datetime(self):
        start = self.starts_at.strftime("%d/%m/%Y")
        if self.starts_at == self.ends_at:
            return start
        end = self.ends_at.strftime("%d/%m/%Y")
        args = dict(start=start, end=end)
        return ugettext("from %(start)s to %(end)s") % args

    def url(self):
        return reverse('event_details', args=(self.id,))

    @staticmethod
    def form():
        from forms import EventForm
        return EventForm

    @property
    def photos(self):
        return self.photo_albums.filter(flyer=False)

    @property
    def flyers(self):
        return self.photo_albums.filter(flyer=True)

    @property
    def first_flyer(self):
        flyers = [i for i in self.flyers]
        if flyers:
            photos = [i for i in flyers[0].photos.all()]
            if photos:
                return photos[0]

    def is_last_event(self):
        last_event = self.get_last_event()
        return self.id == last_event.id

    def is_last_new_event(self):
        last_new_event = self.get_last_new_event()
        return self.id == last_new_event.id

    @classmethod
    def get_last_event(cls):
        try:
            return cls.objects.all().order_by('-starts_at')[0]
        except IndexError:
            return

    @classmethod
    def get_last_new_event(cls):
        now = datetime.now()
        try:
            return cls.objects.filter(starts_at__gt=now)\
                              .order_by('-starts_at')[0]
        except IndexError:
            return
