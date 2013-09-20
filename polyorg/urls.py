from django.conf.urls import url, patterns
from views import *

urlpatterns = patterns('polyorg.views',
        url(r'list/$', 'candidatelists_list', name='candidate-list-list'),
        url(r'list/create/$', 'candidatelist_create', name='candidate-list-create'),
        url(r'list/(?P<candidatelist_id>[-\w]+)$', 'candidates_list', name='candidate-list'),
        url(r'list/(?P<candidatelist_id>[-\w]+)/create/$', 'candidate_create', name='candidate-create')
    )
