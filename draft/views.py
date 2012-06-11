import simplejson

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from auth.decorators import login_required
from draft.models import ContentDraft
from section.decorators import render_to
from section.templatetags.wysiwygtags import UI_TAGS

@login_required
@render_to("draft/view.html")
def view(request, id):
    draft = get_object_or_404(ContentDraft, id=id)
    return dict(draft=draft)

@login_required
@render_to("draft/edit.html")
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
def add(request, model, id):
    ct = ContentType.objects.get(model=model)
    model_class = ct.model_class()
    object = get_object_or_404(model_class, id=id)
    return _edit(request, object, model=model)

@login_required
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
    print form.errors
    ui_tags = simplejson.dumps(UI_TAGS)
    return dict(form=form, object=object, model=model, draft=draft,
                ui_tags=ui_tags, model_class=model_class)

@login_required
@require_POST
def publish(request, id):
    draft = get_object_or_404(ContentDraft, id=id)
    ct = draft.content_type
    user = request.user
    object = draft.object
    if object:
        form = ct.model_class().form()(user=user, instance=object, draft=draft)
    else:
        form = ct.model_class().form()(user=user, draft=draft)
    object = form.publish()
    return HttpResponseRedirect(object.url())

@login_required
@require_POST
def delete(request, id):
    draft = get_object_or_404(ContentDraft, id=id)
    url = draft.object.url()
    draft.delete()
    return HttpResponseRedirect(url)
