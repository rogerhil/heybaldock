from django.shortcuts import get_object_or_404

from models import Section
from decorators import render_to

def section_home(request):
    return section_view(request, "home")

@render_to("section/section.html")
def section_view(request, slug):
    section = get_object_or_404(Section, slug=slug)
    return dict(section=section, request=request)

