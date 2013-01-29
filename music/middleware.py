# -*- coding: utf-8; Mode: Python -*-

from music.models import Band


class MusicMiddleware(object):

    def process_request(self, request):
        """
        """
        request.band = Band.get_active_band(request)
        if not request.band or request.GET.get('update_band_session'):
            user = request.user
            if user.is_authenticated() and user.bands.count():
                band = user.bands.get(name="Hey Baldock")
                Band.set_active_band(request, band)
