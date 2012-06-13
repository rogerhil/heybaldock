from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from auth.decorators import login_required
from section.decorators import render_to
from lib.decorators import ajax
from models import PhotoAlbum

from image import ImageHandler

@render_to("photo/photo_album_view.html")
def photo_album_view(request, id):
    album = get_object_or_404(PhotoAlbum, id=id)
    return dict(album=album)

@login_required
@ajax
def upload_ajax(request):
    handler = ImageHandler()
    handler.load_by_image_user(request.FILES['image'], request.user)
    handler.save_thumbnails()
    url = handler.url('small')
    url_view = handler.url('big')
    name = handler.original_filename()
    data = {'url': url, 'url_view': url_view, 'name': name}
    return {'success': True, 'data': data}

@login_required
@ajax
def cancel_upload_ajax(request):
    image = request.POST['image']
    handler = ImageHandler()
    handler.load_by_filename_user(image, request.user)
    handler.delete()
    return {'success': True}

@login_required
@require_POST
def delete_photo_album(request, id):
    album = get_object_or_404(PhotoAlbum, id=id)
    name = album.name
    try:
        album.delete()
        msg = _('The photo album "%s" was successfully deleted.' % name)
        messages.add_message(request, messages.SUCCESS, msg)
    except Exception, err:
        args = dict(name=name, err=err)
        msg = _('Error while trying to delete the "%(name)s" ' \
                'photo album. %(err)s' % args)
        messages.add_message(request, messages.ERROR, msg)
    url = reverse('section_view', args=('fotos',))
    return HttpResponseRedirect(url)