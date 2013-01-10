from models import Event, Location
from draft import forms


class EventForm(forms.CmsForm):

    class Meta:
        model = Event
        fields = ('name', 'description', 'content', 'starts_at', 'ends_at',
                  'location')


class LocationForm(forms.CmsForm):

    class Meta:
        model = Location
        fields = ('name', 'description', 'zipcode', 'street', 'number',
                  'complement', 'district', 'city', 'state', 'country',
                  'latitude', 'longitude', 'phone1', 'phone2', 'phone3',
                  'location_type')
    class Media:
        js = ('/media/js/locationform.js',)