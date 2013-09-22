# -*- coding: utf-8; Mode: Python -*-

import os
import string
from random import shuffle

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
    handler.save()
    return handler.single_url()

def generate_key(size=20):
    letters = [i for i in (string.ascii_lowercase + string.digits)]
    letters += letters
    letters += letters
    shuffle(letters)
    return ''.join(letters[:size])

def generate_filename(filename, base_size=20):
    name, ext = os.path.splitext(filename)
    name = name.replace(' ', '-')
    key = generate_key(base_size)
    return "%s_%s%s" % (name, key, ext)

def pretty_items(r, d,
       nametag=lambda x: "<strong>%s: </strong>" % x.replace('_', ' ').title(),
       itemtag=lambda x: '<li>%s</li>' % x, valuetag=lambda x: "%s" % x,
       listitemvaluetag=lambda x: '<li class="list_value">%s</li>' % x,
       blocktag=('<ul>', '</ul>'), ignorekeys=None):
    if ignorekeys is None:
        ignorekeys = []
    if isinstance(d, dict):
        r.append(blocktag[0])
        for k, v in d.iteritems():
            if k in ignorekeys:
                continue
            name = nametag(k)
            if isinstance(v, dict) or isinstance(v, list):
                r.append(itemtag(name))
                pretty_items(r, v, nametag, itemtag, valuetag,
                             listitemvaluetag, blocktag,
                             ignorekeys=ignorekeys or None)
            else:
                value = valuetag(unicode(v))
                r.append(itemtag(name + value))
        r.append(blocktag[1])
    elif isinstance(d, list):
        r.append(blocktag[0])
        for i in d:
            if isinstance(i, dict) or isinstance(i, list):
                if isinstance(i, dict):
                    for ig in ignorekeys:
                        if i.has_key(ig):
                            del i[ig]
                    if len(i.keys()) > 1:
                        pretty_items(r, i, nametag, itemtag, valuetag,
                                     listitemvaluetag, blocktag,
                                     ignorekeys=ignorekeys or None)
                    elif len(i.keys()) == 1:
                        value = valuetag(i.values()[0])
                        r.append(listitemvaluetag(value))
                else:
                    pretty_items(r, i, nametag, itemtag, valuetag,
                                 listitemvaluetag, blocktag,
                                 ignorekeys=ignorekeys or None)
            else:
                value = valuetag(unicode(i))
                r.append(listitemvaluetag(value))
        r.append(blocktag[1])

def metadata_display(metadata):
    r = []
    def valuetag(x):
        if isinstance(x, basestring) and x.strip().startswith('http://'):
            return '<a href="%s" target="_blank">%s</a>' % (x, x)
        else:
            return x
    ignorekeys = ['resource_url', 'id', 'releases_url', 'active']
    pretty_items(r, metadata, ignorekeys=ignorekeys, valuetag=valuetag)
    return '\n'.join(r)

def chunks(alist, n):
    """ Creates a generator for partitions of lists with length n.
    >>> chunks(range(15), 3)
    <generator object chunks at 0x100594f50>
    >>> list(chunks(range(15), 3))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11], [12, 13, 14]]
    """
    for i in xrange(0, len(alist), n):
        yield alist[i:i+n]