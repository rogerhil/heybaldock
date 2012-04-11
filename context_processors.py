from datetime import datetime

from section.models import Section
from event.models import Event, Location

SECTIONS = [i for i in Section.objects.all()]
SECTIONS_MAP = dict([(i.slug, i) for i in SECTIONS])
SECTIONS_MAP_ID = dict([(i.id, i) for i in SECTIONS])
SECTIONS_MAP_SLUG_ID = dict([(i.slug, i.id) for i in SECTIONS])

def main(request):
    now = datetime.now()
    events = Event.objects.filter(starts_at__gte=now).order_by('-starts_at')[:10]
    locations = Location.objects.all().order_by('name')[:10]

    #if request.user.is_authenticated():
    #    drafts = section.drafts_related()

    c = dict(sections=SECTIONS,
             events=events,
             locations=locations,
             request_get=request.GET)
    return c