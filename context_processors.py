from datetime import datetime

from django.conf import settings

from section.models import Section
from event.models import Event, Location
from music.models import Rehearsal

SECTIONS = [i for i in Section.objects.all().order_by('order')]
SECTIONS_MAP = dict([(i.slug, i) for i in SECTIONS])
SECTIONS_MAP_ID = dict([(i.id, i) for i in SECTIONS])
SECTIONS_MAP_SLUG_ID = dict([(i.slug, i.id) for i in SECTIONS])

def main(request):
    user = request.user
    now = datetime.now()
    events = Event.objects.filter(starts_at__gte=now).order_by('-starts_at')[:10]
    locations = Location.objects.all().order_by('name')[:10]
    upcoming_rehearsals = Rehearsal.objects.filter(date__gte=now)
    logged = user.is_authenticated()

    permissions = dict(
        manage_rehearsals=logged and user.has_perm("music.manage_rehearsals"),
        manage_events=logged and user.has_perm("event.manage_events"),
        manage_locations=logged and user.has_perm("event.manage_locations"),
        manage_sections=logged and user.has_perm("section.manage_sections"),
    )
    c = dict(
        sections=SECTIONS,
        band=request.band,
        events=events,
        locations=locations,
        upcoming_rehearsals=upcoming_rehearsals,
        request_get=request.GET,
        site_domain=settings.SITE_DOMAIN,
        facebook_app_id=settings.FACEBOOK_APP_ID,
        enable_repertory_features=settings.ENABLE_REPERTORY_FEATURES,
        permissions=permissions
    )
    return c