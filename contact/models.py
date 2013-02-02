# -*- coding: utf-8; Mode: Python -*-

from south.modelsinspector import add_introspection_rules

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template import loader, Context
from django.utils.translation import ugettext as _, ugettext_lazy as l_

from lib.fields import PickleField
from contact.mail import send_mail

add_introspection_rules([], ["^lib\.fields\.PickleField"])


class Notification(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    email_sent = models.BooleanField(default=False)
    subject = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    template = models.CharField(max_length=128, null=True, blank=True)
    template_context = PickleField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField(null=True)
    action = models.CharField(max_length=32, null=True, blank=True)
    object = generic.GenericForeignKey()

    _notifications = {
        'event.event': {
            'created': {
                'subject': _("Show %(instance)s"),
                'template': 'event/notification/event_created.html'
            },
            'published': {
                'subject': _("Show %(instance)s has been published"),
                'template': 'event/notification/event_published.html'
            },
            'changed': {
                'subject': _("Show %(instance)s has been changed"),
                'template': 'event/notification/event_published.html'
            }
        },
        'music.rehearsal': {
            'created': {
                'subject': _("%(instance)s"),
                'template': 'music/notification/rehearsal_created.html'
            },
            'changed': {
                'subject': _("%(instance)s has been changed"),
                'template': 'music/notification/rehearsal_changed.html'
            },
        },
        'music.event repertory': {
            'created': {
                'subject': _("%(instance)s"),
                'template': 'music/notification/event_repertory_created.html'
            },
            'changed': {
                'subject': _("%(instance)s has been changed"),
                'template': 'music/notification/event_repertory_changed.html'
            },
            'rate_reminder': {
                'subject': _("Rate the songs of %(instance)s"),
                'template': 'music/notification/rehearsal_rate_reminder.html'
            }
        }
    }

    def __unicode__(self):
        return "%s (%s)" % (self.subject, self.date)

    def message(self, extra_context=None):
        context = Context(self.context)
        if extra_context:
            context.update(extra_context)
        template = loader.get_template(self.template)
        return template.render(context)

    def subject_formatted(self, extra_context=None):
        context = Context(self.context)
        if extra_context:
            context.update(extra_context)
        return self.subject % context

    @property
    def context(self):
        return self.get_template_context_object()

    @property
    def times_notified(self):
        times = Notification.objects.filter(
            content_type=self.content_type,
            object_id=self.object_id
        ).count()
        return times

    @property
    def has_notified(self):
        return bool(self.users_notifications.all().count())

    @property
    def has_notified_twice(self):
        return self.times_notified == 2

    def send_mails(self):
        for user_notification in self.users_notifications.all():
            user_notification.send_mail()
        self.email_sent = True
        self.save()

    def mark_as_read(self):
        self.read = True
        self.save()

    def mark_as_unread(self):
        self.read = True
        self.save()

    def notify_users(self, users):
        for user in users:
            UserNotification.objects.create(user=user, notification=self)

    def get_data(self):
        ct = self.content_type
        action = self.action
        key = "%s.%s" % (ct.app_label, ct.name)
        data = self._notifications[key].get(action)
        return data

    @classmethod
    def notify(cls, instance, action, users, context=None, notes=None,
               mail=True):
        ct = ContentType.objects.get_for_model(type(instance))
        data = cls._notifications["%s.%s" % (ct.app_label, ct.name)][action]
        notification = cls.objects.create(
            content_type=ct,
            object_id=instance.id,
            notes=notes,
            template=data['template'],
            subject=data['subject'],
            action=action
        )
        template_context = dict(
            instance=instance,
            notification=notification,
            site_url=settings.SITE_URL
        )
        if context is not None:
            template_context.update(context)
        notification.set_template_context_object(template_context)
        notification.save()
        notification.notify_users(users)
        if mail:
            notification.send_mails()


class UserNotification(models.Model):
    notification = models.ForeignKey(Notification,
                                     related_name="users_notifications")
    user = models.ForeignKey(User, related_name="notifications")
    read = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s to %s" % (self.notification, self.user)

    @property
    def message(self):
        return self.notification.message(dict(user=self.user))

    @property
    def email_message(self):
        template = loader.get_template("contact/email_base.html")
        return template.render(Context(dict(content=self.message)))

    @property
    def subject(self):
        return self.notification.subject_formatted()

    def send_mail(self):
        send_mail(self.subject, self.email_message, self.user.email, html=True)
        self.email_sent = True
        self.save()

    def mark_as_read(self):
        self.read = True
        self.save()

    def mark_as_unread(self):
        self.read = True
        self.save()
