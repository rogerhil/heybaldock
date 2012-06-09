from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^$', views.section_home, name='section_home'),
    url(r'^(?P<slug>\w+)/$', views.section_view, name='section_view', kwargs={'message': {}}),

)

