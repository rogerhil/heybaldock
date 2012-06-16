from django.conf import settings
from django.shortcuts import render_to_response

IGPATHS = ['media', 'jsi18n', 'auth']

class ComingSoonMiddleware(object):

    def process_response(self, request, response):
        """
        """
        if settings.COMMING_SOON:
            path = request.get_full_path().split('/')[1]
            if path not in IGPATHS:
                if hasattr(request, 'user') and \
                   request.user.is_authenticated():
                    return response
                else:
                    return render_to_response('coming_soon.html')
        return response

class UnderMaintenanceMiddleware(object):

    def process_response(self, request, response):
        """
        """
        if settings.UNDER_MAINTENANCE:
            path = request.get_full_path().split('/')[1]
            if path not in IGPATHS:
                if hasattr(request, 'user') and \
                   request.user.is_authenticated():
                    return response
                else:
                    return render_to_response('under_maintenance.html')
        return response