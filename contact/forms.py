from django import forms
from django.utils.translation import ugettext as _

from mail import send_mail

class ContactForm(forms.Form):
    """
    """

    name = forms.CharField(label=_("Name"), max_length=128)
    email = forms.EmailField(label=_("E-mail"), max_length=128)
    subject = forms.CharField(label=_("Subject"), max_length=255)
    message = forms.CharField(label=_("Message"), widget=forms.Textarea())

    def save(self):
        data = self.cleaned_data
        send_mail(data['name'], data['email'],
                  data['subject'], data['message'])