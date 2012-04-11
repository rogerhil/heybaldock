from django.core.validators import ValidationError
from django.shortcuts import get_object_or_404

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