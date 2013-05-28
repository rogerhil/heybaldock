from datetime import datetime

from django import template
from django.template.context import Context
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from event.models import Event
from video.models import VideoAlbum
from photo.models import PhotoAlbum
from contact.forms import ContactForm

register = template.Library()

UI_TAGS = [
    ('upcoming_events', _('Upcoming Events List')),
    ('event_history_button', _('Event History Button Link')),
    ('video_albums', _('Video Albums list')),
    ('photo_albums', _('Photo Albums list')),
    ('contact_form', _('Contact Form')),
    ('facebook_like_button', _('Facebook Like Button')),
]

@register.simple_tag()
def upcoming_events():
    now = datetime.now()
    events = Event.objects.filter(starts_at__gte=now)\
                          .order_by('-starts_at')
    c = dict(events=events)
    return render_to_string("event/event_list.html", Context(c))

@register.simple_tag()
def event_history_button():
    c = dict()
    return render_to_string("event/event_history_button.html", Context(c))

@register.simple_tag()
def video_albums():
    albums = VideoAlbum.objects.filter(listable=True).order_by('-updated')
    c = dict(albums=albums)
    return render_to_string("video/video_albums.html", Context(c))

@register.simple_tag()
def photo_albums():
    albums = PhotoAlbum.objects.filter(listable=True).order_by('-event__starts_at')
    c = dict(albums=albums)
    return render_to_string("photo/photo_albums.html", Context(c))

@register.inclusion_tag("contact/contact_form.html", takes_context=True)
def contact_form(context):
    request = context['request']
    if request.POST:
        form = ContactForm(request.POST)
    else:
        form = ContactForm()
    c = dict(form=form)
    return c

@register.simple_tag()
def facebook_like_button():
    return render_to_string("facebook_like.html", Context({}))