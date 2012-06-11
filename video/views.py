from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.validators import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from auth.decorators import login_required
from section.decorators import render_to
from lib.decorators import ajax, required_args
from lib.youtube import youtube_small_info_by_url
from models import VideoAlbum

@render_to("video/video_album_view.html")
def video_album_view(request, id):
    album = get_object_or_404(VideoAlbum, id=id)
    return dict(album=album)

@login_required
@ajax
@required_args('url')
def url_validate_and_details(request):
    url = request.GET['url']

    try:
        info = youtube_small_info_by_url(url)
    except ValidationError, err:
        return {'success': False, 'error': ', '.join(err.messages)}

    info['recorded'] = str(info['recorded'])
    return {'success': True, 'info': info}

@login_required
@require_POST
def delete_video_album(request, id):
    album = get_object_or_404(VideoAlbum, id=id)
    name = album.name
    try:
        album.delete()
        msg = _('The video album "%s" was successfully deleted.' % name)
        messages.add_message(request, messages.SUCCESS, msg)
    except Exception, err:
        msg = _('Error while trying to delete the "%s" video album. %s' % \
                                                                (name, err))
        messages.add_message(request, messages.ERROR, msg)
    url = reverse('section_view', args=('videos',))
    return HttpResponseRedirect(url)