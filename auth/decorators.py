from functools import wraps

from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required, permission_required

login_required = login_required(login_url="/auth/login")


def draft_permission_required(view_func):
    from draft.models import ContentDraft
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        draft = get_object_or_404(ContentDraft, id=kwargs['id'])
        app_label = draft.content_type.app_label
        model = draft.content_type.model
        perm = '%s.manage_%ss' % (app_label, model)
        redirect = '/permission/denied/'
        return permission_required(perm, redirect)(view_func)(request,
                                                              *args, **kwargs)
    return _wrapped_view

def draft_model_permission_required(view_func):

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        ct = ContentType.objects.get(model=kwargs['model'])
        app_label = ct.app_label
        model = ct.model
        perm = '%s.manage_%ss' % (app_label, model)
        redirect = '/permission/denied/'
        return permission_required(perm, redirect)(view_func)(request,
                                                              *args, **kwargs)
    return _wrapped_view