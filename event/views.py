from datetime import datetime

from django.shortcuts import get_object_or_404

from section.decorators import render_to
from models import Event, Location

@render_to("event/event_details.html")
def event_details(request, id):
    event = get_object_or_404(Event, id=id)
    return dict(event=event)

@render_to("event/event_history.html")
def event_history(request):
    now = datetime.now()
    events = Event.objects.filter(ends_at__lte=now).order_by('-starts_at')
    return dict(events_history=events)

@render_to("event/location_list.html")
def location_list(request):
    return dict()

@render_to("event/location_details.html")
def location_details(request, id):
    location = get_object_or_404(Location, id=id)
    return dict(location=location)

