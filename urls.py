from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView
admin.autodiscover()

js_info_dict = {
    'packages': ('your.app.package',),
}

urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'auth/', include('auth.urls')),
)

urlpatterns += patterns('',
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    url(r'^fbchannel.html', TemplateView.as_view(template_name="channel.html"), name="facebook_channel"),
    url(r'eventos/', include('event.urls')),
    url(r'videos/', include('video.urls')),
    url(r'fotos/', include('photo.urls')),
    url(r'contato/', include('contact.urls')),
    url(r'draft/', include('draft.urls')),
    url(r'busca/', include('search.urls')),
    url(r'', include('section.urls')),
    url(r'^admin/', include(admin.site.urls))
)
