from django.conf.urls import url, patterns
from views import *

urlpatterns = patterns('polyorg.views',
        url(r'list/$', 'candidatelists_list', name='candidate-list-list'),
        url(r'list/entity/(?P<entity_id>[-\w]+)$', 'candidatelists_list', name='candidate-list-list'),
        url(r'list/create/$', 'candidatelist_edit', name='candidate-list-create'),
        url(r'list/create/(?P<entity_id>[-\w]+)$', 'candidatelist_edit', name='candidate-list-create'),
        url(r'list/(?P<candidatelist_id>[-\w]+)$', 'candidates_list', name='candidate-list'),
        url(r'list/(?P<candidatelist_id>[-\w]+)/create/$', 'candidate_create', name='candidate-create'),
        url(r'list/(?P<candidatelist_id>[-\w]+)/edit/$', 'candidatelist_edit', name='candidatelist-edit'),
        url(r'list/(?P<candidatelist_id>[-\w]+)/remove/(?P<candidate_id>[-\w]+)/$', 'candidate_remove', name='candidate_remove'),
    )
