import re

from django.db.models import Q
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.template.defaultfilters import striptags

from event.models import Event, Location
from photo.models import PhotoAlbum, Photo
from section.decorators import render_to
from section.models import Section
from video.models import VideoAlbum, Video

pos = lambda x: 0 if x < 0 else x

LIMIT = 50

class Search(object):

    def __init__(self, model):
        self.model = model
        self.query = ''
        self.query_list = []

    def search(self, query):
        self.query = query
        self.query_list = [i.strip() for i in query.split(' ')]
        s = getattr(self, "_%s_search" % self.model._meta.module_name)
        res = []
        for q in self.query_list:
            res += s(q)
        return res

    def _get_summary(self, obj, field):
        summary = []
        fdepth = field.split('__')
        o = obj
        for f in fdepth:
            o = getattr(o, f)
        cont = striptags(o)
        for q in self.query_list:
            match = re.search(q, cont, flags=re.IGNORECASE)
            if match:
                contindex = match.start()
                summary.append(cont[pos(contindex - LIMIT):contindex + LIMIT])
        return summary

    def _new_item(self, obj, field):
        fields = field if isinstance(field, list) else [field]
        summary = []
        for f in fields:
            summary += self._get_summary(obj, f)
        image_url = ''
        if not hasattr(obj, 'url') or isinstance(obj.url, unicode):
            url = obj.album.url()
            if isinstance(obj, Video):
                image_url = obj.thumbnail_small
            elif isinstance(obj, Photo):
                image_url = obj.image_small_url
        else:
            url = obj.url()
            if isinstance(obj, VideoAlbum) or isinstance(obj, PhotoAlbum):
                image_url = obj.cover_url
            if isinstance(obj, Event):
                flyers = obj.flyers
                if flyers:
                    image_url = flyers[0].cover_url
        item = {
            'title': str(obj),
            'summary': ["... %s ..." % i for i in summary],
            'url': url,
            'image_url': image_url
        }
        return item

    def _section_search(self, query):
        items = self.model.objects.filter(content__contains=query)
        return [self._new_item(i, 'content') for i in items]

    def _event_search(self, query):
        items = self.model.objects.filter(Q(name__contains=query) | \
                                  Q(location__name__contains=query) | \
                                  Q(location__description__contains=query) | \
                                  Q(location__street__contains=query) | \
                                  Q(location__district__contains=query) | \
                                  Q(location__city__contains=query))
        fields = ['name', 'location__name', 'location__description',
                  'location__street', 'location__district', 'location__city']
        return [self._new_item(i, fields) for i in items]

    def _location_search(self, query):
        items = self.model.objects.filter(Q(name__contains=query) | \
                                          Q(description__contains=query) | \
                                          Q(street__contains=query) | \
                                          Q(district__contains=query) | \
                                          Q(city__contains=query))
        return [self._new_item(i, ['name', 'location__name']) for i in items]

    def _photoalbum_search(self, query):
        items = self.model.objects.filter(Q(name__contains=query) | \
                                          Q(event__name__contains=query) | \
                                    Q(event__location__name__contains=query))
        fields = ['name', 'event__name', 'event__location__name']
        return [self._new_item(i, fields) for i in items]

    def _photo_search(self, query):
        items = self.model.objects.filter(description__contains=query)
        return [self._new_item(i, 'description') for i in items]

    def _video_search(self, query):
        items = self.model.objects.filter(Q(title__contains=query) | \
                                          Q(description__contains=query))
        return [self._new_item(i, ['title', 'description']) for i in items]

    def _videoalbum_search(self, query):
        return self._photoalbum_search(query)

@render_to("search/search.html")
def search(request):
    query = request.GET.get('query', '').strip()
    if query:
        items = Search(Section).search(query)
        items += Search(Event).search(query)
        items += Search(Location).search(query)
        items += Search(PhotoAlbum).search(query)
        items += Search(Photo).search(query)
        items += Search(VideoAlbum).search(query)
        items += Search(Video).search(query)
        count = len(items)
    else:
        items = []
        count = 0
    result = {
        'items': items,
        'count': count
    }
    return dict(result=result, query=query)