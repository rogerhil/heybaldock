# -*- coding: utf-8; Mode: Python -*-

from music.models import Band


class MusicMiddleware(object):

    def process_request(self, request):
        """
        """
        request.band = Band.get_active_band(request)
