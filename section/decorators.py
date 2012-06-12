from functools import wraps

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from draft.models import ContentDraft

SLUG_MAP = {
    'event': 'eventos',
    'location': 'eventos',
    'videoalbum': 'videos',
    'photoalbum': 'fotos',
    'photo album': 'fotos',
    'video album': 'videos',
}

TRANSLATIONS = {
    'event': _('Event'),
    'location': _('Location'),
    'videoalbum': _('Video Album'),
    'photoalbum': _('Photo Album'),
    'photo album': _('Photo Album'),
    'video album': _('Video Album'),
}

trans = lambda x: TRANSLATIONS.get(x, _("%s section" % x))

CT_MAP = {}

if not CT_MAP:
    v = lambda x: (x.name.replace(' ', ''), x.id)
    CT_MAP = dict([v(i) for i in ContentType.objects.all()])

def _get_section_drafts_related(c, request):
    from context_processors import SECTIONS_MAP, SECTIONS_MAP_SLUG_ID
    def dfilter(ct, oid):
        return ContentDraft.objects.filter(content_type=ct, object_id=oid)
    drafts = []
    model_title = ''
    if c.get('section'):
        section = c['section']
        drafts = dfilter(CT_MAP['section'], section.id)
        model_title = trans(section.menu_title)
    elif c.get('draft'):
        draft = c['draft']
        if draft.content_type.name == 'section':
            section = draft.object
            drafts = dfilter(CT_MAP['section'], section.id)
            model_title = trans(section.menu_title)
        else:
            model = draft.content_type.name.replace(' ', '')
            slug = SLUG_MAP[model]
            section = SECTIONS_MAP[slug]
            if draft.object_id:
                drafts = dfilter(CT_MAP[model], draft.object_id)
                model_title = trans(model)
    elif c.get('model'):
        model = c['model']
        if model == 'section':
            slug = c['object'].slug
        else:
            slug = SLUG_MAP[model]
        section = SECTIONS_MAP[slug]
        if c.get('object'):
            drafts = dfilter(CT_MAP[model], c['object'].id)
            model_title = trans(model)
    elif c.get('event'):
        section = SECTIONS_MAP['eventos']
        drafts = dfilter(CT_MAP['event'], c['event'].id)
        model_title = trans('event')
    elif c.get('album'):
        model = c['album']._meta.module_name
        section = SECTIONS_MAP[SLUG_MAP[model]]
        drafts = dfilter(CT_MAP[model], c['album'].id)
        model_title = trans(model)
    elif c.get('location'):
        model = c['location']._meta.module_name
        section = SECTIONS_MAP[SLUG_MAP[model]]
        drafts = dfilter(CT_MAP[model], c['location'].id)
        model_title = trans(model)
    else:
        slug = request.get_full_path().split('/')[1]
        if slug == 'busca':
            section = SECTIONS_MAP['home']
        else:
            section = SECTIONS_MAP[slug]
            drafts = dfilter(CT_MAP['section'], SECTIONS_MAP_SLUG_ID[slug])
            model_title = trans(section.menu_title)
    if not isinstance(drafts, list):
        drafts.order_by('-content_date')
    return dict(section=section,
                drafts_related=drafts,
                model_title=model_title)

def render_to(template, slug=None):
    def _decorator(view_func, *args, **kwargs):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            c = view_func(request, *args, **kwargs)
            if isinstance(c, HttpResponseRedirect):
                return c
            c.update(_get_section_drafts_related(c, request))
            return render_to_response(template, RequestContext(request, c))
        return _wrapped_view
    return _decorator
