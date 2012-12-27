# -*- coding: utf-8; Mode: Python -*-

from django.utils import simplejson

from photo.image import ImageHandlerAlbumCoverTemp


def mzip(ll):
    if not ll:
        return ll
    m = max([len(i) for i in ll])
    newl = []
    for i in ll:
        l = i[:]
        dif = (m - len(l))
        if dif:
            l += ['' for i in xrange(dif)]
        newl.append(l)
    newl = zip(*newl)
    mlist = []
    for tup in newl:
        has_difference = len(set(tup)) != 1
        dif = {'has_difference': has_difference}
        mlist.append(dict(
            json_diff=simplejson.dumps(dif), items=tup,
        ))
    return mlist

def str_list_in_list(alist, list_of_lists):
    for l in list_of_lists:
        if map(lambda x: x.strip(), l) == map(lambda x: x.strip(), alist):
            return True
    return False

def get_or_create_temporary(url):
    handler = ImageHandlerAlbumCoverTemp()
    handler.load_by_url(url)
    return handler.url()
  