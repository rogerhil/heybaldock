
from functools import wraps

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _


def repertory_is_locked(request, repertory):
    if not repertory.is_editable(request.user):
        msg = _("You can't make any changes in a locked repertory.")
        messages.add_message(request, messages.WARNING, msg)
        url = reverse('repertory_details', args=(repertory.id,))
        return HttpResponseRedirect(url)

def ajax_repertory_is_locked(request, repertory):
    if not repertory.is_editable(request.user):
        msg = _("You can't make any changes in a locked repertory.")
        return dict(success=False, message=msg)

def check_locked_repertory(view_func, *args, **kwargs):
    from music.models import Repertory
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        repertory = get_object_or_404(Repertory, id=kwargs['id'])
        url = repertory_is_locked(request, repertory)
        return url or view_func(request, *args, **kwargs)

    return _wrapped_view

def ajax_check_locked_main_repertory(view_func, *args, **kwargs):
    from music.models import Repertory
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        repertory = Repertory.get_main_repertory()
        d = ajax_repertory_is_locked(request, repertory)
        return d or view_func(request, *args, **kwargs)
    return _wrapped_view

def ajax_check_locked_repertory(view_func, *args, **kwargs):
    from music.models import Repertory
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        repertory = get_object_or_404(Repertory, id=kwargs['id'])
        d = ajax_repertory_is_locked(request, repertory)
        return d or view_func(request, *args, **kwargs)
    return _wrapped_view

def ajax_check_locked_repertory_item(view_func, *args, **kwargs):
    from music.models import RepertoryGroupItem
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        item = get_object_or_404(RepertoryGroupItem, id=kwargs['id'])
        d = ajax_repertory_is_locked(request, item.group.repertory)
        return d or view_func(request, *args, **kwargs)
        return url or view_func(request, *args, **kwargs)
    return _wrapped_view

def ajax_check_locked_player_repertory_item(view_func, *args, **kwargs):
    from music.models import PlayerRepertoryItem
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        player = get_object_or_404(PlayerRepertoryItem, id=kwargs['id'])
        repertory = player.repertory_item.group.repertory
        d = ajax_repertory_is_locked(request, repertory)
        return d or view_func(request, *args, **kwargs)
    return _wrapped_view