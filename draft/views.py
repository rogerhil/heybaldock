
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from django.views.decorators.http import require_POST

from hbauth.decorators import login_required, draft_permission_required, \
                              draft_model_permission_required
from draft.models import ContentDraft
from event.models import Event
from photo.image import ImageHandlerSections
from section.decorators import render_to
from section.templatetags.wysiwygtags import UI_TAGS


@login_required
@render_to("draft/view.html")
@draft_permission_required
def view(request, id):
    draft = get_object_or_404(ContentDraft, id=id)
    return dict(draft=draft)

@login_required
@render_to("draft/edit.html")
@draft_model_permission_required
def add_new(request, model):
    ct = ContentType.objects.get(model=model)
    model_class = ct.model_class()
    if request.POST:
        form = model_class.form()(user=request.user, data=request.POST)
        valid = form.is_valid()
        js_valid = form.js_is_valid(request.POST)
        if valid and js_valid:
            form.save()
            url = reverse('view_draft', args=(form.draft.id,))
            return HttpResponseRedirect(url)
    else:
        form = model_class.form()(user=request.user)
    return dict(form=form, model=model, model_class=model_class)

@login_required
@draft_model_permission_required
def add(request, model, id):
    ct = ContentType.objects.get(model=model)
    model_class = ct.model_class()
    object = get_object_or_404(model_class, id=id)
    return _edit(request, object, model=model)

@login_required
@draft_permission_required
def edit(request, id):
    draft = get_object_or_404(ContentDraft, id=id)
    return _edit(request, draft.object, draft=draft)

@render_to("draft/edit.html")
def _edit(request, object, model=None, draft=None):
    user = request.user
    if draft:
        model_class = draft.content_type.model_class()
    else:
        model_class = type(object)
    form_class = object and object.form() or model_class.form()
    if request.POST:
        if draft and object:
            form = form_class(user=user, draft=draft, instance=object,
                                                         data=request.POST)
        elif draft:
            form = form_class(user=user, draft=draft, data=request.POST)
        else:
            form = form_class(user=user, instance=object, data=request.POST)
        valid = form.is_valid()
        js_valid = form.js_is_valid(request.POST)
        if valid and js_valid:
            form.save()
            url = reverse('view_draft', args=(form.draft.id,))
            return HttpResponseRedirect(url)
    else:
        if draft and object:
            form = form_class(user=user, draft=draft, instance=object)
        elif object:
            form = form_class(user=user, instance=object)
        elif draft:
            form = form_class(user=user, draft=draft)
    ui_tags = simplejson.dumps(UI_TAGS)
    images_urls = ImageHandlerSections.list_all_urls()
    images_urls_json = simplejson.dumps(images_urls)
    return dict(form=form, object=object, model=model, draft=draft,
                ui_tags=ui_tags, images_urls_json=images_urls_json,
                images_urls=images_urls, model_class=model_class)

@login_required
@require_POST
@draft_permission_required
def publish(request, id):
    draft = get_object_or_404(ContentDraft, id=id)
    ct = draft.content_type
    user = request.user
    object = draft.object
    if object:
        form = ct.model_class().form()(user=user, instance=object, draft=draft)
    else:
        form = ct.model_class().form()(user=user, draft=draft)
    if isinstance(form.instance, Event) and not form.instance.band:
        form.instance.band = request.band
    object = form.publish()
    request.band.reload_band_cache(request)
    return HttpResponseRedirect(object.url())

@login_required
@require_POST
@draft_permission_required
def delete(request, id):
    draft = get_object_or_404(ContentDraft, id=id)
    url = draft.object.url()
    draft.delete()
    return HttpResponseRedirect(url)
