from django.conf.urls.defaults import patterns, url

import views

urlpatterns = patterns('',
    url(r'^send_mail/$', views.send_mail, name='contact_send_mail'),
)
