
from django import forms
from django.conf import settings
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
        args = dict(name=data['name'], email=data['email'])
        msgfrom = _("Message from %(name)s, e-mail: %(email)s\n\n" % args)
        body = msgfrom + data['message']
        send_mail(data['subject'], body, settings.MAIL_USER)