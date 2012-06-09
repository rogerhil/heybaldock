from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^heybaldock/', include('heybaldock.foo.urls')),
    url(r'auth/', include('heybaldock.auth.urls')),
    url(r'eventos/', include('heybaldock.event.urls')),
    url(r'videos/', include('heybaldock.video.urls')),
    url(r'fotos/', include('heybaldock.photo.urls')),
    url(r'contato/', include('heybaldock.contact.urls')),
    url(r'draft/', include('heybaldock.draft.urls')),
    url(r'', include('heybaldock.section.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )