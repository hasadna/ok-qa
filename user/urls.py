from django.conf.urls.defaults import patterns, url
from .views import *
from .feeds import *

urlpatterns = patterns('',
    url(r'^u/profile/$', edit_profile, name='edit_profile'),
    url(r'^u/password_change/$', 'django.contrib.auth.views.password_change', name='password_change'),
    url(r'^u/password_change/done/$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),
    url(r'^u/follow/$', 'user_follow_unfollow', name='user-follow-unfollow'),
    url(r'^u/(?P<candidate_id>\d+)/atom/$',
        AtomUserAnswerFeed(),
        name='user_feed'
    ),
    url(r'^u/logout/$', 'django.contrib.auth.views.logout',
                                  {'next_page': '/'},
                                  name="logout"),
    url(r'^u/login/$', 'django.contrib.auth.views.login',
                                  name='login'),
    url(r'^u/editor_lists/$', editor_list, name='editor_list'),

    #TODO: refactor to user underscore in name i.e. `public_profile`
    url(r'^(?P<username>.+)/$', public_profile, name="public-profile"),
)
