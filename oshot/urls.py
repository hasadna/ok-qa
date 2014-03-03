import os
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from entities.views.ui import EntityDetail, EntityList

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'oshot.views.home_page', name="home_page"),
    url(r'^home$', 'oshot.views.home_page'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^p/(?P<url>.*)$', 'django.contrib.flatpages.views.flatpage'),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^robots\.txt',
        TemplateView.as_view(template_name='robots.txt')
    ),

    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'', include('qa.urls')),
    url(r'', include('social_auth.urls')),
    url(r'^search/$', 'oshot.views.place_search'),
    url(r'^(?P<entity_slug>[-\w]+)/search/$', 'oshot.views.place_search'),
    (r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
    (r'^avatar/', include('avatar.urls')),
    (r'^s/', include('actstream.urls')),
    (r'^po/', include('polyorg.urls')),
    # flat pages to help with static pages
    # user.url has to be last as it handles /[username]
    url(r'^u/entity_stats/$', 'oshot.views.entity_stats', name='entity_stats'),
    url(r'', include('user.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if 'DEV' in os.environ:
    urlpatterns += staticfiles_urlpatterns() + \
                   static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
