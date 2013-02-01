from django.conf.urls.defaults import patterns, url

import views

urlpatterns = patterns('',
    url(r'^send_mail/$', views.send_mail, name='contact_send_mail'),
    url(r'^notification/notify/(?P<app>\w+)/(?P<model>\w+)/(?P<id>\d+)/(?P<action>\w+)/$', views.notify, name='notify'),
    url(r'^notification/my/$', views.my_notifications, name='my_notifications'),
    url(r'^notification/my/count/$', views.my_notifications_count, name='my_notifications_count'),
    url(r'^notification/(?P<id>\d+)/template/test/$', views.notification_template_test, name='notification_template_test'),
    url(r'^notification/user/(?P<id>\d+)/content/$', views.user_notification_content, name='user_notification_content'),
)
