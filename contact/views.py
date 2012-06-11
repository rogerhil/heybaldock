from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.utils.translation import ugettext as _

from forms import ContactForm
from section.views import section_view

@require_POST
def send_mail(request):
    form = ContactForm(request.POST)
    if form.is_valid():
        form.save()
        msg = _('Your message has been successfully sent')
        messages.add_message(request, messages.SUCCESS, msg)
        url = reverse('section_view', args=('contato',))
        return HttpResponseRedirect(url)
    else:
        return section_view(request, slug='contato')