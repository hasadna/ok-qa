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
        return # Election day - send everyone to the main homepage on default.
        if request.path == '/':
            if request.user.is_authenticated():
                entity = request.user.profile.locality
                if not entity:
                    return HttpResponseRedirect(reverse('edit_profile'))
            else:
                return

            if entity:
                return HttpResponseRedirect(reverse('local_home', kwargs={
                                'entity_id': entity.id}))
