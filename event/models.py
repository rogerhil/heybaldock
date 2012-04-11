from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext, ugettext_lazy as _


class Location(models.Model):
    """
    """
    name = models.CharField(_("Name"), max_length=64)
    description = models.CharField(_("Description"), max_length=255, null=True, blank=True)
    zipcode = models.CharField(_("Zip code"), max_length=8)
    address = models.CharField(_("Address"), max_length=255)
    city = models.CharField(_("City"), max_length=128)
    state = models.CharField(_("State"), max_length=128)
    country = models.CharField(_("Country"), max_length=128)
    latitude = models.IntegerField()
    longitude = models.IntegerField()
    #album = models.ForeignKey(Album, verbose_name=_("Album"), null=True)
    phone1 = models.IntegerField(_("Phone 1"))
    phone2 = models.IntegerField(_("Phone 2"), null=True, blank=True)
    phone3 = models.IntegerField(_("Phone 3"), null=True, blank=True)
    phone4 = models.IntegerField(_("Phone 4"), null=True, blank=True)

    template_view = "event/location.html"
    template_varname = "location"

    def __unicode__(self):
        return "%s - %s" % (self.name, self.address)

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

    def __unicode__(self):
        return "%s - %s" % (self.name, self.datetime)

    @property
    def datetime(self):
        start = self.starts_at.strftime("%d/%m/%Y")
        if self.starts_at == self.ends_at:
            return start
        end = self.ends_at.strftime("%d/%m/%Y")
        return ugettext("from %s to %s") % (start, end)

    def url(self):
        return reverse('event_details', args=(self.id,))

    @staticmethod
    def form():
        from forms import EventForm
        return EventForm

