from models import Section

SECTION_ID_MAP = {}

def build_section_id_map():
    global SECTION_ID_MAP
    if not SECTION_ID_MAP:
        sections = Section.objects.all()
        SECTION_ID_MAP = dict([(s.id, s.slug) for s in sections])

build_section_id_map()
