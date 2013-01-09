from datetime import datetime

from django.conf import settings

from section.models import Section
from event.models import Event, Location

SECTIONS = [i for i in Section.objects.all().order_by('order')]
SECTIONS_MAP = dict([(i.slug, i) for i in SECTIONS])
SECTIONS_MAP_ID = dict([(i.id, i) for i in SECTIONS])
SECTIONS_MAP_SLUG_ID = dict([(i.slug, i.id) for i in SECTIONS])

def main(request):
    now = datetime.now()
    events = Event.objects.filter(starts_at__gte=now).order_by('-starts_at')[:10]
    locations = Location.objects.all().order_by('name')[:10]
    c = dict(
        sections=SECTIONS,
        band=request.band,
        events=events,
        locations=locations,
        request_get=request.GET,
        site_domain=settings.SITE_DOMAIN,
        facebook_app_id=settings.FACEBOOK_APP_ID,
        enable_repertory_features=settings.ENABLE_REPERTORY_FEATURES
    )
    return c