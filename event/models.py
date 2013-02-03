# -*- coding: utf-8; Mode: Python -*-

from datetime import datetime

from django.db import models
from django.db.models.signals import pre_save, pre_delete
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext, ugettext_lazy as _

from contact.models import Notification

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

class LocationType:
    show = 1
    studio = 2
    home = 3

    @classmethod
    def choices(cls):
        choices = [(getattr(cls, k), k.title()) for k in dir(cls)
                                                  if not k.startswith('__') and
                                      not hasattr(getattr(cls, k), '__call__')]
        choices.sort(lambda a, b: 1 if a[0] > b[0] else -1)
        return choices

    @classmethod
    def display(cls, t):
        return dict(cls.choices()).get(t)


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
    phone1 = models.CharField(_("Phone 1"), max_length=20)
    phone2 = models.CharField(_("Phone 2"), max_length=20, null=True, blank=True)
    phone3 = models.CharField(_("Phone 3"), max_length=20, null=True, blank=True)
    location_type = models.SmallIntegerField(default=LocationType.show,
                                             choices=LocationType.choices())

    template_view = "event/location.html"
    template_varname = "location"
    media = {'scripts': ['/media/js/maps.js',
                         'https://maps.google.com/maps/api/js?sensor=true']}

    def __unicode__(self):
        return unicode(self.name)

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

    @property
    def type_display(self):
        return LocationType.display(self.location_type)

    @property
    def zipcode_display(self):
        if len(self.zipcode) > 5:
            return "%s-%s" % (self.zipcode[:5], self.zipcode[5:])
        else:
            return self.zipcode

    @property
    def phones_display(self):
        def d(phone):
            if len(phone) < 8:
                return phone
            elif len(phone) == 8 or len(phone) == 9:
                return "%s-%s" % (phone[:4], phone[4:])
            elif len(phone) > 9:
                return "(%s) %s-%s" % (phone[:2], phone[2:6], phone[6:])
        phones = [self.phone1, self.phone2, self.phone3]
        return ', '.join([d(p) for p in phones if p and p.strip()])


class Event(models.Model):
    """
    """
    name = models.CharField(_("Name"), max_length=64)
    description = models.CharField(_("Description"), max_length=255, null=True)
    content = models.TextField(_("Content"), blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    location = models.ForeignKey(Location, verbose_name=_("Location"))
    band = models.ForeignKey("music.Band", null=True, related_name="events")

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

    @property
    def is_upcoming(self):
        now = datetime.now()
        return self.starts_at > now

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

    @classmethod
    def pre_save(cls, instance, **kwargs):
        if not instance.id:
            band = instance.band
            band.shows_count += 1
            band.save()

    @classmethod
    def pre_delete(cls, instance, **kwargs):
        from music.models import EventRepertory
        band = instance.band
        band.shows_count -= 1
        band.save()
        repertories = EventRepertory.objects.filter(event=instance)
        # make sure all repertories related will go on too
        repertories.delete()
        ct = ContentType.objects.get_for_model(type(instance))
        notifications = Notification.objects.filter(content_type=ct,
                                                    object_id=instance.id)
        notifications.delete()


pre_save.connect(Event.pre_save, Event)
pre_delete.connect(Event.pre_delete, Event)
