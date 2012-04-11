from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^(?P<id>\d+)/$', views.event_details, name='event_details'),
    url(r'^historico/$', views.event_history, name='event_history'),
    url(r'^locais/$', views.location_list, name='location_list'),
    url(r'^locais/(?P<id>\d+)/$', views.location_details, name='location_details'),
)