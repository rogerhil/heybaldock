from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^profile/$', views.profile, name='profile'),
)