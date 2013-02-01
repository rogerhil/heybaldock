from django import template
from django.contrib.contenttypes.models import ContentType
from django.template.context import Context
from django.template.loader import get_template
from django.utils.translation import ugettext as _

from contact.models import Notification

register = template.Library()

@register.simple_tag()
def notify(instance, action):
    template = get_template("contact/notify_button.html")
    ct = ContentType.objects.get_for_model(type(instance))
    notifications = Notification.objects.filter(content_type=ct,
                                                object_id=instance.id)
    context = dict(
        instance=instance,
        app_label=instance._meta.app_label,
        model_name =instance._meta.module_name,
        action=action,
        notified=bool(notifications.count())
    )
    return template.render(Context(context))
