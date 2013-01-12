# -*- coding: utf-8; Mode: Python -*-

import decimal
import pickle
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.utils import simplejson

from auth.decorators import login_required
from section.decorators import render_to, json
from discogs import Discogs
from photo.image import FileHandlerSongAudio
from forms import RepertoryForm, AlbumInfoForm, AlbumForm, SongForm, \
                  InstrumentForm, PlayerForm, ArtistForm, \
                  PlayerRepertoryItemForm, InstrumentTagTypeForm, \
                  DocumentPlayerRepertoryItemForm, BandForm, RehearsalForm
from models import Repertory, Song, Album, Artist, RepertoryGroup, \
                   RepertoryGroupItem, Instrument, Player, \
                   InstrumentTagType, PlayerRepertoryItem, \
                   MusicHistoryChanges, UserRepertoryItemRating, \
                   PlayerRepertoryItemRating, Band, BandArtist, Rehearsal
from decorators import ajax_check_locked_repertory, check_locked_repertory, \
                       ajax_check_locked_repertory_item, \
                       ajax_check_locked_player_repertory_item, \
                       ajax_check_locked_main_repertory

from event.models import Event
from utils import get_or_create_temporary, mzip, str_list_in_list, \
                  generate_filename
from defaults import Tempo, Tonality, SongMode, TimeDuration

DISCOGS_PAGES = 500
MAX_YEARS = 30

def new_history_entry(user, instance, action, summary=''):
    content_type = ContentType.objects.get_for_model(type(instance))
    summary = '%s "%s (%s)" %s. %s' % (content_type, instance,
                                       instance.id, action, summary)
    history = MusicHistoryChanges.objects.create(
        content_type=content_type,
        object_id=instance.id,
        user=user,
        summary=summary
    )
    return history

@login_required
@render_to("music/repertories.html")
def repertories(request):
    repertories = Repertory.objects.filter(event__isnull=False)
    main_repertory = Repertory.get_main_repertory()
    return dict(repertories=repertories, main_repertory=main_repertory)

@login_required
@render_to("music/band_settings.html")
def band_settings(request, id):
    band = get_object_or_404(Band, id=id)
    if request.POST:
        form = BandForm(data=request.POST, instance=band)
        if form.is_valid():
            band = form.save(commit=False)
            band.save()
            band.artists.clear()
            for artist in form.cleaned_data.get('artists'):
                band_artist = BandArtist(band=band, artist=artist)
                band_artist.save()
            band.members.clear()
            for member in form.cleaned_data.get('members'):
                band.members.add(member)
            Band.set_active_band(request, band)
            new_history_entry(request.user, form.instance, 'created')
            msg = _('The band settings was successfully changed.')
            messages.add_message(request, messages.SUCCESS, msg)
            url = reverse('band_settings', args=(form.instance.id,))
            return HttpResponseRedirect(url)
    else:
        form = BandForm(instance=band)
    return dict(band=band, form=form)

@login_required
@render_to("music/add_band.html")
def add_band(request):
    if request.POST:
        form = BandForm(request.POST)
        if form.is_valid():
            band = form.save(commit=False)
            band.save()
            for artist in form.cleaned_data.get('artists'):
                band_artist = BandArtist(band=band, artist=artist)
                band_artist.save()
            for member in form.cleaned_data.get('members'):
                band.members.add(member)
            new_history_entry(request.user, form.instance, 'created')
            msg = _('The band was successfully added.')
            messages.add_message(request, messages.SUCCESS, msg)
            url = reverse('band_settings', args=(form.instance.id,))
            return HttpResponseRedirect(url)
    else:
        form = BandForm()
    return dict(form=form)

@login_required
@render_to("music/rehearsals.html")
def rehearsals(request):
    now = datetime.now()
    upcoming = Rehearsal.objects.filter(date__gte=now)
    past = Rehearsal.objects.filter(date__lte=now)
    return dict(upcoming=upcoming, past=past)

def get_rehearsal_abscence_payers(band):
    payers = []
    values = []
    for user in band.active_members:
        count = Rehearsal.objects.filter(paid_by=user).exclude(cost=None)\
                                 .exclude(cost=decimal.Decimal()).count()
        values.append(count)
        payers.append((count, user))
    abscence_payers = []

    for count, payer in payers:
        if count < max(values):
            abscence_payers.append((payer, max(values) - count))
    abscence_payers = ", ".join(["%s (%s)" % (p.first_name, c) for p, c in
                                 abscence_payers])
    return abscence_payers

@login_required
@render_to("music/add_rehearsal.html")
def add_rehearsal(request):
    user = request.user
    band = Band.get_active_band(request)
    if request.POST:
        data = request.POST
        form = RehearsalForm(band=band, data=data)
        if form.is_valid():
            form.save()
            msg = _("The rehearsal was successfully created.")
            new_history_entry(user, form.instance, 'created')
            messages.add_message(request, messages.SUCCESS, msg)
            url = reverse("rehearsal", args=(form.instance.id,))
            return HttpResponseRedirect(url)
    else:
        form = RehearsalForm(band=band)
    abscence_payers = get_rehearsal_abscence_payers(band)
    return dict(form=form, abscence_payers=abscence_payers)

@login_required
@render_to("music/rehearsal.html")
def rehearsal(request, id):
    rehearsal = get_object_or_404(Rehearsal, id=id)
    return dict(rehearsal=rehearsal)

@login_required
def remove_rehearsal(request, id):
    user = request.user
    rehearsal = get_object_or_404(Rehearsal, id=id)
    rehearsal.delete()
    msg = _("The rehearsal was successfully removed.")
    new_history_entry(user, rehearsal, 'removed')
    messages.add_message(request, messages.SUCCESS, msg)
    return HttpResponseRedirect(reverse("rehearsals"))

@login_required
@render_to("music/add_rehearsal.html")
def change_rehearsal(request, id):
    user = request.user
    band = Band.get_active_band(request)
    rehearsal = get_object_or_404(Rehearsal, id=id)
    if request.POST:
        data = request.POST
        form = RehearsalForm(band=band, data=data, instance=rehearsal)
        if form.is_valid():
            form.save()
            msg = _("The rehearsal was successfully modified.")
            new_history_entry(user, form.instance, 'changed')
            messages.add_message(request, messages.SUCCESS, msg)
            url = reverse("rehearsal", args=(form.instance.id,))
            return HttpResponseRedirect(url)
    else:
        form = RehearsalForm(band=band, instance=rehearsal)
    abscence_payers = get_rehearsal_abscence_payers(band)
    return dict(form=form, abscence_payers=abscence_payers, change=True)

@login_required
@render_to("music/add_repertory.html")
def add_repertory(request):
    initial = {'band': request.band}
    if request.POST:
        form = RepertoryForm(request.POST, initial=initial)
        if form.is_valid():
            form.save()
            if not form.instance.band:
                form.instance.band = request.band
                form.instance.save()
            if request.POST.get('mode') == 'based_on_repertory':
                id = int(request.POST['repertory_based'])
                based_rep = Repertory.objects.get(id=id)
                form.instance.import_items_from(based_rep)
            new_history_entry(request.user, form.instance, 'created')
            msg = _('The repertory was successfully added.')
            messages.add_message(request, messages.SUCCESS, msg)
            url = reverse('repertory_details', args=(form.instance.id,))
            return HttpResponseRedirect(url)
    else:
        form = RepertoryForm(initial=initial)
    repertories = Repertory.objects.all().exclude(name='Main')
    return dict(form=form, repertories=repertories)

@login_required
@render_to("music/repertory_details.html")
def repertory_details(request, id):
    user = request.user
    if int(id) == 1:
        try:
            repertory = Repertory.get_main_repertory()
        except Repertory.DoesNotExist:
            repertory = Repertory.objects.create(name='Main',
                                                 band=request.band)
            RepertoryGroup.objects.create(name='Main', repertory=repertory,
                                          order=1)
    else:
        repertory = get_object_or_404(Repertory, id=id)

    if request.POST:
        data = request.POST
        url = reverse('repertory_details', args=(repertory.id,))
        if data.get('lock'):
            if repertory.is_free():
                repertory.lock(user)
                new_history_entry(user, repertory, 'locked')
                msg = _("The repertory is locked for edition by you.")
                messages.add_message(request, messages.WARNING, msg)
            else:
                msg = _("You can't unlock a repertory already locked.")
                messages.add_message(request, messages.WARNING, msg)
        if data.get('unlock'):
            if repertory.is_free():
                msg = _("This repertory is already unlocked.")
                messages.add_message(request, messages.SUCCESS, msg)
            else:
                repertory.unlock()
                new_history_entry(user, repertory, 'unlocked')
                msg = _("This repertory was successfully unlocked.")
                messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(url)

    groups = repertory.groups.all().order_by('order')

    c = dict(
        repertory=repertory,
        groups=groups,
        players=Player.objects.all(),
        tonality_choices=get_tonality_choices(),
        mode_choices=SongMode.choices(),
        is_locked=repertory.is_locked(user),
        editable=repertory.is_editable(user)
    )
    return c

@login_required
@check_locked_repertory
def remove_repertory(request, id):
    repertory = get_object_or_404(Repertory, id=id)
    url = reverse('repertories')
    if repertory.is_main:
        msg = _("You can't remove the main repertory!")
        messages.add_message(request, messages.WARNING, msg)
        return HttpResponseRedirect(url)
    repertory.delete()
    msg = _('The repertory "%s" was successfully removed.' % repertory.name)
    messages.add_message(request, messages.SUCCESS, msg)
    return HttpResponseRedirect(url)

@login_required
@json
@ajax_check_locked_repertory
def add_repertory_group(request, id):
    repertory = Repertory.objects.get(id=id)
    count = repertory.groups.all().count()
    group = repertory.groups.create(name=request.POST['name'], order=count + 1)
    new_history_entry(request.user, group, 'created')
    groups = repertory.groups.all().order_by('order')
    tc = RequestContext(request, dict(groups=groups, repertory=repertory))
    c = dict(
        success=True,
        content=loader.get_template("music/repertory_content.html").render(tc)
    )
    return c

@login_required
@json
@ajax_check_locked_repertory
def remove_repertory_group(request, id, group_id):
    repertory = Repertory.objects.get(id=id)
    group = repertory.groups.get(id=group_id)
    action = 'group "%s (%s)" has been deleted.' % (group.name, group.id)
    group.delete()
    new_history_entry(request.user, repertory, action)
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
@ajax_check_locked_repertory
def move_repertory_group(request, id, group_id):
    user = request.user
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

    new_history_entry(request.user, current_group, 'has been moved.')

    groups = repertory.groups.all().order_by('order')
    tc = RequestContext(request, dict(groups=groups))
    c = dict(
        editable=repertory.is_editable(user),
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
        band = request.band
        artists_ids = [a.id for a in band.artists.all()]
        ids = main_group.items.all().values_list('song__id', flat=True)
        songs = Song.objects.filter(name__icontains=name,
                                    album__artist__id__in=artists_ids)\
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
    c = dict()
    return c

@login_required
@render_to("music/add_album.html")
def add_album(request):
    year = datetime.now().year
    initial = {'artist': request.GET.get('a', '')}
    c = dict(
        form=AlbumInfoForm(initial=initial),
        max_years=MAX_YEARS,
        year=year
    )
    return c

def get_custom_results(request):
    #custom = pickle.loads(open('songs.pickle').read())
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
            artists_dict[a['name']] = a
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


    years = list(set(map(int, years)))
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
    if artist_form.is_new:
        new_history_entry(request.user, artist, "created")
    else:
        new_history_entry(request.user, artist, "updated")

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
            if album_form.is_new:
                new_history_entry(request.user, album, "created")
            else:
                new_history_entry(request.user, album, "updated")
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

def get_tonality_choices():
    tonality_choices = [(k, v, Tonality.tonality_type(k)) for k, v in
                                                      Tonality.minor_choices()]
    tonality_choices += [(k, v, Tonality.tonality_type(k)) for k, v in
                                                      Tonality.major_choices()]
    return tonality_choices

@render_to("music/album.html")
@login_required
def album(request, id):
    album = get_object_or_404(Album, id=id)
    return dict(album=album, tempo_choices=Tempo.choices(),
                tonality_choices=get_tonality_choices())

@login_required
def remove_album(request, id):
    album = get_object_or_404(Album, id=id)
    artist = album.artist
    action = 'album "%s (%s)" removed.' % (album.name, album.id)
    album.delete()
    new_history_entry(request.user, artist, action)
    msg = _('The album was successfully removed.')
    messages.add_message(request, messages.SUCCESS, msg)
    return HttpResponseRedirect(reverse('artist_albums', args=(artist.id,)))

@render_to("music/artist_albums.html")
@login_required
def artist_albums(request, id):
    artist = get_object_or_404(Artist, id=id)
    return dict(artist=artist)

@render_to("music/artists.html")
@login_required
def artists(request):
    artists = Artist.objects.all().order_by('name')
    return dict(artists=artists)

@render_to("music/artist_details.html")
@login_required
def artist_details(request, id):
    artist = get_object_or_404(Artist, id=id)
    return dict(artist=artist)

def get_song_line_content(request, song):
    template = loader.get_template("music/song_line.html")
    tonality_choices = [(k, v, Tonality.tonality_type(k)) for k, v in
                                                      Tonality.minor_choices()]
    tonality_choices += [(k, v, Tonality.tonality_type(k)) for k, v in
                                                      Tonality.major_choices()]
    c = dict(song=song, tonality_choices=tonality_choices,
             tempo_choices=Tempo.choices())
    return template.render(RequestContext(request, c))

@json
@login_required
def upload_song_audio(request, id):
    song = get_object_or_404(Song, id=id)
    audio_file = request.FILES['audio_file']
    filename = generate_filename(audio_file.name)
    handler = FileHandlerSongAudio()
    handler.load(filename, audio_file)
    handler.save()
    song.audio = filename
    song.save()
    song = Song.objects.get(id=id)
    new_history_entry(request.user, song, "new audio song has been upload.")
    content = get_song_line_content(request, song)
    return dict(success=True, content=content)

@json
@login_required
def change_tempo_signature(request, id):
    song = get_object_or_404(Song, id=id)
    beats = int(request.POST['beats'])
    value = int(request.POST['value'])
    tempo = int(request.POST['tempo'])
    song.tempo = tempo
    song.signature = "%s/%s" % (beats, value)
    song.save()
    new_history_entry(request.user, song, "tempo has been changed.")
    content = get_song_line_content(request, song)
    return dict(success=True, content=content)

@json
@login_required
def change_tonality(request, id):
    song = get_object_or_404(Song, id=id)
    song.tonality = request.POST['tonality']
    song.save()
    new_history_entry(request.user, song, "tonality has been changed.")
    content = get_song_line_content(request, song)
    return dict(success=True, content=content)

@json
@login_required
@ajax_check_locked_repertory_item
def change_repertory_item_tonality(request, id):
    item = get_object_or_404(RepertoryGroupItem, id=id)
    tonality = request.POST['tonality']
    if tonality == 'ORIGINAL':
        tonality = None
    item.tonality = tonality
    item.save()
    new_history_entry(request.user, item, "tonality has been changed.")
    content = get_song_line_repertory_content(request, item)
    return dict(success=True, content=content, item_id=item.id)

@json
@login_required
@ajax_check_locked_repertory_item
def change_repertory_item_song_mode(request, id):
    item = get_object_or_404(RepertoryGroupItem, id=id)
    item.mode = int(request.POST['mode_id'])
    item.save()
    new_history_entry(request.user, item, "song mode has been changed.")
    content = get_song_line_repertory_content(request, item)
    return dict(success=True, content=content, item_id=item.id)

@json
@login_required
@ajax_check_locked_main_repertory
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
    summary = ', new item "%s (%s)" was added.' % (item, item.id)
    new_history_entry(request.user, main, summary)
    return dict(success=True)

@json
@login_required
@ajax_check_locked_repertory
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
    summary = ', new item "%s (%s)" was added.' % (item, item.id)
    new_history_entry(request.user, group, summary)
    song_line = get_song_line_repertory_content(request, item)
    return dict(success=True, song_line=song_line)

@json
@login_required
@ajax_check_locked_repertory
def remove_song_from_repertory(request, id, group_id, item_id):
    item = get_object_or_404(RepertoryGroupItem, id=item_id,
                             group__id=group_id, group__repertory__id=id)
    n = item.number
    group = item.group
    summary = 'item "%s (%s)" has been deleted.' % (item, item.id)
    item.delete()
    new_history_entry(request.user, group, summary)
    items = group.items.filter(number__gt=n).order_by('number')
    for item in items:
        item.number -= 1
        item.save()
    return dict(success=True)

@login_required
@json
@ajax_check_locked_repertory
def move_song(request, id, group_id, item_id):
    user = request.user
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
    new_history_entry(request.user, current_item, "has been moved.")
    tc = dict(
        group=group,
        repertory=repertory,
        editable=repertory.is_editable(user)
    )
    tc = RequestContext(request, tc)
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
            new_history_entry(request.user, form.instance, 'created')
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
    new_history_entry(request.user, instrument, "has been removed.")
    instrument.delete()
    return dict(success=True)

@render_to("music/instruments.html")
def instruments(request):
    instruments = Instrument.objects.all().order_by('name')
    tag_types = InstrumentTagType.objects.all()
    return dict(instruments=instruments, tag_types=tag_types)

@json
@login_required
def add_player(request, id, user_id):
    data = dict(instrument=id, user=user_id)
    form = PlayerForm(data=data)
    user = request.user
    if form.is_valid():
        form.save()
        new_history_entry(request.user, form.instance, 'created')
        template = loader.get_template("auth/profile_instruments.html")
        context = RequestContext(request, dict(user=user))
        return dict(success=True, content=template.render(context))
    return dict(success=False)

@json
@login_required
def remove_player(request, id, user_id):
    player = get_object_or_404(Player, id=id, user__id=user_id)
    new_history_entry(request.user, player, "has been removed.")
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
    enable_inactive = request.band.enable_inactive_members
    item = get_object_or_404(RepertoryGroupItem, id=id)
    ids = item.players.all().values_list('player__id', flat=True)
    players = Player.objects.all().exclude(id__in=ids)
    if not enable_inactive:
        players = players.exclude(user__is_active=False)

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

    instruments_dict = {}
    for player in players:
        instrument = player.instrument
        if not instruments_dict.has_key(instrument.id):
            instruments_dict[player.instrument.id] = {'players': []}
        instruments_dict[player.instrument.id]['instrument'] = instrument
        instruments_dict[player.instrument.id]['players'].append(player)

    template = loader.get_template("music/players_menu.html")
    c = dict(
        instruments=instruments_dict.values(),
        item=item,
        members=members,
        tags_tuples=tags_dict.items()
    )
    context = RequestContext(request, c)
    return dict(success=True, content=template.render(context))

def player_repertory_item_menu_content(request, player_repertory_item):
    user = request.user
    ids = player_repertory_item.tag_types.all().values_list('id', flat=True)
    all_tag_types = InstrumentTagType.objects.filter(
                            instrument=player_repertory_item.player.instrument)
    tag_types = []
    for tag_type in all_tag_types:
        if tag_type.id in ids:
            tag_type.selected = True
        tag_types.append(tag_type)
    template = loader.get_template("music/player_repertory_item_menu.html")
    item = player_repertory_item.repertory_item
    repertory = item.group.repertory
    c = dict(
        player_repertory_item=player_repertory_item,
        tag_types=tag_types,
        editable=repertory.is_editable(user)
    )
    context = RequestContext(request, c)
    player = dict(
        id=player_repertory_item.id,
        is_lead=player_repertory_item.is_lead
    )
    return dict(content=template.render(context), player=player,
                item_id=item.id)

@json
@login_required
def player_repertory_item_menu(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    c = player_repertory_item_menu_content(request, player_repertory_item)
    c['success'] = True
    return c

@json
@login_required
@ajax_check_locked_player_repertory_item
def toogle_tag_type(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    tag_type_id = int(request.POST.get('tag_type_id'))
    tag_type = get_object_or_404(InstrumentTagType, id=tag_type_id)
    ids = player_repertory_item.tag_types.all().values_list('id', flat=True)
    if tag_type_id in ids:
        player_repertory_item.tag_types.remove(tag_type)
        summary = 'tag type "%s (%s) has been added"' % (tag_type, tag_type.id)
    else:
        player_repertory_item.tag_types.add(tag_type)
        summary = 'tag type "%s (%s) has been removed"' % (tag_type,
                                                           tag_type.id)
    new_history_entry(request.user, player_repertory_item, summary)
    player_repertory_item.save()
    c = player_repertory_item_menu_content(request, player_repertory_item)
    c['success'] = True
    return c

@json
@login_required
@ajax_check_locked_player_repertory_item
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
@ajax_check_locked_player_repertory_item
def change_as_member(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    artist = get_object_or_404(Artist, id=request.POST['member_id'])
    player_repertory_item.as_member = artist
    player_repertory_item.save()
    new_history_entry(request.user, player_repertory_item,
                      "as member changed.")
    c = player_repertory_item_menu_content(request, player_repertory_item)
    c['success'] = True
    return c

@json
@login_required
@ajax_check_locked_player_repertory_item
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
    new_history_entry(request.user, player_repertory_item, "player changed.")
    if other_player_repertory_item:
        other_player_repertory_item.player = current_player
        other_player_repertory_item.save()
        new_history_entry(request.user, other_player_repertory_item,
                          "player changed.")
    c = player_repertory_item_menu_content(request, player_repertory_item)
    c['success'] = True
    return c

@json
@login_required
@ajax_check_locked_player_repertory_item
def change_player_user_options(request, id):
    enable_inactive = request.band.enable_inactive_members
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    player = player_repertory_item.player
    players = Player.objects.filter(instrument=player.instrument)\
                            .exclude(id=player.id)
    if not enable_inactive:
        players = players.exclude(user__is_active=False)
    template = loader.get_template("music/change_player_user_options.html")
    c = dict(players=players, player_repertory_item=player_repertory_item)
    context = RequestContext(request, c)
    no_players = not bool(players.count())
    return dict(success=True, content=template.render(context),
                no_players=no_players)

@json
@login_required
@ajax_check_locked_player_repertory_item
def change_notes(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    player_repertory_item.notes = request.POST['notes']
    player_repertory_item.save()
    new_history_entry(request.user, player_repertory_item, "notes changed.")
    return dict(success=True)

@json
@login_required
@ajax_check_locked_player_repertory_item
def add_document_for_player_repertory_item(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    data = dict(player_repertory_item=player_repertory_item.id)
    form = DocumentPlayerRepertoryItemForm(data=data, files=request.FILES)
    if form.is_valid():
        doc = form.save()
        summary = 'created for "%s (%s)"' % (player_repertory_item,
                                             player_repertory_item.id)
        new_history_entry(request.user, doc, summary)
        c = player_repertory_item_menu_content(request, player_repertory_item)
        c['success'] = True
        return c
    else:
        return dict(success=False)

@json
@login_required
@ajax_check_locked_player_repertory_item
def remove_document_for_player_repertory_item(request, id, document_id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    document = player_repertory_item.documents.get(id=document_id)
    document.delete()
    summary = 'document "%s (%s)" has been removed.' % (document, document.id)
    new_history_entry(request.user, player_repertory_item, summary)
    c = player_repertory_item_menu_content(request, player_repertory_item)
    c['success'] = True
    return c

def get_song_line_repertory_content(request, item):
    user = request.user
    group = item.group
    repertory = group.repertory
    temp = loader.get_template("music/song_line_repertory_content.html")
    tonality_choices = get_tonality_choices()
    c = {'item': item, 'group': group, 'repertory': repertory,
         'tonality_choices': tonality_choices,
         'mode_choices': SongMode.choices(),
         'editable': repertory.is_editable(user)}
    return temp.render(RequestContext(request, c))

@json
@login_required
def update_song_line_repertory_content(request, id):
    item = get_object_or_404(RepertoryGroupItem, id=id)
    content = get_song_line_repertory_content(request, item)
    return dict(success=True, content=content, item_id=item.id)

@json
@login_required
def rate_repertory_item(request, id):
    user = request.user
    item = get_object_or_404(RepertoryGroupItem, id=id)
    rate = int(request.POST['rate'])
    try:
        rating = UserRepertoryItemRating.objects.get(user=user,
                                                     repertory_item=item)
    except UserRepertoryItemRating.DoesNotExist:
        rating = UserRepertoryItemRating(user=user, repertory_item=item)
    rating.rate = rate
    rating.save()
    content = get_song_line_repertory_content(request, item)
    return dict(success=True, content=content, item_id=item.id)

@json
@login_required
def rate_player_repertory_item(request, id):
    user = request.user
    player_rep = get_object_or_404(PlayerRepertoryItem, id=id)
    rate = int(request.POST['rate'])
    try:
        rating = PlayerRepertoryItemRating.objects.get(user=user,
                                              player_repertory_item=player_rep)
    except PlayerRepertoryItemRating.DoesNotExist:
        rating = PlayerRepertoryItemRating(user=user,
                                           player_repertory_item=player_rep)
    rating.rate = rate
    rating.save()
    item = player_rep.repertory_item
    content = get_song_line_repertory_content(request, item)
    return dict(success=True, content=content, item_id=item.id)

@json
@login_required
@ajax_check_locked_repertory_item
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
        new_history_entry(request.user, form.instance, "created")
        item = form.instance.repertory_item
        content = get_song_line_repertory_content(request, item)
        return dict(success=True, content=content, item_id=item.id)
    return dict(success=False)

@json
@login_required
@ajax_check_locked_player_repertory_item
def remove_player_repertory_item(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    item = player_repertory_item.repertory_item
    content = get_song_line_repertory_content(request, item)
    return dict(success=True, content=content, item_id=item.id)

@json
@login_required
@ajax_check_locked_player_repertory_item
def player_set_as_lead(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    player_repertory_item.is_lead = bool(int(request.POST.get('is_lead')))
    player_repertory_item.save()
    summary = "change is lead as %s" % player_repertory_item.is_lead
    new_history_entry(request.user, player_repertory_item, summary)
    item = player_repertory_item.repertory_item
    content = get_song_line_repertory_content(request, item)
    return dict(success=True, content=content, item_id=item.id)

@login_required
@render_to("music/add_instrument_tag_type.html")
def add_instrument_tag_type(request):
    if request.POST:
        form = InstrumentTagTypeForm(data=request.POST)
        if form.is_valid():
            form.save()
            new_history_entry(request.user, form.instance, "created")
            msg = _('The instrument tag type was successfully added.')
            messages.add_message(request, messages.SUCCESS, msg)
            url = reverse('instruments')
            return HttpResponseRedirect(url)
    else:
        form = InstrumentTagTypeForm
    return dict(form=form)

@login_required
@render_to("music/instrument_tag_types.html")
def instrument_tag_types(request):
    tag_types = InstrumentTagType.objects.all()
    return dict(tag_types=tag_types)

@login_required
@render_to("music/history.html")
def music_history(request):
    users = User.objects.all()
    selected_user = int(request.GET.get('u') or users[0].id)
    history = MusicHistoryChanges.objects.filter(user__id=selected_user)
    history = history.order_by('-content_date')
    return dict(history=history, users=users, selected_user=selected_user)
