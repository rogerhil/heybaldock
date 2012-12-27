# -*- coding: utf-8; Mode: Python -*-

from datetime import datetime
from django.utils.simplejson import loads
from urllib import urlencode, urlopen

class Discogs:

    SEARCH_URL = 'http://api.discogs.com/database/search'

    @staticmethod
    def get_album_infos(artist, album, per_page=20, page=1):
        params = [
            ('release_title', album),
            ('artist', artist),
            ('type', 'release'),
            ('per_page', per_page),
            ('page', page)
        ]
        url = "%s?%s" % (Discogs.SEARCH_URL, urlencode(params))
        response = urlopen(url)
        content = response.read()
        info = loads(content)
        return info

    @staticmethod
    def get_resource(resource_url):
        resource = loads(urlopen(resource_url).read())
        #if resource['tracklist'] and \
        #   resource['tracklist'][0]['duration']:
        #    return resource
        return resource

    @staticmethod
    def get_tracklist(resource_url):
        conv = lambda x: datetime.strptime(x, '%M:%S')
        tosec = lambda x: conv(x) - conv('0:0')
        resource = loads(urlopen(resource_url).read())
        tracklist = resource['tracklist']
        for item in tracklist:
            tracklist['duration'] = tosec(item['duration'])
        return tracklist