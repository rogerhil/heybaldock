from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from models import Section
from decorators import render_to

@render_to("section/large_section.html")
def section_home(request):
    section = get_object_or_404(Section, slug='home')
    return dict(section=section, request=request)

@render_to("section/section.html")
def section_view(request, slug):
    if slug == 'home':
        return HttpResponseRedirect('/')
    section = get_object_or_404(Section, slug=slug)
    return dict(section=section, request=request)

