# -*- coding: utf-8; Mode: Python -*-

import decimal
import pickle
from datetime import datetime

from django.db.models import Q
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User, Permission
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.utils import simplejson

from hbauth.decorators import login_required
from section.decorators import render_to, json
from discogs import Discogs
from photo.image import FileHandlerSongAudio
from forms import EventRepertoryForm, AlbumInfoForm, AlbumForm, SongForm, \
                  InstrumentForm, PlayerForm, ArtistForm, \
                  PlayerRepertoryItemForm, InstrumentTagTypeForm, \
                  DocumentPlayerRepertoryItemForm, BandForm, RehearsalForm
from models import Repertory, EventRepertory, Song, Album, Artist, \
                   RepertoryItem, EventRepertoryItem, Instrument, \
                   Player, InstrumentTagType, PlayerRepertoryItem, \
                   MusicHistoryChanges, UserRepertoryItemRating, \
                   PlayerRepertoryItemRating, Band, BandArtist, Rehearsal
from decorators import check_locked_event_repertory, \
                       ajax_check_locked_repertory_item, \
                       ajax_check_locked_player_repertory_item, \
                       ajax_check_locked_main_repertory, \
                       ajax_check_locked_event_repertory, \
                       ajax_check_locked_event_repertory_item

from event.models import Event
from utils import get_or_create_temporary, mzip, str_list_in_list, \
                  generate_filename
from defaults import Tempo, Tonality, SongMode, RepertoryItemStatus

DISCOGS_PAGES = 500
MAX_YEARS = 30

def new_history_entry(user, instance, action, created=False):
    content_type = ContentType.objects.get_for_model(type(instance))
    summary = '%s "%s (%s)" %s' % (content_type, instance,
                                       instance.id, action)
    history = MusicHistoryChanges.objects.create(
        content_type=content_type,
        object_id=instance.id,
        user=user,
        summary=summary,
        created=created
    )
    history.set_content_object(instance)
    history.save()
    return history

@login_required
@render_to("music/repertories.html")
def repertories(request):
    event_repertories = EventRepertory.objects.filter(event__isnull=False)
    rehearsal_repertories = EventRepertory.objects\
                                          .filter(rehearsal__isnull=False)
    try:
        main_repertory = request.band.repertory
    except Repertory.DoesNotExist:
        main_repertory = Repertory.objects.create(band=request.band)
    return dict(event_repertories=event_repertories,
                rehearsal_repertories=rehearsal_repertories,
                main_repertory=main_repertory)

@login_required
@render_to("music/repertories_statistics.html")
def repertories_statistics(request):
    band = request.band
    band.update_counts()
    main_repertory = band.repertory
    items = main_repertory.items.all()
    repertories = EventRepertory.objects.all()
    stats = repertory_stats(main_repertory)
    statuses = RepertoryItemStatus.active_choices()
    modes = SongMode.choices()
    rehearsal_id = long(request.GET.get('rehearsal', 0))
    event_id = long(request.GET.get('show', 0))
    return dict(repertories=repertories, main_repertory=main_repertory,
                stats=stats, items=items, band=band, statuses=statuses,
                modes=modes, rehearsal_id=rehearsal_id, event_id=event_id)

@json
@login_required
def repertories_stats(request):
    band = request.band
    main_repertory = band.repertory
    stats = repertory_stats(main_repertory)
    template = loader.get_template("music/repertories_stats.html")
    content = template.render(RequestContext(request, dict(stats=stats)))
    return dict(success=True, content=content)

@login_required
@render_to("music/band_settings.html")
def band_settings(request, id):
    band = get_object_or_404(Band, id=id)
    if request.POST:
        if request.POST.get('permissions_of'):
            member = User.objects.get(id=long(request.POST['permissions_of']))
            member.user_permissions.clear()
            for permission in request.POST.getlist('member_permissions', []):
                member.user_permissions.add(long(permission))
            member.save()
            new_history_entry(request.user, member, 'permissions changed')
            msg = _('The permissions of %s was successfully modified.' %
                    member.get_full_name())
            messages.add_message(request, messages.SUCCESS, msg)
            url = reverse('band_settings', args=(band.id,))
            return HttpResponseRedirect(url)
        else:
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
                new_history_entry(request.user, form.instance, 'created', True)
                msg = _('The band settings was successfully changed.')
                messages.add_message(request, messages.SUCCESS, msg)
                url = reverse('band_settings', args=(form.instance.id,))
                return HttpResponseRedirect(url)
    else:
        form = BandForm(instance=band)
    permissions = Permission.objects.filter(codename__contains='manage_')
    permissions_users = []
    for member in band.active_members:
        perms = []
        for permission in permissions:
            perms.append(dict(
                permission=permission,
                hasperm=bool(member.user_permissions.filter(id=permission.id)\
                                                    .count())
            ))
        permissions_users.append(dict(
            member=member,
            permissions=perms
        ))
    return dict(band=band, form=form, permissions=permissions,
                permissions_users=permissions_users)

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
            new_history_entry(request.user, form.instance, 'created', True)
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
    upcoming = Rehearsal.objects.filter(date__gte=now).order_by('date')
    past = Rehearsal.objects.filter(date__lte=now).order_by('-date')
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
@permission_required('music.manage_rehearsals', '/permission/denied/')
def add_rehearsal(request):
    user = request.user
    band = Band.get_active_band(request)
    if request.POST:
        data = request.POST
        form = RehearsalForm(band=band, data=data)
        if form.is_valid():
            form.save()
            msg = _("The rehearsal was successfully created.")
            new_history_entry(user, form.instance, 'created', True)
            messages.add_message(request, messages.SUCCESS, msg)
            url = reverse("rehearsal", args=(form.instance.id,))
            band.reload_band_cache(request)
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
@permission_required('music.manage_rehearsals', '/permission/denied/')
def remove_rehearsal(request, id):
    band = request.band
    user = request.user
    rehearsal = get_object_or_404(Rehearsal, id=id)
    rehearsal.delete()
    msg = _("The rehearsal was successfully removed.")
    new_history_entry(user, rehearsal, 'removed')
    messages.add_message(request, messages.SUCCESS, msg)
    band.reload_band_cache(request)
    return HttpResponseRedirect(reverse("rehearsals"))

@login_required
@render_to("music/add_rehearsal.html")
@permission_required('music.manage_rehearsals', '/permission/denied/')
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
@render_to("music/add_event_repertory.html")
@permission_required('music.manage_event_repertories', '/permission/denied/')
def add_event_repertory(request):
    band = request.band
    initial = {'band': band}
    if request.POST:
        form = EventRepertoryForm(request.POST, initial=initial)
        if form.is_valid():
            form.save()
            if not form.instance.band:
                form.instance.band = request.band
                form.instance.save()
            if request.POST.get('mode') == 'based_on_repertory':
                id = int(request.POST['repertory_based'])
                based_rep = EventRepertory.objects.get(id=id)
                form.instance.import_items_from(based_rep)
            new_history_entry(request.user, form.instance, 'created', True)
            msg = _('The repertory was successfully created.')
            messages.add_message(request, messages.SUCCESS, msg)
            url = reverse('event_repertory', args=(form.instance.id,))
            band.reload_band_cache(request)
            return HttpResponseRedirect(url)
    else:
        form = EventRepertoryForm(initial=initial)
    repertories = EventRepertory.objects.all()
    return dict(form=form, repertories=repertories)

@login_required
@permission_required('music.manage_event_repertories', '/permission/denied/')
def add_event_repertory_for_rehearsal(request, id):
    success, rep, msg = _add_event_repertory_for_rehearsal(request, id)
    if success:
        messages.add_message(request, messages.SUCCESS, msg)
        url = reverse('event_repertory', args=(rep.id,))
        return HttpResponseRedirect(url)
    else:
        messages.add_message(request, messages.ERROR, msg)
        url = reverse('rehearsal', args=(id,))
        return HttpResponseRedirect(url)

@json
@login_required
@permission_required('music.manage_event_repertories', '/permission/denied/')
def add_event_repertory_for_rehearsal_ajax(request, id):
    success, rep, msg = _add_event_repertory_for_rehearsal(request, id)
    if success:
        url = reverse('event_repertory', args=(rep.id,))
        return dict(success=success, url=url)
    else:
        return dict(success=success, message=msg)

@json
@login_required
@permission_required('music.manage_event_repertories', '/permission/denied/')
def add_event_repertory_for_event_ajax(request, id):
    success, rep, msg = _add_event_repertory_for_event(request, id)
    if success:
        url = reverse('event_repertory', args=(rep.id,))
        return dict(success=success, url=url)
    else:
        return dict(success=success, message=msg)

@login_required
@permission_required('music.manage_event_repertories', '/permission/denied/')
def add_event_repertory_for_event(request, id):
    success, rep, msg = _add_event_repertory_for_event(request, id)
    if success:
        messages.add_message(request, messages.SUCCESS, msg)
        url = reverse('event_repertory', args=(rep.id,))
        return HttpResponseRedirect(url)
    else:
        messages.add_message(request, messages.ERROR, msg)
        url = reverse('event_details', args=(id,))
        return HttpResponseRedirect(url)

def _add_event_repertory_for_rehearsal(request, id):
    band = request.band
    data = {
        'band': band.id,
        'rehearsal': id
    }
    try:
        repertory = EventRepertory.objects.get(band=band.id,
                                               rehearsal__id=long(id))
    except EventRepertory.DoesNotExist:
        repertory = None
    form = EventRepertoryForm(data, instance=repertory)

    if form.is_valid():
        form.save()
        last = request.GET.get('import_from_last')
        if last and last.isdigit() and int(last):
            reps = EventRepertory.objects.filter(band=band,
                                                 rehearsal__isnull=False)\
                                         .exclude(id=form.instance.id)\
                                         .order_by('-rehearsal__date')
            if reps.count():
                rep = reps[0]
                for item in rep.items.all():
                    new_item = item.clone_object(form.instance)
                    new_item.times_played = 0
                    new_item.save()
        if request.POST:
            ids = [long(i) for i in request.POST.getlist('items_ids[]')]
            items = RepertoryItem.objects.filter(id__in=ids)
            for item in items:
                ids = form.instance.all_items.all().values_list('item__id',
                                                                flat=True)
                if item.id in ids:
                    continue
                new_item = EventRepertoryItem.objects.create(item=item,
                                                       repertory=form.instance,
                                                       times_played=0)
                new_history_entry(request.user, new_item, 'created', True)

        new_history_entry(request.user, form.instance, 'created', True)
        msg = _('The repertory was successfully created.')
        band.reload_band_cache(request)
        return True, form.instance, msg
    else:
        msg = _(u'Some error occurred while trying to create the repertory. %s'
                % form.errors)
        return False, None, msg

def _add_event_repertory_for_event(request, id):
    band = request.band
    data = {
        'band': band.id,
        'event': id
    }
    try:
        repertory = EventRepertory.objects.get(band=band.id,
                                               event__id=long(id))
    except EventRepertory.DoesNotExist:
        repertory = None
    form = EventRepertoryForm(data, instance=repertory)

    if form.is_valid():
        form.save()
        last = request.GET.get('import_from_last')
        if last and last.isdigit() and int(last):
            reps = EventRepertory.objects.filter(band=band,
                                                 event__isnull=False)\
                                         .exclude(id=form.instance.id)\
                                         .order_by('-event__starts_at')
            if reps.count():
                rep = reps[0]
                for item in rep.items.all():
                    new_item = item.clone_object(form.instance)
                    new_item.times_played = 0
                    new_item.save()
        if request.POST:
            ids = [long(i) for i in request.POST.getlist('items_ids[]')]
            items = RepertoryItem.objects.filter(id__in=ids)
            for item in items:
                ids = form.instance.all_items.all().values_list('item__id',
                                                                flat=True)
                if item.id in ids:
                    continue
                new_item = EventRepertoryItem.objects.create(item=item,
                                                       repertory=form.instance,
                                                       times_played=1)
                new_history_entry(request.user, new_item, 'created', True)
        msg = _('The repertory was successfully created.')
        new_history_entry(request.user, form.instance, 'created', True)
        band.reload_band_cache(request)
        return True, form.instance, msg

    else:
        msg = _(u'Some error occurred while trying to create the repertory. %s'
                % form.errors)
        return False, None, msg

def repertory_stats(repertory):
    af = repertory.all_items.filter
    stats_keys = {
        1: 'new',
        2: 'trash',
        3: 'restored',
        4: 'working',
        5: 'ready',
        6: 'abandoned'
    }

    artists = {}
    for item in repertory.items.all():
        artist = item.song.album.artist
        if artist.id not in artists:
            artists[artist.id] = dict(
                total=0,
                name=artist.name_display,
                stats=dict(
                    new=0,
                    ready=0,
                    working=0,
                    abandoned=0,
                    restored=0,
                    trash=0
                )
            )
        artists[artist.id]['total'] += 1
        artists[artist.id]['stats'][stats_keys[item.status]] += 1

    stats = dict(
        total=repertory.items.all().count(),
        new=af(status=RepertoryItemStatus.new).count(),
        ready=af(status=RepertoryItemStatus.ready).count(),
        working=af(status=RepertoryItemStatus.working).count(),
        abandoned=af(status=RepertoryItemStatus.abandoned).count(),
        restored=af(status=RepertoryItemStatus.restored).count(),
        trash=af(status=RepertoryItemStatus.deleted).count(),
        artists=artists.values()
    )
    return stats

@login_required
@render_to("music/main_repertory.html")
def main_repertory(request):
    user = request.user
    try:
        repertory = request.band.repertory
    except Repertory.DoesNotExist:
        repertory = Repertory.objects.create(band=request.band)

    if request.POST:
        data = request.POST
        url = reverse('main_repertory')
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

    c = dict(
        repertory=repertory,
        items=repertory.items.order_by('status'),
        sort=dict(status=True),
        trash=repertory.trash,
        players=Player.objects.all(),
        tonality_choices=get_tonality_choices(),
        mode_choices=SongMode.choices(),
        status_choices=RepertoryItemStatus.active_choices(),
        is_locked=repertory.is_locked(user),
        editable=repertory.is_editable(user),
        has_perm=user.has_perm('music.manage_main_repertory'),
        stats=repertory_stats(repertory)
    )
    return c

@login_required
@render_to("music/event_repertory.html")
def event_repertory(request, id):
    user = request.user
    repertory = get_object_or_404(EventRepertory, id=id)

    if request.POST:
        data = request.POST
        url = reverse('event_repertory', args=(id,))
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

    c = dict(
        repertory=repertory,
        items=repertory.items,
        statuses=RepertoryItemStatus.active_choices(),
        is_locked=repertory.is_locked(user),
        editable=repertory.is_editable(user),
        has_perm=user.has_perm('music.manage_event_repertories')
    )
    return c

@login_required
@check_locked_event_repertory
def remove_event_repertory(request, id):
    band = request.band
    repertory = get_object_or_404(EventRepertory, id=id)
    url = reverse('repertories')
    repertory.delete()
    msg = _(u'The "%s" was successfully removed.' % repertory)
    messages.add_message(request, messages.SUCCESS, msg)
    band.reload_band_cache(request)
    return HttpResponseRedirect(url)

@login_required
@json
@permission_required('music.manage_main_repertory', '/permission/denied/')
def search_song_by_name(request):
    band = request.band
    name = request.POST['name']
    def item(s):
        return dict(
            name=str(s.name),
            artist=str(s.album.artist.short_name),
            url=str(s.album.icon_url),
            id=s.id
        )
    main = band.repertory
    artists_ids = [a.id for a in band.artists.all()]
    ids = main.items.values_list('song__id', flat=True)
    songs = Song.objects.filter((Q(name__icontains=name) |
                                 Q(album__artist__name__icontains=name)),
                                album__artist__id__in=artists_ids)\
                        .exclude(id__in=ids)[:10]
    songs = [item(s) for s in songs]

    c = dict(
        success=True,
        songs=songs
    )
    return c

@login_required
@json
@permission_required('music.manage_event_repertories', '/permission/denied/')
def search_item_by_name(request, id):
    name = request.POST['name']
    def item(i):
        return dict(
            name=str(i.song.name),
            artist=str(i.song.album.artist.short_name),
            url=str(i.song.album.icon_url),
            id=i.id
        )
    repertory = EventRepertory.objects.get(id=id)
    main = request.band.repertory
    ids = repertory.all_items.values_list('item__id', flat=True)
    ids = filter(lambda x: x is not None, ids)
    items = main.items.filter(song__name__icontains=name)\
                      .exclude(id__in=ids)[:10]
    songs = [item(i) for i in items]
    c = dict(
        success=True,
        songs=songs
    )
    return c

@login_required
@render_to("music/music_management.html")
def music_management(request):
    now = datetime.now()
    rehearsals = dict(
        upcoming=Rehearsal.objects.filter(date__gte=now).order_by('date'),
        past=Rehearsal.objects.filter(date__lte=now).order_by('-date')[:5]
    )
    return dict(all_rehearsals=rehearsals)

@login_required
@render_to("music/add_album.html")
@permission_required('music.manage_music', '/permission/denied/')
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
@permission_required('music.manage_music', '/permission/denied/')
def custom_album_creation(request):
    custom = get_custom_results(request)
    c = dict(custom=custom)
    return c

@login_required
@json
@permission_required('music.manage_music', '/permission/denied/')
def register_album(request):
    redirect_url = None
    message = ''
    data = request.POST
    adata = {'resource_url': data['artist_resource_url']}
    artist_form = ArtistForm(adata)
    success = artist_form.is_valid()
    artist = artist_form.save()
    if artist_form.is_new:
        new_history_entry(request.user, artist, "created", True)
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
                new_history_entry(request.user, album, "created", True)
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
    has_perm = request.user.has_perm('music.manage_music')
    return dict(album=album, tempo_choices=Tempo.choices(),
                tonality_choices=get_tonality_choices(), has_perm=has_perm)

@login_required
@permission_required('music.manage_music', '/permission/denied/')
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
    has_perm = request.user.has_perm('music.manage_music')
    return dict(artist=artist, has_perm=has_perm)

@render_to("music/artists.html")
@login_required
def artists(request):
    band = request.band
    filt = request.GET.get('f')
    if filt == 'active':
        artists = band.artists.all().order_by('name')
    elif filt == 'all':
        artists = Artist.objects.all().order_by('name')
    elif filt == 'inactive':
        ids = band.artists.all().values_list('id', flat=True)
        artists = Artist.objects.all().exclude(id__in=ids).order_by('name')
    elif filt == 'withalbums':
        artists = Artist.objects.all()
        artists = [a for a in artists if a.albums.count()]
    else:
        artists = band.artists.all().order_by('name')
    has_perm = request.user.has_perm('music.manage_music')
    return dict(artists=artists, has_perm=has_perm)

@render_to("music/artist_details.html")
@login_required
def artist_details(request, id):
    artist = get_object_or_404(Artist, id=id)
    has_perm = request.user.has_perm('music.manage_music')
    return dict(artist=artist, has_perm=has_perm)

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
@permission_required('music.manage_music', '/permission/denied/')
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
@permission_required('music.manage_music', '/permission/denied/')
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
@permission_required('music.manage_music', '/permission/denied/')
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
@permission_required('music.manage_main_repertory', '/permission/denied/')
def change_repertory_item_tonality(request, id):
    item = get_object_or_404(RepertoryItem, id=id)
    tonality = request.POST['tonality']
    if tonality == 'ORIGINAL':
        tonality = None
    item.tonality = tonality
    item.save()
    new_history_entry(request.user, item, "tonality has been changed.")
    content = get_main_repertory_item_content(request, item)
    return dict(success=True, content=content, item_id=item.id)

@json
@login_required
@ajax_check_locked_repertory_item
@permission_required('music.manage_main_repertory', '/permission/denied/')
def change_repertory_item_song_mode(request, id):
    item = get_object_or_404(RepertoryItem, id=id)
    item.mode = int(request.POST['mode_id'])
    item.save()
    new_history_entry(request.user, item, "song mode has been changed.")
    content = get_main_repertory_item_content(request, item)
    return dict(success=True, content=content, item_id=item.id)

@json
@login_required
@ajax_check_locked_repertory_item
@permission_required('music.manage_main_repertory', '/permission/denied/')
def change_repertory_item_status(request, id):
    item = get_object_or_404(RepertoryItem, id=id)
    item.status = int(request.POST['status_id'])
    item.save()
    new_history_entry(request.user, item, "song status has been changed.")
    content = get_main_repertory_item_content(request, item)
    return dict(success=True, content=content, item_id=item.id)

@json
@login_required
@ajax_check_locked_repertory_item
@permission_required('music.manage_main_repertory', '/permission/denied/')
def change_repertory_item_date(request, id):
    item = get_object_or_404(RepertoryItem, id=id)
    item.date = datetime.strptime(request.POST['date'], "%Y-%m-%d")
    item.save()
    new_history_entry(request.user, item, "song date has been changed.")
    content = get_main_repertory_item_content(request, item)
    return dict(success=True, content=content, item_id=item.id)

@json
@login_required
@ajax_check_locked_event_repertory_item
@permission_required('music.manage_event_repertories', '/permission/denied/')
def change_event_repertory_item_times_played(request, id):
    item = get_object_or_404(EventRepertoryItem, id=id)
    item.times_played = request.POST['times_played']
    item.save()
    new_history_entry(request.user, item, "times_played has been changed.")
    content = get_event_repertory_item_content(request, item)
    return dict(success=True, content=content, item_id=item.id)

@json
@login_required
@ajax_check_locked_main_repertory
@permission_required('music.manage_main_repertory', '/permission/denied/')
def add_song_to_main_repertory(request):
    band = request.band
    song = get_object_or_404(Song, id=request.POST['id'])
    main = band.repertory
    if main.trash.filter(song__id=song.id).count():
        msg = _("This song is in trash, you can restore it from there!")
        return dict(success=False, message=msg)
    if main.items.filter(song__id=song.id).count():
        msg = _("Song already exist in repertory!")
        return dict(success=False, message=msg)
    item = RepertoryItem.objects.create(repertory=main,
                                        song=song)
    summary = ', new item "%s" was added.' % item
    new_history_entry(request.user, main, summary)
    song_line = get_main_repertory_item_content(request, item)
    return dict(success=True, song_line=song_line)

@json
@login_required
@ajax_check_locked_event_repertory
@permission_required('music.manage_event_repertories', '/permission/denied/')
def add_item_to_event_repertory(request, id):
    repertory = get_object_or_404(EventRepertory, id=id)
    item = get_object_or_404(RepertoryItem, id=request.POST['id'])
    if repertory.items.filter(item__id=item.id).count():
        msg = _("Song already exist in repertory!")
        return dict(success=False, message=msg)
    new_item = _add_item_to_event_repertory(request, repertory, item)
    song_line = get_event_repertory_item_content(request, new_item)
    return dict(success=True, song_line=song_line)

def _add_item_to_event_repertory(request, repertory, item):
    count = repertory.items.all().count()
    times_played = 1
    if repertory.rehearsal:
        times_played = 0
    item = EventRepertoryItem.objects.create(repertory=repertory, item=item,
                                             order=count + 1,
                                             times_played=times_played)
    summary = ', new item "%s" was added.' % item
    new_history_entry(request.user, repertory, summary)
    return item

@json
@login_required
@ajax_check_locked_event_repertory
@permission_required('music.manage_event_repertories', '/permission/denied/')
def add_event_repertory_items_by_category(request, id):
    repertory = get_object_or_404(EventRepertory, id=id)
    user = request.user
    band = request.band
    main_repertory = band.repertory
    data = request.POST
    items = main_repertory.all_items.all()
    if data.get('by_status'):
        items = items.filter(status=int(data['by_status']))
    if data.get('above_stars'):
        if data['above_stars_voted_by'] == 'me':
            items = [i for i in items
                        if i.user_votes(user).rate >= int(data['above_stars'])]
        else:
            items = [i for i in items if i.ratings >= int(data['above_stars'])]
    if data.get('below_stars'):
        if data['below_stars_voted_by'] == 'me':
            items = [i for i in items
                        if i.user_votes(user).rate and
                           i.user_votes(user).rate <= int(data['below_stars'])]
        else:
            items = [i for i in items if i.ratings and
                                         i.ratings <= int(data['below_stars'])]
    played_in_rehearsals_below = data.get('played_in_rehearsals_below')
    played_in_rehearsals_above = data.get('played_in_rehearsals_above')
    if played_in_rehearsals_below or played_in_rehearsals_above:
        perc = float(played_in_rehearsals_below or
                     played_in_rehearsals_above) / 100
        if played_in_rehearsals_below:
            ids = [i.id for i in items if i.frequency_in_rehearsals <= perc]
        else:
            ids = [i.id for i in items if i.frequency_in_rehearsals >= perc]
        items = [i for i in items if i.id in ids]

    items_ids = []
    for item in items:
        if repertory.all_items.filter(item=item):
            # skip existing in the repertory
            continue
        new_item = _add_item_to_event_repertory(request, repertory, item)
        items_ids.append(new_item.id)

    content = get_event_repertory_content(request, repertory)
    return dict(success=True, content=content, items_ids=items_ids)

@json
@login_required
@ajax_check_locked_event_repertory
@permission_required('music.manage_event_repertories', '/permission/denied/')
def event_repertory_items_dynamic_ordering(request, id):
    repertory = get_object_or_404(EventRepertory, id=id)
    levels = [int(i) for i in request.POST.getlist('levels[]')]
    items = repertory.all_items.all()
    count = items.count()
    slow = items.filter(item__mode=SongMode.slow)
    medium = items.filter(item__mode=SongMode.medium)
    fast = items.filter(item__mode=SongMode.fast)
    items_by_level = {
        1: (slow, slow.count(), 0),
        2: (medium, medium.count(), 0),
        3: (fast, fast.count(), 0)
    }
    intervals = items.filter(item=None)
    ic = intervals.count()
    intervals_div = count / (ic + 1)
    nlevels_dict = {1: 0, 2: 0, 3: 0}
    for level in levels:
        nlevels_dict[level] += 1
    oitems = []
    for level in levels:
        if intervals and \
           len(oitems) / intervals_div == (ic + 1 - len(intervals)):
            oitems.append(intervals[0])
            intervals = intervals[1:]
        its, count, cc = items_by_level[level]
        cc += 1
        c = count / nlevels_dict[level]
        if cc >= nlevels_dict[level]:
            oitems += its
        else:
            oitems += its[:c]
        items_by_level[level] = (its[c:], count, cc)
    for i, item in enumerate(oitems):
        item.order = i + 1
    for item in oitems:
        item.save()
    content = get_event_repertory_content(request, repertory)
    return dict(success=True, content=content)


@json
@login_required
@ajax_check_locked_event_repertory
@permission_required('music.manage_event_repertories', '/permission/denied/')
def add_event_repertory_item_interval(request, id):
    repertory = get_object_or_404(EventRepertory, id=id)
    interval = int(request.POST['interval'])
    count = repertory.items.all().count()
    item = EventRepertoryItem.objects.create(repertory=repertory,
                                             order=count + 1,
                                             empty_duration=interval)
    summary = ', new item interval "%s" was added.' % item
    new_history_entry(request.user, repertory, summary)
    song_line = get_event_repertory_item_content(request, item)
    return dict(success=True, song_line=song_line)

@json
@login_required
@ajax_check_locked_repertory_item
@permission_required('music.manage_main_repertory', '/permission/denied/')
def remove_song_from_main_repertory(request, id):
    item = get_object_or_404(RepertoryItem, id=id)
    repertory = item.repertory
    summary = 'item "%s" has been removed (moved to trash).' % item
    item.to_trash()
    new_history_entry(request.user, repertory, summary)
    trash_content = get_trash_content(request, repertory)
    return dict(success=True, trash_content=trash_content)

def get_event_repertory_content(request, repertory):
    user = request.user
    items = repertory.items
    tc = dict(
        repertory=repertory,
        items=items,
        statuses=RepertoryItemStatus.active_choices(),
        is_locked=repertory.is_locked(user),
        editable=repertory.is_editable(user),
        has_perm=user.has_perm('music.manage_event_repertories')
    )
    tc = RequestContext(request, tc)
    return loader.get_template("music/event_repertory_content.html").render(tc)

def _sort_repertory(request, items):
    filters = {}
    for key in request.GET.keys():
        if not key.startswith('filter_'):
            continue
        value = request.GET.getlist(key)
        if len(value) == 1:
            value = value[0]
        filters[key.replace('filter_', '')] = value

    if filters:
        band = request.band
        shows = band.shows_count
        rehearsals = band.rehearsals_count
        if filters.get('date_from'):
            date = datetime.strptime(filters['date_from'], "%d/%m/%Y")
            items = items.filter(date__gte=date)
        if filters.get('date_to'):
            date = datetime.strptime(filters['date_to'], "%d/%m/%Y")
            items = items.filter(date__lte=date)
        if filters.get('song'):
            items = items.filter(song__name__icontains=filters['song'].strip())
        if filters.get('album'):
            items = items.filter(song__album__name__icontains=
                                                      filters['album'].strip())
        if filters.get('artist'):
            items = items.filter(song__album__artist__name__icontains=
                                                     filters['artist'].strip())
        if filters.get('mode[]'):
            modes = filters.get('mode[]')
            items = items.filter(song__mode__in=modes)
        if filters.get('status[]'):
            statuses = filters.get('status[]')
            items = items.filter(status__in=statuses)
        if filters.get('shows_above'):
            f = float(shows * int(filters['shows_above'])) / 100
            items = items.filter(in_shows_count__gte=f)
        if filters.get('shows_below'):
            f = float(shows * int(filters['shows_below'])) / 100
            items = items.filter(in_shows_count__lte=f)
        if filters.get('rehearsals_above'):
            f = float(rehearsals * int(filters['rehearsals_above'])) / 100
            items = items.filter(in_rehearsals_count__gte=f)
        if filters.get('rehearsals_below'):
            f = float(rehearsals * int(filters['rehearsals_below'])) / 100
            items = items.filter(in_rehearsals_count__lte=f)

    sort_by = request.GET.get('sort_by', '')
    sort = {}
    if sort_by:
        if sort_by.replace('-', '') == 'ratings':
            items = list(items)
            v = (-1, 1) if sort_by.startswith('-') else (1, -1)
            items.sort(lambda a, b: v[0] if a.ratings > b.ratings else v[1])
        else:
            items = items.order_by(sort_by)
        sort[sort_by] = True

    if filters.get('ratings_above'):
        items = [i for i in items if i.ratings >=
                                     int(filters['ratings_above'])]
    if filters.get('ratings_below'):
        items = [i for i in items if i.ratings <=
                                     int(filters['ratings_below'])]

    return items, sort

def get_repertory_content(request, repertory):
    user = request.user
    items = repertory.all_items.all()
    items, sort = _sort_repertory(request, items)
    tc = dict(
        repertory=repertory,
        sort=sort,
        items=items,
        trash=repertory.trash,
        players=Player.objects.all(),
        tonality_choices=get_tonality_choices(),
        mode_choices=SongMode.choices(),
        status_choices=RepertoryItemStatus.active_choices(),
        is_locked=repertory.is_locked(user),
        editable=repertory.is_editable(user),
        has_perm=user.has_perm('music.manage_main_repertory')
    )
    tc = RequestContext(request, tc)
    return loader.get_template("music/main_repertory_content.html").render(tc)

def get_repertories_statistics_content(request):
    band = request.band
    repertory = band.repertory
    items, sort = _sort_repertory(request, repertory.items)
    tc = dict(main_repertory=main_repertory, items=items, sort=sort, band=band)
    tc = RequestContext(request, tc)
    return loader.get_template("music/repertories_statistics_content.html")\
                 .render(tc)

@json
@login_required
def sort_main_repertory(request):
    repertory = request.band.repertory
    repertory_content = get_repertory_content(request, repertory)
    sort_by = request.GET.get('sort_by', '')
    return dict(success=True, repertory_content=repertory_content,
                sort_by=sort_by)

@json
@login_required
def sort_repertories_statistics(request):
    repertory_content = get_repertories_statistics_content(request)
    sort_by = request.GET.get('sort_by', '')
    return dict(success=True, repertory_content=repertory_content,
                sort_by=sort_by)

def get_trash_content(request, repertory):
    user = request.user
    tc = dict(
        repertory=repertory,
        editable=repertory.is_editable(user),
        has_perm=user.has_perm('music.manage_main_repertory')
    )
    tc = RequestContext(request, tc)
    return loader.get_template("music/main_repertory_trash.html").render(tc)

@json
@login_required
@ajax_check_locked_repertory_item
@permission_required('music.manage_main_repertory', '/permission/denied/')
def purge_song_from_main_repertory(request, id):
    item = get_object_or_404(RepertoryItem, id=id)
    repertory = item.repertory
    summary = 'item "%s" has been purged (removed from trash).' % item
    item.delete()
    new_history_entry(request.user, repertory, summary)
    repertory_content = get_repertory_content(request, repertory)
    trash_content = get_trash_content(request, repertory)
    return dict(success=True, repertory_content=repertory_content,
                trash_content=trash_content)

@json
@login_required
@ajax_check_locked_repertory_item
@permission_required('music.manage_main_repertory', '/permission/denied/')
def restore_song_to_main_repertory(request, id):
    item = get_object_or_404(RepertoryItem, id=id)
    repertory = item.repertory
    item.restore()
    summary = 'item "%s" has been restore from trash.' % item
    new_history_entry(request.user, repertory, summary)
    repertory_content = get_repertory_content(request, repertory)
    trash_content = get_trash_content(request, repertory)
    return dict(success=True, repertory_content=repertory_content,
                trash_content=trash_content)

@json
@login_required
@ajax_check_locked_event_repertory_item
@permission_required('music.manage_event_repertories', '/permission/denied/')
def remove_song_from_event_repertory(request, id):
    item = get_object_or_404(EventRepertoryItem, id=id)
    order = item.order
    summary = 'item "%s" has been deleted.' % item
    item.delete()
    new_history_entry(request.user, item.repertory, summary)
    items = item.repertory.items.filter(order__gt=order).order_by('order')
    for item in items:
        item.order -= 1
        item.save()
    return dict(success=True)

@login_required
@json
@ajax_check_locked_event_repertory_item
@permission_required('music.manage_event_repertories', '/permission/denied/')
def move_event_repertory_item(request, id):
    user = request.user
    order = int(request.POST['order'])
    current_item = EventRepertoryItem.objects.get(id=id)
    repertory = current_item.repertory
    if current_item.order == order:
        tc = RequestContext(request, dict(repertory=repertory))
        c = dict(
            success=True,
            content=loader.get_template("music/event_repertory_content.html")\
                          .render(tc)
        )
        return c
    current_order = current_item.order
    current_item.number = -1 # aux
    current_item.save()
    if current_order < order:
        items = repertory.items.filter(order__lte=order,
                                       order__gt=current_order)\
                               .order_by('order')
        # update number
        for item in items:
            item.order -= 1
            item.save()
    else:
        items = repertory.items.filter(order__gte=order,
                                       order__lt=current_order)\
                                .order_by('-order')
        # update numbers
        for item in items:
            item.order += 1
            item.save()

    current_item.order = order
    current_item.save()
    new_history_entry(request.user, current_item, "has been moved.")
    tc = dict(
        repertory=repertory,
        editable=repertory.is_editable(user),
        has_perm=user.has_perm('music.manage_main_repertory')
    )
    tc = RequestContext(request, tc)
    c = dict(
        success=True,
        content=loader.get_template("music/event_repertory_content.html")\
                      .render(tc)
    )
    return c

@login_required
@render_to("music/add_instrument.html")
@permission_required('music.manage_music', '/permission/denied/')
def add_instrument(request):
    if request.POST:
        form = InstrumentForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            new_history_entry(request.user, form.instance, 'created', True)
            msg = _('The instrument was successfully added.')
            messages.add_message(request, messages.SUCCESS, msg)
            url = reverse('instruments')
            return HttpResponseRedirect(url)
    else:
        form = InstrumentForm
    return dict(form=form)

@json
@login_required
@permission_required('music.manage_music', '/permission/denied/')
def remove_instrument(request, id):
    instrument = get_object_or_404(Instrument, id=id)
    new_history_entry(request.user, instrument, "has been removed.")
    instrument.delete()
    return dict(success=True)

@render_to("music/instruments.html")
def instruments(request):
    instruments = Instrument.objects.all().order_by('name')
    tag_types = InstrumentTagType.objects.all()
    has_perm = request.user.has_perm('music.manage_music')
    return dict(instruments=instruments, tag_types=tag_types,
                has_perm=has_perm)

@json
@login_required
def add_player(request, id, user_id):
    data = dict(instrument=id, user=user_id)
    form = PlayerForm(data=data)
    user = request.user
    if form.is_valid():
        form.save()
        new_history_entry(request.user, form.instance, 'created', True)
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
    item = get_object_or_404(RepertoryItem, id=id)
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
    item = player_repertory_item.item
    repertory = item.repertory
    c = dict(
        player_repertory_item=player_repertory_item,
        tag_types=tag_types,
        editable=repertory.is_editable(user),
        has_perm=user.has_perm('music.manage_main_repertory')
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
@permission_required('music.manage_main_repertory', '/permission/denied/')
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
@permission_required('music.manage_main_repertory', '/permission/denied/')
def change_as_member_options(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    artist = player_repertory_item.item.song.album.artist
    as_member = player_repertory_item.as_member
    members = [i for i in artist.active_members if i.id != as_member.id]
    template = loader.get_template("music/change_as_member_options.html")
    c = dict(members=members, player_repertory_item=player_repertory_item)
    context = RequestContext(request, c)
    return dict(success=True, content=template.render(context))

@json
@login_required
@ajax_check_locked_player_repertory_item
@permission_required('music.manage_main_repertory', '/permission/denied/')
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
@permission_required('music.manage_main_repertory', '/permission/denied/')
def change_player_user(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    item = player_repertory_item.item
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
@permission_required('music.manage_main_repertory', '/permission/denied/')
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
@permission_required('music.manage_main_repertory', '/permission/denied/')
def change_notes(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    player_repertory_item.notes = request.POST['notes']
    player_repertory_item.save()
    new_history_entry(request.user, player_repertory_item, "notes changed.")
    return dict(success=True)

@json
@login_required
@ajax_check_locked_player_repertory_item
@permission_required('music.manage_main_repertory', '/permission/denied/')
def add_document_for_player_repertory_item(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    data = dict(player_repertory_item=player_repertory_item.id)
    form = DocumentPlayerRepertoryItemForm(data=data, files=request.FILES)
    if form.is_valid():
        doc = form.save()
        summary = 'created for "%s (%s)"' % (player_repertory_item,
                                             player_repertory_item.id)
        new_history_entry(request.user, doc, summary, True)
        c = player_repertory_item_menu_content(request, player_repertory_item)
        c['success'] = True
        return c
    else:
        return dict(success=False)

@json
@login_required
@ajax_check_locked_player_repertory_item
@permission_required('music.manage_main_repertory', '/permission/denied/')
def remove_document_for_player_repertory_item(request, id, document_id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    document = player_repertory_item.documents.get(id=document_id)
    document.delete()
    summary = 'document "%s (%s)" has been removed.' % (document, document.id)
    new_history_entry(request.user, player_repertory_item, summary)
    c = player_repertory_item_menu_content(request, player_repertory_item)
    c['success'] = True
    return c

def get_main_repertory_item_content(request, item):
    user = request.user
    repertory = item.repertory
    temp = loader.get_template("music/main_repertory_item_content.html")
    tonality_choices = get_tonality_choices()
    c = {
        'item': item,
        'repertory': repertory,
        'tonality_choices': tonality_choices,
        'mode_choices': SongMode.choices(),
        'status_choices': RepertoryItemStatus.active_choices(),
        'editable': repertory.is_editable(user),
        'has_perm': user.has_perm('music.manage_main_repertory')
    }
    return temp.render(RequestContext(request, c))

def get_event_repertory_item_content(request, item):
    user = request.user
    repertory = item.repertory
    temp = loader.get_template("music/event_repertory_item_content.html")
    c = {
        'item': item,
        'repertory': repertory,
        'editable': repertory.is_editable(user),
        'has_perm': user.has_perm('music.manage_main_repertory')
    }
    return temp.render(RequestContext(request, c))

@json
@login_required
def update_main_repertory_item_content(request, id):
    item = get_object_or_404(RepertoryItem, id=id)
    content = get_main_repertory_item_content(request, item)
    return dict(success=True, content=content, item_id=item.id)

@json
@login_required
def rate_repertory_item(request, id):
    user = request.user
    item = get_object_or_404(RepertoryItem, id=id)
    rate = int(request.POST['rate'])
    try:
        rating = UserRepertoryItemRating.objects.get(user=user, item=item)
    except UserRepertoryItemRating.DoesNotExist:
        rating = UserRepertoryItemRating(user=user, item=item)
    rating.rate = rate
    rating.save()
    content = get_main_repertory_item_content(request, item)
    return dict(success=True, content=content, item_id=item.id)

@json
@login_required
def rate_event_repertory_item(request, id):
    user = request.user
    event_item = get_object_or_404(EventRepertoryItem, id=id)
    item = event_item.item
    rate = int(request.POST['rate'])
    try:
        rating = UserRepertoryItemRating.objects.get(user=user, item=item)
    except UserRepertoryItemRating.DoesNotExist:
        rating = UserRepertoryItemRating(user=user, item=item)
    rating.rate = rate
    rating.save()
    content = get_event_repertory_item_content(request, event_item)
    return dict(success=True, content=content, item_id=event_item.id)

@json
@login_required
def rate_player_repertory_item(request, id):
    user = request.user
    player_rep = get_object_or_404(PlayerRepertoryItem, id=id)
    rate = int(request.POST['rate'])
    is_main = int(request.POST['is_main'])
    event_id = int(request.POST.get('event_id', 0))
    try:
        rating = PlayerRepertoryItemRating.objects.get(user=user,
                                              player_repertory_item=player_rep)
    except PlayerRepertoryItemRating.DoesNotExist:
        rating = PlayerRepertoryItemRating(user=user,
                                           player_repertory_item=player_rep)
    rating.rate = rate
    rating.save()
    item = player_rep.item
    if is_main:
        content = get_main_repertory_item_content(request, item)
    else:
        item = EventRepertoryItem.objects.get(id=event_id)
        content = get_event_repertory_item_content(request, item)
    return dict(success=True, content=content, item_id=item.id)

@json
@login_required
@ajax_check_locked_repertory_item
@permission_required('music.manage_main_repertory', '/permission/denied/')
def add_player_repertory_item(request, id):
    data = request.POST
    data = dict(
        item=id,
        player=data['player_id'],
        as_member=data.get('member_id') or None,
        tag_types=data.getlist('tag_types[]', [])
    )
    form = PlayerRepertoryItemForm(data=data)
    if form.is_valid():
        form.save()
        new_history_entry(request.user, form.instance, "created", True)
        item = form.instance.item
        content = get_main_repertory_item_content(request, item)
        return dict(success=True, content=content, item_id=item.id)
    return dict(success=False, message=str(form.errors))

@json
@login_required
@ajax_check_locked_player_repertory_item
@permission_required('music.manage_main_repertory', '/permission/denied/')
def remove_player_repertory_item(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    item = player_repertory_item.item
    player_repertory_item.delete()
    content = get_main_repertory_item_content(request, item)
    return dict(success=True, content=content, item_id=item.id)

@json
@login_required
@ajax_check_locked_player_repertory_item
@permission_required('music.manage_main_repertory', '/permission/denied/')
def player_set_as_lead(request, id):
    player_repertory_item = get_object_or_404(PlayerRepertoryItem, id=id)
    player_repertory_item.is_lead = bool(int(request.POST.get('is_lead')))
    player_repertory_item.save()
    summary = "change is lead as %s" % player_repertory_item.is_lead
    new_history_entry(request.user, player_repertory_item, summary)
    item = player_repertory_item.item
    content = get_main_repertory_item_content(request, item)
    return dict(success=True, content=content, item_id=item.id)

@login_required
@render_to("music/add_instrument_tag_type.html")
@permission_required('music.manage_music', '/permission/denied/')
def add_instrument_tag_type(request):
    if request.POST:
        form = InstrumentTagTypeForm(data=request.POST)
        if form.is_valid():
            form.save()
            new_history_entry(request.user, form.instance, "created", True)
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
