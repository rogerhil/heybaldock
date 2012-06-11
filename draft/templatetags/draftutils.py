from django import template
from django.core.urlresolvers import reverse
from django.template.context import Context
from django.template.loader import get_template
from django.utils.translation import ugettext as _

from section.settings import SECTION_ID_MAP

register = template.Library()

_ACTIONS = {
    'videoalbum_add': {'url': reverse('add_draft_new', args=('videoalbum',)),
                       'name': _('Add video album')},
    'photoalbum_add': {'url': reverse('add_draft_new', args=('photoalbum',)),
                       'name': _('Add photo album')},
    'event_add': {'url': reverse('add_draft_new', args=('event',)),
                       'name': _('Add new event')}
}

ACTIONS = {
    'section': {
        'videos': [_ACTIONS['videoalbum_add']],
        'fotos': [_ACTIONS['photoalbum_add']],
        'eventos': [_ACTIONS['event_add']],
    },
    'videoalbum': [_ACTIONS['videoalbum_add']],
    'photoalbum': [_ACTIONS['photoalbum_add']]
}

@register.simple_tag()
def object_manage_buttons(user, model, object_id):
    template = get_template("draft/object_manage_buttons.html")
    actions = []
    if model == 'section':
        actions += ACTIONS[model].get(SECTION_ID_MAP[object_id], [])
    else:
        actions += ACTIONS.get(model, [])
    c = {'user': user,
         'model': model,
         'object_id': object_id,
         'actions': actions}
    return template.render(Context(c))
