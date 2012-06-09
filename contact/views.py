from django.views.decorators.http import require_POST
from django.utils.translation import ugettext as _

from forms import ContactForm
from section.views import section_view

@require_POST
def send_mail(request):
    form = ContactForm(request.POST)
    if form.is_valid():
        form.save()
        text = _('Your message has been successfully sent')
        msg = {'type': 'success', 'text': text}
        request.POST = {}
        return section_view(request, slug='contato', message=msg)
    else:
        return section_view(request, slug='contato')