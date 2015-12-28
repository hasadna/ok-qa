from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import Count

from entities.models import Entity

class DefaultEntity(object):
    def process_request(self, request):
        return # Election day - send everyone to the main homepage on default.
        if request.path == '/':
            if request.user.is_authenticated():
                try:
                    entity = request.user.profile.entities[0] # TODO #453
                except IndexError:
                    return HttpResponseRedirect(reverse('edit_profile'))
            else:
                return

            if entity:
                return HttpResponseRedirect(reverse('entity_home', kwargs={
                                'entity_id': entity.id}))
