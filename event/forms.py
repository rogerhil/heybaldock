
from django.forms import ValidationError
from django.utils.translation import ugettext as _

from models import Event, Location, LocationType
from draft import forms


class EventForm(forms.CmsForm):

    class Meta:
        model = Event
        fields = ('name', 'description', 'content', 'starts_at', 'ends_at',
                  'location')

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        choices = Location.objects.filter(location_type=LocationType.show)
        self.fields['location'].choices = [(i.id, i) for i in choices]



class LocationForm(forms.CmsForm):

    class Meta:
        model = Location
        fields = ('name', 'description', 'zipcode', 'street', 'number',
                  'complement', 'district', 'city', 'state', 'country',
                  'latitude', 'longitude', 'phone1', 'phone2', 'phone3',
                  'location_type')
    class Media:
        js = ('/media/js/locationform.js',)

    def _clean_phone(self, phone, required=False):
        phone = phone.replace(' ', '')
        if not phone and not required:
            return phone
        if not phone.isdigit():
            raise ValidationError(_("Phone must have only digits"))
        if len(phone) < 8:
            raise ValidationError(_("Phone must have at least 8 digits"))
        return phone

    def clean_phone1(self):
        return self._clean_phone(self.cleaned_data['phone1'], required=True)

    def clean_phone2(self):
        return self._clean_phone(self.cleaned_data['phone2'])

    def clean_phone3(self):
        return self._clean_phone(self.cleaned_data['phone3'])