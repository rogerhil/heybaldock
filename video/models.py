from django.db import models
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from lib.youtube import youtube_id_by_url
from signals import video_post_save
from event.models import Event

class VideoAlbum(models.Model):
    """
    """
    name = models.CharField(_("Name"), max_length=64)
    description = models.CharField(_("Description"), max_length=255, null=True)
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    updated = models.DateTimeField(_("Updated"), auto_now=True)
    cover_url = models.URLField(_("Url"), null=True)
    count = models.IntegerField(default=0)
    listable = models.BooleanField(default=True, help_text=_('This album will be displayed on the Videos section'))
    event = models.ForeignKey(Event, null=True, blank=True, related_name="video_albums", help_text=_('In case this album is associated with some event, this field is not required'))

    template_view = "video/album_details.html"
    template_varname = "album"

    @staticmethod
    def form():
        from forms import AlbumForm
        return AlbumForm

    def url(self):
        return reverse('video_album_view', args=(self.id,))

    def update_cover(self):
        videos = self.videos.all().order_by('-id')[:1]
        if videos:
            video = videos[0]
            self.cover_url = video.thumbnail_small

class Video(models.Model):
    """
    """
    title = models.CharField(_("Name"), max_length=64)
    description = models.CharField(_("Description"), max_length=255, null=True)
    album = models.ForeignKey(VideoAlbum, verbose_name=_("Album"), related_name='videos')
    recorded = models.DateField(_("Date"), null=True)
    thumbnail = models.URLField(_("Thumbnail"))
    thumbnail_small = models.URLField(_("Small thumbnail"))
    url = models.URLField(_("Url"))

    def embed_code(self):
        id = youtube_id_by_url(self.url)
        code = '<iframe class="youtube-player" type="text/html" ' \
               'width="586" height="360" ' \
               'src="http://www.youtube.com/embed/%s" ' \
               'frameborder="0"></iframe>' % id
        return code

post_save.connect(video_post_save, sender=Video)