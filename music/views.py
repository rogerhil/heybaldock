# -*- coding: utf-8; Mode: Python -*-

import pickle

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.utils import simplejson

from auth.decorators import login_required
from section.decorators import render_to, json
from discogs import Discogs
from forms import RepertoryForm, AlbumInfoForm, AlbumForm, SongForm, \
                  InstrumentForm, PlayerForm, ArtistForm, \
                  PlayerRepertoryItemForm, InstrumentTagTypeForm
from models import Repertory, Song, Album, Artist, RepertoryGroup, \
                   RepertoryGroupItem, Instrument, Player, \
                   InstrumentTagType, PlayerRepertoryItem
from utils import get_or_create_temporary, mzip, str_list_in_list

DISCOGS_PAGES = 500
MAX_YEARS = 10

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
            url = reverse('repertory_details', args=(form.instance.id,))
            return HttpResponseRedirect(url)
    else:
        form = RepertoryForm()
    return dict(form=form)

@login_required
@render_to("music/repertory_details.html")
def repertory_details(request, id):
    if int(id) == 1:
        try:
            repertory = Repertory.get_main_repertory()
        except Repertory.DoesNotExist:
            repertory = Repertory.objects.create(name='Main')
            RepertoryGroup.objects.create(name='Main', repertory=repertory,
                                          order=1)
    else:
        repertory = get_object_or_404(Repertory, id=id)

    groups = repertory.groups.all().order_by('order')
    c = dict(
        repertory=repertory,
        groups=groups,
        players=Player.objects.all()
    )
    return c

@login_required
@json
def add_repertory_group(request, id):
    repertory = Repertory.objects.get(id=id)
    count = repertory.groups.all().count()
    repertory.groups.create(name=request.POST['name'], order=count + 1)
    groups = repertory.groups.all().order_by('order')
    tc = RequestContext(request, dict(groups=groups, repertory=repertory))
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
    tc = RequestContext(request, dict(groups=groups, repertory=repertory))
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
            content=loader.get_template("music/repertory_content.html")\
                          .render(tc)
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
    is_main = int(request.POST['main'])
    group_id = int(request.POST['group_id'])
    def item(s):
        return dict(
            name=str(s.name),
            url=str(s.album.icon_url),
            id=s.id
        )
    main = Repertory.get_main_repertory()
    main_group = main.groups.all()[0]
    if is_main:
        ids = main_group.items.all().values_list('song__id', flat=True)
        songs = Song.objects.filter(name__icontains=name)\
                            .exclude(id__in=ids)[:10]
        songs = [item(s) for s in songs]
    else:
        group = RepertoryGroup.objects.get(id=group_id)
        ids = group.items.all().values_list('song__id', flat=True)
        items = main_group.items.filter(song__name__icontains=name)\
                                .exclude(song__id__in=ids)[:10]
        songs = [item(i.song) for i in items]
    c = dict(
        success=True,
        songs=songs
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

def get_custom_results(request):
    custom = pickle.loads(open('songs.pickle').read())
    #return custom
    data = request.GET
    info = Discogs.get_album_infos(data['artist'], data['album'],
                                   page=data.get('page', 1),
                                   per_page=DISCOGS_PAGES)
    countries = [data['country']]
    all_countries = False
    if data['country'].startswith('All of:'):
        countries = ['US', 'UK', 'Europe', 'UK & Europe']
    elif data['country'].startswith('All countries'):
        all_countries = True
    results = [i for i in info['results'] if i.get('year') and
                      (int(i['year']) >= int(data['from_year']) and
                       int(i['year']) <= (int(data['from_year']) + MAX_YEARS))]
    if not all_countries:
        results = [i for i in results if i['country'] in countries]
    thumbs = []
    album_titles = []
    years = []
    styles = []
    genres = []
    artists = []
    artists_dict = {}
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
        if res['thumb'].find('s.discogs.com') == -1:
            url = get_or_create_temporary(res['thumb'])
            thumbs.append({'title': res['title'], 'url': url})
        album_titles.append(' - '.join(res['title'].split(' - ')[1:]))
        ainfo = Discogs.get_resource(res['resource_url'])
        years.append(res['year'])
        artists += [i['name'] for i in ainfo['artists']]
        for a in ainfo['artists']:
            artists_dict[i['name']] = a
        if ainfo.get('styles'):
            styles += ainfo['styles']
        if ainfo.get('genres'):
            genres += ainfo['genres']
        tracklist = ainfo.get('tracklist')
        if tracklist:
            durations = [i['duration'] for i in tracklist]
            titles = [i['title'] for i in tracklist]
            positions = [i['position'] for i in tracklist]
            composers = [', '.join(set([j['name'] for j in i['extraartists']]))
                                   for i in tracklist if i.get('extraartists')]
            if positions not in songs['hpositions']:
                songs['hpositions'].append(positions)
            if not str_list_in_list(titles, songs['htitles']):
                songs['htitles'].append(titles)
            if all(durations) and durations not in songs['hdurations']:
                songs['hdurations'].append(durations)
            if not str_list_in_list(composers, songs['hcomposers']):
                songs['hcomposers'].append(composers)
                data_composers.append([i['extraartists'] for i in tracklist
                                                     if i.get('extraartists')])

    positions_lengths = set([len(i) for i in songs['hpositions']])
    titles_lengths = set([len(i) for i in songs['htitles']])
    durations_lengths = set([len(i) for i in songs['hdurations']])
    base_lengths = list(positions_lengths.intersection(titles_lengths)
                                         .intersection(durations_lengths))

    songs['hpositions'] = [i for i in songs['hpositions']
                                                    if len(i) in base_lengths]
    songs['htitles'] = [i for i in songs['htitles'] if len(i) in base_lengths]
    songs['hdurations'] = [i for i in songs['hdurations']
                                                    if len(i) in base_lengths]
    songs['hcomposers'] = [i for i in songs['hcomposers']
                                                    if len(i) in base_lengths]
    data_composers = [i for i in data_composers if len(i) in base_lengths]

    songs['json_positions'] = [simplejson.dumps(i)
                                                for i in songs['hpositions']]
    songs['json_durations'] = [simplejson.dumps(i)
                                                for i in songs['hdurations']]
    songs['json_titles'] = [simplejson.dumps(i) for i in songs['htitles']]
    songs['json_composers'] = [simplejson.dumps(i) for i in data_composers]
    songs['positions'] = mzip(songs['hpositions'])
    songs['durations'] = mzip(songs['hdurations'])
    songs['titles'] = mzip(songs['htitles'])
    songs['composers'] = mzip(songs['hcomposers'])

    years = list(set(map(int, years)))[:5]
    years.sort()

    artists = list(set(artists))
    artists.sort()
    artists = [artists_dict[i] for i in artists]

    custom = dict(
        thumbs=thumbs,
        titles=set(album_titles),
        years=years,
        artists=artists,
        styles=set(styles),
        genres=set(genres),
        songs=songs
    )

    open('songs.pickle', 'w').write(pickle.dumps(custom))
    return custom

@login_required
@render_to("music/custom_results.html")
def custom_album_creation(request):
    custom = get_custom_results(request)
    c = dict(custom=custom)
    return c

@login_required
@json
def register_album(request):
    redirect_url = None
    message = ''
    data = request.POST
    adata = {'resource_url': data['artist_resource_url']}
    artist_form = ArtistForm(adata)
    success = artist_form.is_valid()
    artist = artist_form.save()

    if success:
        album_form = AlbumForm(metadata={}, artist=artist, data=data)
        success = album_form.is_valid()
        if success:
            positions = simplejson.loads(data['position'])
            titles = simplejson.loads(data['title'])
            durations = simplejson.loads(data['duration'])
            composers = data.get('composer')
            if composers:
                composers = simplejson.loads(composers)
            forms = []
            for i, position in enumerate(positions):
                d = {
                    'position': position,
                    'name': titles[i],
                    'duration': durations[i],
                    'composer': simplejson.dumps(composers[i]) if composers else ''
                }
                song_form = SongForm(data=d)
                if not song_form.is_valid():
                    success = False
                    break
                forms.append(song_form)
            album = album_form.save()
            for form in forms:
                form.save(album)
            redirect_url = reverse("album", args=(album.id,))
            msg = _('The album was successfully registered.')
            messages.add_message(request, messages.SUCCESS, msg)
        else:
            message = str(album_form.errors)
    else:
        message = str(artist_form.errors)
    c = dict(success=success, redirect_url=redirect_url, message=message)
    return c

@render_to("music/album.html")
def album(request, id):
    album = get_object_or_404(Album, id=id)
    return dict(album=album)

def remove_album(request, id):
    album = get_object_or_404(Album, id=id)
    album.delete()
    msg = _('The album was successfully removed.')
    messages.add_message(request, messages.SUCCESS, msg)
    return HttpResponseRedirect(reverse('albums'))

@render_to("music/albums.html")
def albums(request):
    artists = Artist.objects.all().order_by('name')
    return dict(artists=artists)

@render_to("music/artists.html")
def artists(request):
    artists = Artist.objects.all().order_by('name')
    return dict(artists=artists)

@render_to("music/artist_details.html")
def artist_details(request, id):
    artist = get_object_or_404(Artist, id=id)
    return dict(artist=artist)

@json
def add_song_to_main_repertory(request):
    song = get_object_or_404(Song, id=request.POST['id'])
    main = Repertory.get_main_repertory()
    group = main.groups.all()[0]
    if group.items.filter(song__id=song.id).count():
        msg = _("Song already exist in repertory!")
        return dict(success=False, message=msg)
    count = group.items.all().count()
    item = RepertoryGroupItem.objects.create(group=group, song=song,
                                             number=count + 1)
    group.items.add(item)
    group.save()
    return dict(success=True)

@json
def add_song_to_repertory(request, id, group_id, song_id):
    song = get_object_or_404(Song, id=song_id)
    repertory = get_object_or_404(Repertory, id=id)
    group = repertory.groups.get(id=group_id)
    if group.items.filter(song__id=song.id).count():
        msg = _("Song already exist in repertory!")
        return dict(success=False, message=msg)
    count = group.items.all().count()
    item = RepertoryGroupItem.objects.create(group=group, song=song,
                                             number=count + 1)
    group.items.add(item)
    group.save()
    template = loader.get_template("music/song_line_repertory_content.html")
    c = {
        'item': item,
        'group': group,
        'repertory': repertory
    }
    song_line = template.render(RequestContext(request, c))
    return dict(success=True, song_line=song_line)

@json
def remove_song_from_repertory(request, id, group_id, item_id):
    item = get_object_or_404(RepertoryGroupItem, id=item_id,
                             group__id=group_id, group__repertory__id=id)
    n = item.number
    group = item.group
    item.delete()
    items = group.items.filter(number__gt=n).order_by('number')
    for item in items:
        item.number -= 1
        item.save()
    return dict(success=True)

@login_required
@json
def move_song(request, id, group_id, item_id):
    number = int(request.POST['number'])
    current_item = RepertoryGroupItem.objects.get(id=item_id,
                                                  group__id=group_id,
                                                  group__repertory__id=id)
    group = current_item.group
    repertory = group.repertory
    if current_item.number == number:
        tc = RequestContext(request, dict(group=group, repertory=repertory))
        c = dict(
            success=True,
            content=loader.get_template("music/repertory_group_content.html")\
                          .render(tc)
        )
        return c
    current_number = current_item.number
    current_item.number = -1 # aux
    current_item.save()
    if current_number < number:
        items = group.items.filter(number__lte=number,
                                   number__gt=current_number)\
                           .order_by('number')
        # update number
        for item in items:
            item.number -= 1
            item.save()
    else:
        items = group.items.filter(number__gte=number,
                                   number__lt=current_number)\
                           .order_by('-number')
        # update numbers
        for item in items:
            item.number += 1
            item.save()

    current_item.number = number
    current_item.save()

    tc = RequestContext(request, dict(group=group, repertory=repertory))
    c = dict(
        success=True,
        content=loader.get_template("music/repertory_group_content.html")\
                      .render(tc)
    )
    return c

@login_required
@render_to("music/add_instrument.html")
def add_instrument(request):
    if request.POST:
        form = InstrumentForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            msg = _('The instrument was successfully added.')
            messages.add_message(request, messages.SUCCESS, msg)
            url = reverse('instruments')
            return HttpResponseRedirect(url)
    else:
        form = InstrumentForm
    return dict(form=form)

@json
@login_required
def remove_instrument(request, id):
    instrument = get_object_or_404(Instrument, id=id)
    instrument.delete()
    return dict(success=True)

@render_to("music/instruments.html")
def instruments(request):
    instruments = Instrument.objects.all().order_by('name')
    return dict(instruments=instruments)

@json
@login_required
def add_player(request, id, user_id):
    data = dict(instrument=id, user=user_id)
    form = PlayerForm(data=data)
    user = request.user
    if form.is_valid():
        form.save()
        template = loader.get_template("auth/profile_instruments.html")
        context = RequestContext(request, dict(user=user))
        return dict(success=True, content=template.render(context))
    return dict(success=False)

@json
@login_required
def remove_player(request, id, user_id):
    player = get_object_or_404(Player, id=id, user__id=user_id)
    player.delete()
    return dict(success=True)

@json
@login_required
def players_to_add(request):
    user = request.user
    ids = user.instruments.all().values_list('instrument__id', flat=True)
    instruments = Instrument.objects.all().exclude(id__in=ids)
    template = loader.get_template("auth/profile_add_instruments.html")
    context = RequestContext(request, dict(instruments=instruments))
    return dict(success=True, content=template.render(context))

@json
@login_required
def players_menu(request, id):
    item = get_object_or_404(RepertoryGroupItem, id=id)
    ids = item.players.all().values_list('player__id', flat=True)
    players = Player.objects.all().exclude(id__in=ids)
    if not players.count():
        return dict(success=True, no_players=True)

    members = item.song.album.artist.active_members
    tags = InstrumentTagType.objects.all().order_by('instrument')
    tags_dict = {}
    for tag in tags:
        if not tags_dict.has_key(tag.instrument.id):
            tags_dict[tag.instrument.id] = []
        tags_dict[tag.instrument.id].append(tag)
    for tags in tags_dict.values():
        tags.sort(lambda a, b: 1 if a.level > b.level else -1)

    template = loader.get_template("music/players_menu.html")
    c = dict(
        players=players,
        item=item,
        members=members,
        tags_tuples=tags_dict.items()
    )
    context = RequestContext(request, c)
    return dict(success=True, content=template.render(context))

def player_repertory_item_menu_content(request, player_repertory_item):
    ids = player_repertory_item.tag_types.all().values_list('id', flat=True)
    all_tag_types = InstrumentTagType.objects.filter(
                            instrument=player_repertory_item.player.instrument)
    tag_types = []
    for tag_type in all_tag_types:
        if tag_type.id in ids:
            tag_type.selected = True
        tag_types.append(tag_type)
    template = loader.get_template("music/player_repertory_item_menu.html")
    c = dict(
        player_repertory_item=player_repertory_item,
        tag_types=tag_types
    )
    context = RequestContext(request, c)
    player = dict(
        id=player_repertory_item.id,
        is_lead=player_repertory_item.is_lead
    )
    return dict(content=template.render(context), player=player)

@json
@login_required
def player_repertory_item_menu(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    c = player_repertory_item_menu_content(request, player_repertory_item)
    c['success'] = True
    return c

@json
@login_required
def toogle_tag_type(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    tag_type_id = int(request.POST.get('tag_type_id'))
    tag_type = get_object_or_404(InstrumentTagType, id=tag_type_id)
    ids = player_repertory_item.tag_types.all().values_list('id', flat=True)
    if tag_type_id in ids:
        player_repertory_item.tag_types.remove(tag_type)
    else:
        player_repertory_item.tag_types.add(tag_type)
    player_repertory_item.save()
    c = player_repertory_item_menu_content(request, player_repertory_item)
    c['success'] = True
    return c

@json
@login_required
def change_as_member_options(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    artist = player_repertory_item.repertory_item.song.album.artist
    as_member = player_repertory_item.as_member
    members = [i for i in artist.active_members if i.id != as_member.id]
    template = loader.get_template("music/change_as_member_options.html")
    c = dict(members=members, player_repertory_item=player_repertory_item)
    context = RequestContext(request, c)
    return dict(success=True, content=template.render(context))

@json
@login_required
def change_as_member(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    artist = get_object_or_404(Artist, id=request.POST['member_id'])
    player_repertory_item.as_member = artist
    player_repertory_item.save()
    c = player_repertory_item_menu_content(request, player_repertory_item)
    c['success'] = True
    return c

@json
@login_required
def change_player_user(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    item = player_repertory_item.repertory_item
    player = get_object_or_404(Player, id=request.POST['player_id'])
    current_player = player_repertory_item.player
    # exchange
    other_player_repertory_item = None
    try:
        other_player_repertory_item = item.players.get(player__id=player.id)
    except PlayerRepertoryItem.DoesNotExist:
        pass
    if other_player_repertory_item:
        other_player_repertory_item.player = None
        other_player_repertory_item.save()
    player_repertory_item.player = player
    player_repertory_item.save()
    if other_player_repertory_item:
        other_player_repertory_item.player = current_player
        other_player_repertory_item.save()
    c = player_repertory_item_menu_content(request, player_repertory_item)
    c['success'] = True
    return c

@json
@login_required
def change_player_user_options(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    player = player_repertory_item.player
    players = Player.objects.filter(instrument=player.instrument)\
    .exclude(id=player.id)
    template = loader.get_template("music/change_player_user_options.html")
    c = dict(players=players, player_repertory_item=player_repertory_item)
    context = RequestContext(request, c)
    no_players = not bool(players.count())
    return dict(success=True, content=template.render(context),
                no_players=no_players)

@json
@login_required
def change_notes(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    player_repertory_item.notes = request.POST['notes']
    player_repertory_item.save()
    return dict(success=True)


@json
@login_required
def add_player_repertory_item(request, id, player_id):
    data = request.POST
    data = dict(
        repertory_item=id,
        player=player_id,
        as_member=data.get('member_id') or None,
        tag_types=data.getlist('tag_types[]', [])
    )
    form = PlayerRepertoryItemForm(data=data)
    if form.is_valid():
        form.save()
        item = form.instance.repertory_item
        group = item.group
        repertory = group.repertory
        temp = loader.get_template("music/song_line_repertory_content.html")
        c = {'item': item, 'group': group, 'repertory': repertory}
        content = temp.render(RequestContext(request, c))
        return dict(success=True, content=content)
    return dict(success=False)

@json
@login_required
def remove_player_repertory_item(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    item = player_repertory_item.repertory_item
    group = item.group
    repertory = group.repertory
    player_repertory_item.delete()
    temp = loader.get_template("music/song_line_repertory_content.html")
    c = {'item': item, 'group': group, 'repertory': repertory}
    content = temp.render(RequestContext(request, c))
    return dict(success=True, content=content, item_id=item.id)

@json
@login_required
def player_set_as_lead(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    player_repertory_item.is_lead = bool(int(request.POST.get('is_lead')))
    player_repertory_item.save()
    item = player_repertory_item.repertory_item
    group = item.group
    repertory = group.repertory
    temp = loader.get_template("music/song_line_repertory_content.html")
    c = {'item': item, 'group': group, 'repertory': repertory}
    content = temp.render(RequestContext(request, c))
    return dict(success=True, content=content, item_id=item.id)

@login_required
@render_to("music/add_instrument_tag_type.html")
def add_instrument_tag_type(request):
    if request.POST:
        form = InstrumentTagTypeForm(data=request.POST)
        if form.is_valid():
            form.save()
            msg = _('The instrument tag type was successfully added.')
            messages.add_message(request, messages.SUCCESS, msg)
            url = reverse('instrument_tag_types')
            return HttpResponseRedirect(url)
    else:
        form = InstrumentTagTypeForm
    return dict(form=form)

@login_required
@render_to("music/instrument_tag_types.html")
def instrument_tag_types(request):
    tag_types = InstrumentTagType.objects.all()
    return dict(tag_types=tag_types)
