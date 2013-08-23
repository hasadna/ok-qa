from django.conf.urls.defaults import patterns, include, url
from .views import *
from .feeds import *

urlpatterns = patterns('',
    url(r'^profile/$', edit_profile, name='edit_profile'),
    url(r'^candidate/$', edit_candidate, name='edit_candidate'),
    url(r'^candidates/$', candidate_list, name="candidate_list"),
    url(r'^follow/$', 'user_follow_unfollow', name='user-follow-unfollow'),
    url(r'^(?P<entity_id>[-\d]+)/candidates/$', candidate_list, name="candidate_list"),
    url(r'^(?P<entity_slug>.*)/candidates/$', candidate_list, name="candidate_list"),
    url(r'^candidate/(?P<candidate_id>\d+)/atom/$',
        AtomUserAnswerFeed(),
        name='user_feed'
    ),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
                                  {'next_page': '/'},
                                  name="logout"),
    url(r'^login/$', 'django.contrib.auth.views.login',
                                  name='login'),
    url(r'^invitation/(?P<invitation_key>\w+)/$',
        InvitationView.as_view(),
        name='accept-invitation'),
    url(r'^candidate/(?P<candidate_id>\d+)/remove/$',
        remove_candidate,
        name='remove_candidate'
    ),
    url(r'^(?P<username>.+)/$', public_profile, name="public-profile"),
)
