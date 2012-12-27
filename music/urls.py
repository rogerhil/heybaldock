from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^repertorios/$', views.repertories, name='repertories'),
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



    url(r'^busca/$', views.search_song_by_name, name='search_song_by_name'),
)