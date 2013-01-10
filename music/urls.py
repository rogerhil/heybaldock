from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^band/add/$', views.add_band, name='add_band'),
    url(r'^band/(?P<id>\d+)/$', views.band_settings, name='band_settings'),

    url(r'^rehearsal/$', views.rehearsals, name='rehearsals'),
    url(r'^rehearsal/add/$', views.add_rehearsal, name='add_rehearsal'),
    url(r'^rehearsal/(?P<id>\d+)/$', views.rehearsal, name='rehearsal'),
    url(r'^rehearsal/(?P<id>\d+)/change/$', views.change_rehearsal, name='change_rehearsal'),
    url(r'^rehearsal/(?P<id>\d+)/delete/$', views.remove_rehearsal, name='remove_rehearsal'),

    url(r'^repertory/$', views.repertories, name='repertories'),
    url(r'^repertory/players_menu/(?P<id>\d+)/$', views.players_menu, name='players_menu'),
    url(r'^repertory/repertory_item/(?P<id>\d+)/player/(?P<player_id>\d+)/add/$', views.add_player_repertory_item, name='add_player_repertory_item'),
    url(r'^repertory/repertory_item/(?P<id>\d+)/change_tonality/$', views.change_repertory_item_tonality, name='change_repertory_item_tonality'),
    url(r'^repertory/repertory_item/(?P<id>\d+)/change_mode/$', views.change_repertory_item_song_mode, name='change_repertory_item_song_mode'),
    url(r'^repertory/repertory_item/(?P<id>\d+)/update_song_line_repertory_content/$', views.update_song_line_repertory_content, name='update_song_line_repertory_content'),
    url(r'^repertory/repertory_item/(?P<id>\d+)/rate/$', views.rate_repertory_item, name='rate_repertory_item'),
    url(r'^repertory/player_repertory_item/(?P<id>\d+)/menu/$', views.player_repertory_item_menu, name='player_repertory_item_menu'),
    url(r'^repertory/player_repertory_item/(?P<id>\d+)/remove/$', views.remove_player_repertory_item, name='remove_player_repertory_item'),
    url(r'^repertory/player_repertory_item/(?P<id>\d+)/set_as_lead/$', views.player_set_as_lead, name='player_set_as_lead'),
    url(r'^repertory/player_repertory_item/(?P<id>\d+)/toogle_tag_type/$', views.toogle_tag_type, name='toogle_tag_type'),
    url(r'^repertory/player_repertory_item/(?P<id>\d+)/change_as_member_options/$', views.change_as_member_options, name='change_as_member_options'),
    url(r'^repertory/player_repertory_item/(?P<id>\d+)/change_as_member/$', views.change_as_member, name='change_as_member'),
    url(r'^repertory/player_repertory_item/(?P<id>\d+)/change_player_user_options/$', views.change_player_user_options, name='change_player_user_options'),
    url(r'^repertory/player_repertory_item/(?P<id>\d+)/change_player_user/$', views.change_player_user, name='change_player_user'),
    url(r'^repertory/player_repertory_item/(?P<id>\d+)/change_notes/$', views.change_notes, name='change_notes'),
    url(r'^repertory/player_repertory_item/(?P<id>\d+)/document/add/$', views.add_document_for_player_repertory_item, name='add_document_for_player_repertory_item'),
    url(r'^repertory/player_repertory_item/(?P<id>\d+)/document/(?P<document_id>\d+)/remove/$', views.remove_document_for_player_repertory_item, name='remove_document_for_player_repertory_item'),
    url(r'^repertory/player_repertory_item/(?P<id>\d+)/rate/$', views.rate_player_repertory_item, name='rate_player_repertory_item'),

    url(r'^repertory/add/$', views.add_repertory, name='add_repertory'),
    url(r'^repertory/(?P<id>\d+)/$', views.repertory_details, name='repertory_details'),
    url(r'^repertory/(?P<id>\d+)/remove/$', views.remove_repertory, name='remove_repertory'),
    url(r'^repertory/(?P<id>\d+)/group/add/$', views.add_repertory_group, name='add_repertory_group'),
    url(r'^repertory/(?P<id>\d+)/group/(?P<group_id>\d+)/remove/$', views.remove_repertory_group, name='remove_repertory_group'),
    url(r'^repertory/(?P<id>\d+)/group/(?P<group_id>\d+)/move/$', views.move_repertory_group, name='move_repertory_group'),
    url(r'^repertory/(?P<id>\d+)/group/(?P<group_id>\d+)/song/(?P<song_id>\d+)/add/$', views.add_song_to_repertory, name='add_song_to_repertory'),
    url(r'^repertory/(?P<id>\d+)/group/(?P<group_id>\d+)/item/(?P<item_id>\d+)/move/$', views.move_song, name='move_song'),
    url(r'^repertory/(?P<id>\d+)/group/(?P<group_id>\d+)/item/(?P<item_id>\d+)/remove/$', views.remove_song_from_repertory, name='remove_song_from_repertory'),

    url(r'^$', views.music_management, name='music_management'),
    url(r'^album/add/$', views.add_album, name='add_album'),
    url(r'^album/add/custom_form/$', views.custom_album_creation, name='custom_album_creation'),
    url(r'^album/add/register/$', views.register_album, name='register_album'),
    url(r'^album/song/add_to_main_pertory/$', views.add_song_to_main_repertory, name='add_song_to_main_repertory'),
    url(r'^album/(?P<id>\d+)/$', views.album, name='album'),
    url(r'^album/(?P<id>\d+)/remove/$', views.remove_album, name='remove_album'),
    url(r'^artist/$', views.artists, name='artists'),
    url(r'^artist/(?P<id>\d+)/$', views.artist_details, name='artist_details'),
    url(r'^artist/(?P<id>\d+)/albums/$', views.artist_albums, name='artist_albums'),
    url(r'^song/(?P<id>\d+)/change_tempo/$', views.change_tempo_signature, name='change_tempo_signature'),
    url(r'^song/(?P<id>\d+)/change_tonality/$', views.change_tonality, name='change_tonality'),
    url(r'^song/(?P<id>\d+)/audio/upload/$', views.upload_song_audio, name='upload_song_audio'),

    url(r'^instrument/$', views.instruments, name='instruments'),
    url(r'^instrument/add/$', views.add_instrument, name='add_instrument'),
    url(r'^instrument/(?P<id>\d+)/remove/$', views.remove_instrument, name='remove_instrument'),
    url(r'^instrument/(?P<id>\d+)/user/(?P<user_id>\d+)/add/$', views.add_player, name='add_player'),
    url(r'^instrument/(?P<id>\d+)/user/(?P<user_id>\d+)/remove/$', views.remove_player, name='remove_player'),
    url(r'^instrument/players_to_add/$', views.players_to_add, name='players_to_add'),
    url(r'^instrument/tag_type/$', views.instrument_tag_types, name='instrument_tag_types'),
    url(r'^instrument/tag_type/add/$', views.add_instrument_tag_type, name='add_instrument_tag_type'),

    url(r'^busca/$', views.search_song_by_name, name='search_song_by_name'),

    url(r'^history/$', views.music_history, name='music_history'),
)