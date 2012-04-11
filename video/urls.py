from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^album/(?P<id>\d+)/$', views.video_album_view, name='video_album_view'),
    url(r'^url_validate_and_details/ajax/$', views.url_validate_and_details, name='video_url_validate_and_details'),
)
