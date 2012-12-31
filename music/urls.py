from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^repertorios/$', views.repertories, name='repertories'),
    url(r'^repertorios/players_menu/(?P<id>\d+)/$', views.players_menu, name='players_menu'),
    url(r'^repertorios/repertory_item/(?P<id>\d+)/player/(?P<player_id>\d+)/add/$', views.add_player_repertory_item, name='add_player_repertory_item'),
    url(r'^repertorios/player_repertory_item/(?P<id>\d+)/menu/$', views.player_repertory_item_menu, name='player_repertory_item_menu'),
    url(r'^repertorios/player_repertory_item/(?P<id>\d+)/remove/$', views.remove_player_repertory_item, name='remove_player_repertory_item'),
    url(r'^repertorios/player_repertory_item/(?P<id>\d+)/set_as_lead/$', views.player_set_as_lead, name='player_set_as_lead'),
    url(r'^repertorios/player_repertory_item/(?P<id>\d+)/toogle_tag_type/$', views.toogle_tag_type, name='toogle_tag_type'),
    url(r'^repertorios/player_repertory_item/(?P<id>\d+)/change_as_member_options/$', views.change_as_member_options, name='change_as_member_options'),
    url(r'^repertorios/player_repertory_item/(?P<id>\d+)/change_as_member/$', views.change_as_member, name='change_as_member'),
    url(r'^repertorios/player_repertory_item/(?P<id>\d+)/change_player_user_options/$', views.change_player_user_options, name='change_player_user_options'),
    url(r'^repertorios/player_repertory_item/(?P<id>\d+)/change_player_user/$', views.change_player_user, name='change_player_user'),
    url(r'^repertorios/player_repertory_item/(?P<id>\d+)/change_notes/$', views.change_notes, name='change_notes'),

    url(r'^repertorios/add/$', views.add_repertory, name='add_repertory'),
    url(r'^repertorios/(?P<id>\d+)/$', views.repertory_details, name='repertory_details'),
    url(r'^repertorios/(?P<id>\d+)/group/add/$', views.add_repertory_group, name='add_repertory_group'),
    url(r'^repertorios/(?P<id>\d+)/group/(?P<group_id>\d+)/remove/$', views.remove_repertory_group, name='remove_repertory_group'),
    url(r'^repertorios/(?P<id>\d+)/group/(?P<group_id>\d+)/move/$', views.move_repertory_group, name='move_repertory_group'),
    url(r'^repertorios/(?P<id>\d+)/group/(?P<group_id>\d+)/song/(?P<song_id>\d+)/add/$', views.add_song_to_repertory, name='add_song_to_repertory'),
    url(r'^repertorios/(?P<id>\d+)/group/(?P<group_id>\d+)/item/(?P<item_id>\d+)/move/$', views.move_song, name='move_song'),
    url(r'^repertorios/(?P<id>\d+)/group/(?P<group_id>\d+)/item/(?P<item_id>\d+)/remove/$', views.remove_song_from_repertory, name='remove_song_from_repertory'),

    url(r'^management/$', views.music_management, name='music_management'),
    url(r'^management/album/add/$', views.add_album, name='add_album'),
    url(r'^management/album/add/custom_form/$', views.custom_album_creation, name='custom_album_creation'),
    url(r'^management/album/add/register/$', views.register_album, name='register_album'),
    url(r'^management/album/song/add_to_main_pertory/$', views.add_song_to_main_repertory, name='add_song_to_main_repertory'),
    url(r'^management/album/(?P<id>\d+)/$', views.album, name='album'),
    url(r'^management/album/(?P<id>\d+)/remove/$', views.remove_album, name='remove_album'),
    url(r'^management/album/$', views.albums, name='albums'),
    url(r'^management/artist/$', views.artists, name='artists'),
    url(r'^management/artist/(?P<id>\d+)/$', views.artist_details, name='artist_details'),

    url(r'^management/instrument/$', views.instruments, name='instruments'),
    url(r'^management/instrument/add/$', views.add_instrument, name='add_instrument'),
    url(r'^management/instrument/(?P<id>\d+)/remove/$', views.remove_instrument, name='remove_instrument'),
    url(r'^management/instrument/(?P<id>\d+)/user/(?P<user_id>\d+)/add/$', views.add_player, name='add_player'),
    url(r'^management/instrument/(?P<id>\d+)/user/(?P<user_id>\d+)/remove/$', views.remove_player, name='remove_player'),
    url(r'^management/instrument/players_to_add/$', views.players_to_add, name='players_to_add'),
    url(r'^management/instrument/tag_type/$', views.instrument_tag_types, name='instrument_tag_types'),
    url(r'^management/instrument/tag_type/add/$', views.add_instrument_tag_type, name='add_instrument_tag_type'),

    url(r'^busca/$', views.search_song_by_name, name='search_song_by_name'),
)