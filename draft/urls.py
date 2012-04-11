from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^(?P<id>\d+)/$', views.view, name='view_draft'),
    url(r'^(?P<model>\w+)/add/$', views.add_new, name='add_draft_new'),
    url(r'^(?P<model>\w+)/(?P<id>\d+)/add/$', views.add, name='add_draft'),
    url(r'^(?P<id>\d+)/edit/$', views.edit, name='edit_draft'),
    url(r'^(?P<id>\d+)/publish/$', views.publish, name='publish_draft'),
    url(r'^(?P<id>\d+)/delete/$', views.delete, name='delete_draft'),
)
