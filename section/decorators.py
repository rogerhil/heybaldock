from functools import wraps

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from draft.models import ContentDraft

SLUG_MAP = {
    'event': 'eventos',
    'location': 'eventos',
    'videoalbum': 'videos',
    'photoalbum': 'fotos',
    'photo album': 'fotos',
    'video album': 'videos',
}

CT_MAP = {
    'user': 3,
    'section': 9,
    'album': 10,
    'photo': 11,
    'location': 12,
    'event': 13,
    'contentdraft': 14,
    'videoalbum': 16,
    'photoalbum': 17,
}

def _get_section_drafts_related(c, request):
    from context_processors import SECTIONS_MAP, SECTIONS_MAP_SLUG_ID
    if c.get('section'):
        section = c['section']
        drafts = ContentDraft.objects.filter(content_type=CT_MAP['section'],
                                             object_id=section.id)
    elif c.get('draft'):
        draft = c['draft']
        if draft.content_type.name == 'section':
            section = draft.object
            drafts = ContentDraft.objects.filter(content_type=CT_MAP['section'],
                                                 object_id=section.id)
        else:
            model = draft.content_type.name
            slug = SLUG_MAP[model]
            section = SECTIONS_MAP[slug]
            drafts = ContentDraft.objects.filter(content_type=CT_MAP['section'])
    elif c.get('model'):
        model = c['model']
        if model == 'section':
            section = c['object']
            drafts = ContentDraft.objects.filter(content_type=CT_MAP['section'],
                                                 object_id=section.id)
        else:
            section = SECTIONS_MAP[SLUG_MAP[model]]
            drafts = ContentDraft.objects.filter(content_type=CT_MAP[model])
    elif c.get('event'):
        section = SECTIONS_MAP['eventos']
        drafts = ContentDraft.objects.filter(content_type=CT_MAP['event'])
    else:
        slug = request.get_full_path().split('/')[1]
        section = SECTIONS_MAP[slug]
        drafts = ContentDraft.objects.filter(content_type=CT_MAP['section'],
                                        object_id=SECTIONS_MAP_SLUG_ID[slug])
    drafts.order_by('-content_date')
    return section, drafts

def render_to(template, slug=None):
    def _decorator(view_func, *args, **kwargs):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            c = view_func(request, *args, **kwargs)
            if isinstance(c, HttpResponseRedirect):
                return c
            c['section'], c['drafts_related'] = \
                                        _get_section_drafts_related(c, request)
            return render_to_response(template, RequestContext(request, c))
        return _wrapped_view
    return _decorator
