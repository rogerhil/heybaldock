# -*- coding: utf-8; Mode: Python -*-

from music.models import Band


class MusicMiddleware(object):

    def process_request(self, request):
        """
        """
        request.band = Band.get_active_band(request)
        if not request.band:
            user = request.user
            if user.is_authenticated() and user.bands.count():
                band = user.bands.all()[0]
                Band.set_active_band(request, band)
