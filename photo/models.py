import os

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext_lazy as _, ugettext

from event.models import Event
from image import ImageHandler
from signals import photo_post_save, photo_post_delete, photo_album_post_delete


class PhotoAlbum(models.Model):
    """
    """
    name = models.CharField(_("Name"), max_length=64)
    description = models.CharField(_("Description"), max_length=255, null=True)
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    updated = models.DateTimeField(_("Updated"), auto_now=True)
    cover_url = models.CharField(_("Cover url"), max_length=255, null=True)
    count = models.IntegerField(default=0)
    listable = models.BooleanField(default=True, help_text=_('This album will be displayed on the Photos section'))
    event = models.ForeignKey(Event, null=True, blank=True, related_name="photo_albums", help_text=_('In case this album is associated with some event, this field is not required'))
    flyer = models.BooleanField(default=False, help_text=_('These album photos will be displayed on the flyers area of the event'))

    template_view = "photo/album_details.html"
    template_varname = "album"

    def __unicode__(self):
        return ugettext("Photo Album %s" % self.name)

    @staticmethod
    def form():
        from forms import AlbumForm
        return AlbumForm

    def url(self):
        return reverse('photo_album_view', args=(self.id,))

    def update_cover(self):
        photos = self.photos.all().order_by('-id')[:1]
        if photos:
            photo = photos[0]
            self.cover_url = photo.image

    def handler(self):
        handler = ImageHandler()
        handler.load_by_album(self)
        return handler

class Photo(models.Model):
    """
    """
    description = models.CharField(_("Description"), max_length=255, null=True)
    album = models.ForeignKey(PhotoAlbum, verbose_name=_("Album"), related_name='photos')
    date = models.DateField(_("Date"), null=True)
    image = models.CharField(_("Image"), max_length=255)

    def __init__(self, *args, **kwargs):
        super(Photo, self).__init__(*args, **kwargs)
        if not self.album_id:
            return
        self._handler = self.handler()
        urls = self._handler.urls()
        for attr, url in urls.items():
            setattr(self, attr, url)

    def __unicode__(self):
        return ugettext("Photo %s" % self.description)

    def image_url(self, size):
        url = getattr(self, 'image_%s_url' % size, '')
        return url

    def handler(self):
        handler = ImageHandler()
        handler.load_by_filename_album(self.image, self.album)
        return handler

post_save.connect(photo_post_save, sender=Photo)
post_delete.connect(photo_post_delete, sender=Photo)
post_delete.connect(photo_album_post_delete, sender=PhotoAlbum)