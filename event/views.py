from datetime import datetime

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from auth.decorators import login_required
from section.decorators import render_to
from models import Event, Location
from maps import search_zip
from lib.decorators import ajax


@render_to("event/event_details.html")
def event_details(request, id):
    event = get_object_or_404(Event, id=id)
    return dict(event=event)

@render_to("event/event_history.html")
def event_history(request):
    now = datetime.now()
    events = Event.objects.filter(ends_at__lte=now).order_by('-starts_at')
    return dict(events_history=events)

@login_required
@require_POST
def delete_event(request, id):
    event = get_object_or_404(Event, id=id)
    name = event.name
    try:
        event.delete()
        msg = _('The event "%s" was successfully deleted.' % name)
        messages.add_message(request, messages.SUCCESS, msg)
    except Exception, err:
        args = dict(name=name, err=err)
        msg = _('Error while trying to delete the "%(name)s" ' \
                'event. %(err)s' % args)
        messages.add_message(request, messages.ERROR, msg)
    url = reverse('section_view', args=('eventos',))
    return HttpResponseRedirect(url)

@render_to("event/location_list.html")
def location_list(request):
    return dict()

@render_to("event/location_details.html")
def location_details(request, id):
    location = get_object_or_404(Location, id=id)
    return dict(location=location)

@login_required
@require_POST
def delete_location(request, id):
    location = get_object_or_404(Location, id=id)
    name = location.name
    try:
        location.delete()
        msg = _('The location "%s" was successfully deleted.' % name)
        messages.add_message(request, messages.SUCCESS, msg)
    except Exception, err:
        args = dict(name=name, err=err)
        msg = _('Error while trying to delete the "%(name)s" ' \
                'location. %(err)s' % args)
        messages.add_message(request, messages.ERROR, msg)
    url = reverse('location_list')
    return HttpResponseRedirect(url)

@ajax
def address_by_zipcode(request):
    zipcode = request.GET['zipcode']
    data = search_zip(zipcode)
    return {'success': True, 'data': data}
