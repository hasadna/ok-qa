from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import Count

from entities.models import Entity

class DefaultEntity(object):
    def process_request(self, request):
        ''' finding a default entity - first the user locality, then the
            `QNA_DEFAULT_ENTITY_ID` settings and lastly, a random place
        '''
        if request.path == '/':
            if request.user.is_authenticated():
                entity = request.user.profile.locality
                if not entity:
                    return HttpResponseRedirect(reverse('edit_profile'))
            else:
                try:
                    entity = Entity.objects.annotate(Count('questions__answers'))\
                            .filter(questions__answers__count__gt=0)\
                            .exclude(pk=settings.QNA_DEFAULT_ENTITY_ID)\
                            .order_by('?')[0]
                except:
                    entity = Entity.objects.order_by('?')[0]

            if entity:
                return HttpResponseRedirect(reverse('local_home', kwargs={
                                'entity_id': entity.id}))

