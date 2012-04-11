from datetime import datetime
from urllib2 import urlparse
from gdata.youtube.service import YouTubeService
from gdata.service import RequestError

from django.core.validators import URLValidator, ValidationError
from django.utils.translation import ugettext as _

service = YouTubeService()

def youtube_id_by_url(url):
    validator = URLValidator()
    try:
        validator(url)
    except ValidationError:
        msg = _("Please provide a valid url")
        raise ValidationError(msg)
    parsed = urlparse.urlparse(url)
    if 'youtube' not in parsed.netloc and \
       'y2u.be' not in parsed.netloc:
        msg = _("Only youtube videos are allowed.")
        raise ValidationError(msg)

    qs = urlparse.parse_qs(parsed.query)
    if 'v' not in qs and not qs['v']:
        msg = _("Invalid youtube video url.")
        raise ValidationError(msg)
    id = qs['v'][0]
    return id

def youtube_entry(id):
    """
    """
    entry = service.GetYouTubeVideoEntry(video_id=id)
    return entry

def validate_youtube_url(url):
    """
    """
    id = youtube_id_by_url(url)
    try:
        info = youtube_small_info(id)
    except RequestError:
        msg = _("Invalid youtube video url.")
        raise ValidationError(msg)
    return info

def youtube_small_info(id):
    """
    """
    entry = youtube_entry(id)
    date = lambda d: datetime.strptime(d, '%Y-%m-%d')
    recorded = entry.recorded and date(entry.recorded.text) or None
    d = {'title': entry.title.text,
         'description': entry.media.description.text,
         'url': 'http://www.youtube.com/watch?v=%s' % id,
         'recorded': recorded,
         'thumbnail': entry.media.thumbnail[0].url,
         'thumbnail_small': entry.media.thumbnail[1].url}
    return d

def youtube_small_info_by_url(url):
    id = youtube_id_by_url(url)
    return youtube_small_info(id)