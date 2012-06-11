from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^album/(?P<id>\d+)/$', views.photo_album_view, name='photo_album_view'),
    url(r'^album/delete/(?P<id>\d+)/$', views.delete_photo_album, name='delete_photo_album'),
    url(r'^upload/ajax/$', views.upload_ajax, name='photo_upload_ajax'),
    url(r'^cancel_upload/ajax/$', views.cancel_upload_ajax, name='photo_cancel_upload_ajax'),
)
