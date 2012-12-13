from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^repertorios/$', views.repertories, name='repertories'),
    url(r'^repertorios/add/$', views.add_repertory, name='add_repertory'),
    url(r'^repertorios/(?P<id>\d+)/$', views.repertory_details, name='repertory_details'),
    url(r'^repertorios/(?P<id>\d+)/group/add/$', views.add_repertory_group, name='add_repertory_group'),
    url(r'^repertorios/(?P<id>\d+)/group/(?P<group_id>\d+)/remove/$', views.remove_repertory_group, name='remove_repertory_group'),
    url(r'^repertorios/(?P<id>\d+)/group/(?P<group_id>\d+)/move/$', views.move_repertory_group, name='move_repertory_group'),

    url(r'^management/$', views.music_management, name='music_management'),
    url(r'^management/album/add/$', views.add_album, name='add_album'),
    url(r'^management/album/search/$', views.search_albums, name='search_albums'),
    url(r'^management/album/search/resource/$', views.get_album_resource, name='get_album_resource'),
    url(r'^management/album/add/register/$', views.register_album, name='register_album'),
    url(r'^management/album/custom/$', views.custom_album_creation, name='custom_album_creation'),

    url(r'^busca/$', views.search_song_by_name, name='search_song_by_name'),
)