from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.conf import settings

from user.models import Profile
from entities.models import Entity

class DefaultEntity(object):
    def process_request(self, request):
        ''' finding a default entity - first the user locality, then the
            `QNA_DEFAULT_ENTITY_ID` settings and lastly, a random place
        '''
        if request.path == '/':
            if request.user.is_authenticated():
                entity = request.user.profile.locality
            else:
                try:
                    entity_id = settings.QNA_DEFAULT_ENTITY_ID
                    entity = Entity.objects.get(pk=entity_id)
                except:
                    entity = Entity.objects.order_by('?')[0]

            return HttpResponseRedirect(reverse('local_home', kwargs={
                            'entity_slug': entity.slug}))

