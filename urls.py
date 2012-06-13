from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView
admin.autodiscover()

js_info_dict = {
    'packages': ('your.app.package',),
}

urlpatterns = patterns('',
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    url(r'^fbchannel.html', TemplateView.as_view(template_name="channel.html"), name="facebook_channel")
)

if settings.COMMING_SOON:
    urlpatterns += patterns('',
        url(r'^$', TemplateView.as_view(template_name="coming_soon.html"), name="comming_soon")
    )
elif settings.UNDER_MAINTENANCE:
    urlpatterns += patterns('',
        url(r'^$', TemplateView.as_view(template_name="under_maintenance.html"), name="comming_soon")
    )
else:
    urlpatterns += patterns('',
        url(r'auth/', include('heybaldock.auth.urls')),
        url(r'eventos/', include('heybaldock.event.urls')),
        url(r'videos/', include('heybaldock.video.urls')),
        url(r'fotos/', include('heybaldock.photo.urls')),
        url(r'contato/', include('heybaldock.contact.urls')),
        url(r'draft/', include('heybaldock.draft.urls')),
        url(r'busca/', include('heybaldock.search.urls')),
        url(r'', include('heybaldock.section.urls')),
        url(r'^admin/', include(admin.site.urls)),
    )

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )