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
    url(r'^repertory/main/$', views.main_repertory, name='main_repertory'),
    url(r'^repertory/main/sort/$', views.sort_main_repertory, name='sort_main_repertory'),
    url(r'^repertory/main/song/search/$', views.search_song_by_name, name='search_song_by_name'),
    url(r'^repertory/main/song/add/$', views.add_song_to_main_repertory, name='add_song_to_main_repertory'),
    url(r'^repertory/main/item/(?P<id>\d+)/remove/$', views.remove_song_from_main_repertory, name='remove_song_from_main_repertory'),
    url(r'^repertory/main/item/(?P<id>\d+)/purge/$', views.purge_song_from_main_repertory, name='purge_song_from_main_repertory'),
    url(r'^repertory/main/item/(?P<id>\d+)/restore/$', views.restore_song_to_main_repertory, name='restore_song_to_main_repertory'),
    url(r'^repertory/main/item/(?P<id>\d+)/update_content/$', views.update_main_repertory_item_content, name='update_main_repertory_item_content'),
    url(r'^repertory/main/item/(?P<id>\d+)/tonality/change/$', views.change_repertory_item_tonality, name='change_repertory_item_tonality'),
    url(r'^repertory/main/item/(?P<id>\d+)/mode/change/$', views.change_repertory_item_song_mode, name='change_repertory_item_song_mode'),
    url(r'^repertory/main/item/(?P<id>\d+)/status/change/$', views.change_repertory_item_status, name='change_repertory_item_status'),
    url(r'^repertory/main/item/(?P<id>\d+)/date/change/$', views.change_repertory_item_date, name='change_repertory_item_date'),
    url(r'^repertory/main/item/(?P<id>\d+)/rate/$', views.rate_repertory_item, name='rate_repertory_item'),
    url(r'^repertory/main/item/(?P<id>\d+)/player/menu/$', views.players_menu, name='players_menu'),
    url(r'^repertory/main/item/(?P<id>\d+)/player/add/$', views.add_player_repertory_item, name='add_player_repertory_item'),
    url(r'^repertory/main/item/player/(?P<id>\d+)/menu/$', views.player_repertory_item_menu, name='player_repertory_item_menu'),
    url(r'^repertory/main/item/player/(?P<id>\d+)/remove/$', views.remove_player_repertory_item, name='remove_player_repertory_item'),
    url(r'^repertory/main/item/player/(?P<id>\d+)/set_as_lead/$', views.player_set_as_lead, name='player_set_as_lead'),
    url(r'^repertory/main/item/player/(?P<id>\d+)/toogle_tag_type/$', views.toogle_tag_type, name='toogle_tag_type'),
    url(r'^repertory/main/item/player/(?P<id>\d+)/change_as_member_options/$', views.change_as_member_options, name='change_as_member_options'),
    url(r'^repertory/main/item/player/(?P<id>\d+)/change_as_member/$', views.change_as_member, name='change_as_member'),
    url(r'^repertory/main/item/player/(?P<id>\d+)/change_player_user_options/$', views.change_player_user_options, name='change_player_user_options'),
    url(r'^repertory/main/item/player/(?P<id>\d+)/change_player_user/$', views.change_player_user, name='change_player_user'),
    url(r'^repertory/main/item/player/(?P<id>\d+)/change_notes/$', views.change_notes, name='change_notes'),
    url(r'^repertory/main/item/player/(?P<id>\d+)/document/add/$', views.add_document_for_player_repertory_item, name='add_document_for_player_repertory_item'),
    url(r'^repertory/main/item/player/(?P<id>\d+)/document/(?P<document_id>\d+)/remove/$', views.remove_document_for_player_repertory_item, name='remove_document_for_player_repertory_item'),
    url(r'^repertory/main/item/player/(?P<id>\d+)/rate/$', views.rate_player_repertory_item, name='rate_player_repertory_item'),

    url(r'^repertory/event/add/$', views.add_event_repertory, name='add_event_repertory'),
    url(r'^repertory/event/add_for_rehearsal/(?P<id>\d+)/$', views.add_event_repertory_for_rehearsal, name='add_event_repertory_for_rehearsal'),
    url(r'^repertory/event/add_for_event/(?P<id>\d+)/$', views.add_event_repertory_for_event, name='add_event_repertory_for_event'),
    url(r'^repertory/event/(?P<id>\d+)/$', views.event_repertory, name='event_repertory'),
    url(r'^repertory/event/(?P<id>\d+)/remove/$', views.remove_event_repertory, name='remove_event_repertory'),
    url(r'^repertory/event/(?P<id>\d+)/item/add/$', views.add_item_to_event_repertory, name='add_item_to_event_repertory'),
    url(r'^repertory/event/(?P<id>\d+)/item/interval/add/$', views.add_event_repertory_item_interval, name='add_event_repertory_item_interval'),
    url(r'^repertory/event/(?P<id>\d+)/item/search/$', views.search_item_by_name, name='search_item_by_name'),
    url(r'^repertory/event/(?P<id>\d+)/items/add/by_category/$', views.add_event_repertory_items_by_category, name='add_event_repertory_items_by_category'),
    url(r'^repertory/event/item/(?P<id>\d+)/remove/$', views.remove_song_from_event_repertory, name='remove_song_from_event_repertory'),
    url(r'^repertory/event/item/(?P<id>\d+)/move/$', views.move_event_repertory_item, name='move_event_repertory_item'),
    url(r'^repertory/event/item/(?P<id>\d+)/rate/$', views.rate_event_repertory_item, name='rate_event_repertory_item'),
    url(r'^repertory/event/item/(?P<id>\d+)/times_played/$', views.change_event_repertory_item_times_played, name='change_event_repertory_item_times_played'),


    url(r'^$', views.music_management, name='music_management'),
    url(r'^album/add/$', views.add_album, name='add_album'),
    url(r'^album/add/custom_form/$', views.custom_album_creation, name='custom_album_creation'),
    url(r'^album/add/register/$', views.register_album, name='register_album'),
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

    url(r'^history/$', views.music_history, name='music_history'),
)