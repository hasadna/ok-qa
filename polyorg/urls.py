from django.conf.urls import url, patterns
from views import *

urlpatterns = patterns('polyorg.views',
        url(r'list/$', 'candiatelists_list', name='candidate-list-list'),
        url(r'list/create/$', 'candiatelist_create', name='candidate-list-create'),
        url(r'list/(?P<candidatelist_id>[-\w]+)$', 'candiates_list', name='candidate-list'),
        url(r'list/(?P<candidatelist_id>[-\w]+)/create/$', 'candiate_create', name='candidate-create')
    )
