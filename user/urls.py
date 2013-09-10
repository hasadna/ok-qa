from django.conf.urls.defaults import patterns, url
from .views import *
from .feeds import *

urlpatterns = patterns('',
    url(r'^u/profile/$', edit_profile, name='edit_profile'),
    url(r'^u/candidate/$', edit_candidate, name='edit_candidate'),
    url(r'^u/candidates/$', candidate_list, name="candidate_list"),
    url(r'^u/follow/$', 'user_follow_unfollow', name='user-follow-unfollow'),
    url(r'^(?P<entity_id>[-\d]+)/candidates/$', candidate_list, name="candidate_list"),
    url(r'^(?P<entity_slug>.*)/candidates/$', candidate_list, name="candidate_list"),
    url(r'^u/(?P<candidate_id>\d+)/atom/$',
        AtomUserAnswerFeed(),
        name='user_feed'
    ),
    url(r'^u/logout/$', 'django.contrib.auth.views.logout',
                                  {'next_page': '/'},
                                  name="logout"),
    url(r'^u/login/$', 'django.contrib.auth.views.login',
                                  name='login'),
    url(r'^u/invitation/(?P<invitation_key>\w+)/$',
        InvitationView.as_view(),
        name='accept-invitation'),
    url(r'^u/(?P<candidate_id>\d+)/remove/$',
        remove_candidate,
        name='remove_candidate'
    ),
    url(r'^(?P<username>.+)/$', public_profile, name="public-profile"),
)
