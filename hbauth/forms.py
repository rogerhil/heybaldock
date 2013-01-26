
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from hbauth.models import UserProfile
from photo.image import ImageHandlerUserPhoto
from music.utils import generate_filename
from event.models import Location, LocationType

class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class UserProfileForm(forms.ModelForm):

    photo = forms.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ('friendly_name', 'birth_date', 'photo')

    def save(self, commit=True):
        data = self.cleaned_data
        if data.get('photo') and not isinstance(data['photo'], basestring):
            if self.instance.photo and self.instance.image_handler and \
               self.instance.image_handler.storage:
                self.instance.image_handler.delete()
            filename = generate_filename(data['photo'].name)
            handler = ImageHandlerUserPhoto()
            handler.load(filename, data['photo'])
            handler.save_thumbnails('PNG')
            self.instance.photo=filename
        self.instance.friendly_name=data.get('friendly_name')
        self.instance.birth_date=data['birth_date']
        self.instance.save()


class UserLocationForm(forms.ModelForm):

    name_choices = [
        (_('House'), _('House')),
        (_('Apartment'), _('Apartment')),
    ]

    class Meta:
        model = Location
        exclude = ('description', 'album', 'location_type')

    def __init__(self, user, *args, **kwargs):
        super(UserLocationForm, self).__init__(*args, **kwargs)
        self.user = user
        self.fields['name'].widget = forms.Select(choices=self.name_choices)

    def save(self, commit=True):
        data = self.cleaned_data
        data['name'] = LocationType.home
        data['location_type'] = LocationType.home
        instance = super(UserLocationForm, self).save(commit=commit)
        profile = self.user.profile
        profile.address = instance
        profile.save()
