
from django.db import models
from django.db.models.signals import pre_delete
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from event.models import Location
from photo.image import ImageHandlerUserPhoto


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    friendly_name = models.CharField(_('Friendly Name'), max_length=64,
                                     null=True, blank=True)
    address = models.ForeignKey(Location, verbose_name=_("Location"),
                                null=True, blank=True)
    photo = models.CharField(_("Photo"), max_length=255, null=True, blank=True)
    birth_date = models.DateField(_("Birth Date"), null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)
        self.image_handler = ImageHandlerUserPhoto()
        if self.photo:
            self.image_handler.load(self.photo)

    @property
    def unread_notifications(self):
        return self.user.notifications.filter(read=False)

    @property
    def huge_url(self):
        if self.photo:
            return self.image_handler.url('huge')
        else:
            return "/media/img/user.huge.png"

    @property
    def thumb_url(self):
        if self.photo:
            return self.image_handler.url('thumb')
        else:
            return "/media/img/user.thumb.png"

    @property
    def icon_url(self):
        if self.photo:
            return self.image_handler.url('icon')
        else:
            return "/media/img/user.icon.png"

    @classmethod
    def pre_delete(cls, instance, **kwargs):
        instance.image_handler.delete()


pre_delete.connect(UserProfile.pre_delete, UserProfile)

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
User.nick = property(lambda u: u.profile.friendly_name if
                               u.profile.friendly_name else u.first_name)
