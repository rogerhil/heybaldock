# -*- coding: utf-8; Mode: Python -*-

import time

from datetime import datetime
from django.utils.simplejson import loads
from urllib import urlencode, quote_plus
from urllib2 import urlopen
from BeautifulSoup import BeautifulStoneSoup

from music.lyricsdownloader import getlyrics

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


class Lyrics:

    base = "http://api.chartlyrics.com/apiv1.asmx/"

    @staticmethod
    def get_lyrics(artist, song):
        # try first the lyricsdownloader script
        lyrics = getlyrics(artist, song)
        if lyrics:
            return '\n'.join(lyrics)
        else:
            # disabling api chartlyrics for a while
            return
        action = "SearchLyric"
        p = lambda x: quote_plus(x)
        params = "artist=%s&song=%s" % (p(artist), p(song))
        url = "%s%s?%s" % (Lyrics.base, action, params)
        response = None
        while not response:
            try:
                response = urlopen(url)
            except:
                time.sleep(1)
        xml = response.read()
        soup = BeautifulStoneSoup(xml)
        results = soup.findAll("searchlyricresult")
        lyrics = None
        time.sleep(10)
        for result in results:
            ln = result.findAll('song')[0].text.lower().strip()
            if song.lower().strip() == ln:
                id = result.findAll('lyricid')[0].text
                cksum = result.findAll('lyricchecksum')[0].text
                action = "GetLyric"
                params = "lyricId=%s&lyricCheckSum=%s" % (id, cksum)
                url = "%s%s?%s" % (Lyrics.base, action, params)
                response = None
                tries = 0
                while not response:
                    try:
                        tries += 1
                        response = urlopen(url, timeout=5)
                    except Exception, err:
                        time.sleep(1)
                xml = response.read()
                soup = BeautifulStoneSoup(xml)
                lyrics = soup.findAll('lyric')[0].text
                break
        return lyrics
