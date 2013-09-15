from django.conf.urls import url, patterns
from views import *

urlpatterns = patterns('polyorg.views',
        url(r'list/$', 'candiatelists_list', name='candidate-list-list'),
        url(r'list/create/$', 'candiatelist_create', name='candidate-list-create')
    )
