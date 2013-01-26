from django.db import models
from django.contrib.auth.models import User

from event.models import Location


class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True)
    address = models.ForeignKey(Location, null=True, blank=True)
    photo = models.CharField(max_length=255)
    birthdate = models.DateField(null=True, blank=True)


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
