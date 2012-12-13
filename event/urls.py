from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^(?P<id>\d+)/$', views.event_details, name='event_details'),
    url(r'^historico/$', views.event_history, name='event_history'),
    url(r'^delete/(?P<slug>\w+)/$', views.delete_event, name='delete_event'),
    url(r'^locais/$', views.location_list, name='location_list'),
    url(r'^locais/(?P<id>\d+)/$', views.location_details, name='location_details'),
    url(r'^locais/address_by_zipcode/ajax/$', views.address_by_zipcode, name='location_address_by_zipcode_ajax'),
    url(r'^locais/delete/(?P<id>\d+)/$', views.delete_location, name='delete_location'),
)
