# -*- coding: utf-8; Mode: Python -*-

import pickle

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.utils import simplejson

from auth.decorators import login_required
from section.decorators import render_to, json

from discogs import Discogs
from forms import RepertoryForm, AlbumInfoForm, AlbumForm, ArtistForm, SongForm
from models import Repertory, Song


@login_required
@render_to("music/repertories.html")
def repertories(request):
    repertories = Repertory.objects.filter(event__isnull=False)
    return dict(repertories=repertories)

@login_required
@render_to("music/add_repertory.html")
def add_repertory(request):
    if request.POST:
        form = RepertoryForm(request.POST)
        if form.is_valid():
            form.save()
            msg = _('The repertory was successfully added.')
            messages.add_message(request, messages.SUCCESS, msg)
            return HttpResponseRedirect(reverse('repertories'))
    else:
        form = RepertoryForm()
    return dict(form=form)

@login_required
@render_to("music/repertory_details.html")
def repertory_details(request, id):
    repertory = get_object_or_404(Repertory, id=id)
    groups = repertory.groups.all().order_by('order')
    c = dict(
        repertory=repertory,
        groups=groups
    )
    return c

@login_required
@json
def add_repertory_group(request, id):
    repertory = Repertory.objects.get(id=id)
    count = repertory.groups.all().count()
    repertory.groups.create(name=request.POST['name'], order=count + 1)
    groups = repertory.groups.all().order_by('order')
    tc = RequestContext(request, dict(groups=groups))
    c = dict(
        success=True,
        content=loader.get_template("music/repertory_content.html").render(tc)
    )
    return c

@login_required
@json
def remove_repertory_group(request, id, group_id):
    repertory = Repertory.objects.get(id=id)
    group = repertory.groups.get(id=group_id)
    group.delete()
    groups = repertory.groups.filter(order__gt=group.order).order_by('order')
    # update orders
    for group in groups:
        group.order -= 1
        group.save()
    groups = repertory.groups.all().order_by('order')
    tc = RequestContext(request, dict(groups=groups))
    c = dict(
        success=True,
        content=loader.get_template("music/repertory_content.html").render(tc)
    )
    return c

@login_required
@json
def move_repertory_group(request, id, group_id):
    repertory = Repertory.objects.get(id=id)
    order = int(request.POST['order'])
    current_group = repertory.groups.get(id=group_id)
    if current_group.order == order:
        groups = repertory.groups.all().order_by('order')
        tc = RequestContext(request, dict(groups=groups))
        c = dict(
            success=True,
            content=loader.get_template("music/repertory_content.html").render(tc)
        )
        return c
    current_order = current_group.order
    current_group.order = -1 # aux
    current_group.save()
    if current_order < order:
        groups = repertory.groups.filter(order__lte=order,
                              order__gt=current_order).order_by('order')
        # update orders
        for group in groups:
            group.order -= 1
            group.save()
    else:
        groups = repertory.groups.filter(order__gte=order,
                              order__lt=current_order).order_by('-order')
        # update orders
        for group in groups:
            group.order += 1
            group.save()

    current_group.order = order
    current_group.save()

    groups = repertory.groups.all().order_by('order')
    tc = RequestContext(request, dict(groups=groups))
    c = dict(
        success=True,
        content=loader.get_template("music/repertory_content.html").render(tc)
    )
    return c

@login_required
@json
def search_song_by_name(request):
    name = request.POST['name']
    db_songs = Song.objects.filter(name__icontains=name)
    discogs_songs = Discogs
    c = dict(
        success=True,
        db_songs=songs
    )
    return c

@login_required
@render_to("music/music_management.html")
def music_management(request):

    c = dict(
    )
    return c

@login_required
@render_to("music/add_album.html")
def add_album(request):
    c = dict(form=AlbumInfoForm())
    return c

@login_required
@json
def register_album(request):
    url = request.POST['resource_url']
    info = Discogs.get_resource(url)
    catno = info['labels'][0]['catno'] if info['labels'] else ''
    description = info['notes']
    artist_info = info['artists'][0]
    artist_metadata = Discogs.get_resource(artist_info['resource_url'])
    artist_data = dict(
        discogsid=artist_info['id'],
        name=artist_info['name'],
    )
    form = ArtistForm(metadata=artist_metadata, data=artist_data)
    if not form.is_valid():
        c = dict(
            success=False,
            errors=form.errors,
        )
        return c
    #artist = form.save()
    data = dict(
        discogsid=info['id'],
        catno=catno,
        name=info['title'],
        description=description,
        #artist=artist.id,
        artist=1,
        thumb=info['thumb'],
        uri=info['uri'],
        year=info['year'],
    )
    form = AlbumForm(metadata=info, data=data)
    if not form.is_valid():
        c = dict(
            success=False,
            errors=form.errors,
        )
        return c
    #album = form.save()

    for track in info['tracklist']:
        for k, v in track.items():
            if isinstance(v, list):
                print k
                for d in v:
                    print
                    for k1, v1 in d.items():
                        print "    %s: %s" % (k1, v1)
            else:
                print "%s: %s" % (k, v)
        #form = SongForm(data=)

    c = dict(success=True)
    return c


@login_required
@render_to("music/albums_results.html")
def search_albums(request):
    data = request.GET
    track_list_enumeration = int(data['track_list_enumeration'])
    composers_info = int(data['composers_info'])
    info = Discogs.get_album_infos(data['artist'], data['album'],
                                   page=data.get('page', 1), per_page=500)
    results = []
    countries = [data['country']]
    all_countries = False
    if data['country'].startswith('All of:'):
        countries = ['US', 'UK', 'Europe', 'UK & Europe']
    elif data['country'].startswith('All countries'):
        all_countries = True

    for res in info['results']:
        if not all_countries and res['country'].strip() not in countries:
            continue
        if not res.get('year'):
            continue
        if res['year'] < data['from_year'] or res['year'] > data['till_year']:
            continue
        ainfo = Discogs.get_resource(res['resource_url'])
        tracklist = ainfo['tracklist']
        if composers_info and not tracklist[0].get('extraartists'):
            continue
        if track_list_enumeration and not tracklist[0].get('duration'):
            continue
        results.append(res)
    info['results'] = results
    #urls = info['pagination']['urls'].has_key
    #page = info['pagination']['page']
    #pages = info['pagination']['pages']
    #info['pagination']['next'] = urls('next') and page + 1 or None
    #info['pagination']['prev'] = urls('prev') and page - 1 or None
    #info['pagination']['first'] = urls('first') and 1 or None
    #info['pagination']['last'] = urls('last') and pages or None
    #info['pagination']['pages'] = range(1, info['pagination']['pages'] + 1)
    c = dict(info=info, occurrences=len(results))
    return c

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

@login_required
@render_to("music/custom_results.html")
def custom_album_creation(request):
    custom = pickle.loads(open('songs.pickle').read())
    return dict(custom=custom)
    data = request.GET
    info = Discogs.get_album_infos(data['artist'], data['album'],
                                   page=data.get('page', 1), per_page=500)
    countries = [data['country']]
    all_countries = False
    if data['country'].startswith('All of:'):
        countries = ['US', 'UK', 'Europe', 'UK & Europe']
    elif data['country'].startswith('All countries'):
        all_countries = True
    results = [i for i in info['results'] if i.get('year') and (i['year'] < data['from_year'] or i['year'] > data['till_year'])]
    if not all_countries:
        results = [i for i in info['results'] if i['country'] in countries]

    thumbs = []
    album_titles = []
    songs = dict(
        positions=[],
        titles=[],
        durations=[],
        composers=[],
        hpositions=[],
        htitles=[],
        hdurations=[],
        hcomposers=[]
    )

    data_composers = []
    for res in results:
        thumbs.append({'title': res['title'], 'url': res['thumb']})
        album_titles.append(res['title'])
        ainfo = Discogs.get_resource(res['resource_url'])
        tracklist = ainfo.get('tracklist')
        if tracklist and all([i.get('extraartists') for i in tracklist]):
            durations = [i['duration'] for i in tracklist]
            titles = [i['title'] for i in tracklist]
            positions = [i['position'] for i in tracklist]
            composers = [', '.join(set([j['name'] for j in i['extraartists']])) for i in tracklist]
            if positions not in songs['hpositions']:
                songs['hpositions'].append(positions)
            if not str_list_in_list(titles, songs['htitles']):
                songs['htitles'].append(titles)
            if all(durations) and durations not in songs['hdurations']:
                songs['hdurations'].append(durations)
            if not str_list_in_list(composers, songs['hcomposers']):
                songs['hcomposers'].append(composers)
                data_composers.append([i['extraartists'] for i in tracklist])

    positions_lengths = set([len(i) for i in songs['hpositions']])
    titles_lengths = set([len(i) for i in songs['htitles']])
    durations_lengths = set([len(i) for i in songs['hdurations']])
    base_lengths = list(positions_lengths.intersection(titles_lengths).intersection(durations_lengths))

    songs['hpositions'] = [i for i in songs['hpositions'] if len(i) in base_lengths]
    songs['htitles'] = [i for i in songs['htitles'] if len(i) in base_lengths]
    songs['hdurations'] = [i for i in songs['hdurations'] if len(i) in base_lengths]
    songs['hcomposers'] = [i for i in songs['hcomposers'] if len(i) in base_lengths]


    songs['json_positions'] = [simplejson.dumps(i) for i in songs['hpositions']]
    songs['json_durations'] = [simplejson.dumps(i) for i in songs['hdurations']]
    songs['json_titles'] = [simplejson.dumps(i) for i in songs['htitles']]
    songs['json_composers'] = [simplejson.dumps(i) for i in data_composers]
    songs['positions'] = mzip(songs['hpositions'])
    songs['durations'] = mzip(songs['hdurations'])
    songs['titles'] = mzip(songs['htitles'])
    songs['composers'] = mzip(songs['hcomposers'])

    custom = dict(
        thumbs=thumbs,
        titles=set(album_titles),
        songs=songs
    )
    open('songs.pickle', 'w').write(pickle.dumps(custom))
    c = dict(custom=custom)
    return c

def get_album_resource(request):
    url = request.GET['resource_url']
    info = Discogs.get_resource(url)
    c = dict(info=info, resource_url=url)
    c = RequestContext(request, c)
    return render_to_response("music/album_info_results.html", c)

def repertoire_include(request):
    data = request.GET
    if data.get('repertoire_id'):
        repertoire = Repertoire.objects.get(id=data['repertoire_id'])
    elif data.get('repertoire_name'):
        repertoire = Repertoire.objects.create(name=data['repertoire_name'])
    tracklist = Discogs.get_tracklist(data['resource_url'])
    for item in tracklist:
         RepertoireItem.objects.create()
