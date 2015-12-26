"""oshot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', 'oshot.views.home_page', name='home_page'),
    url(r'^pages/', include('django.contrib.flatpages.urls')),
    url(r'^avatar/', include('avatar.urls')),
    url(r'^s/', include('actstream.urls')),
    url(r'^po/', include('polyorg.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
    url(r'^robots\.txt',
        TemplateView.as_view(template_name='robots.txt')),
    url(r'^search/$', 'oshot.views.place_search'),
    url(r'^admin/', admin.site.urls),
    url(r'', include('qa.urls')),
    url(r'', include('social_auth.urls')),
    url(r'^(?P<entity_slug>[-\w]+)/search/$', 'oshot.views.place_search'),
    url(r'^u/entity_stats/$', 'oshot.views.entity_stats', name='entity_stats'),
    url(r'', include('user.urls')),
]
