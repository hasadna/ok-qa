from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _

class LocalityMiddleware(object):
    def process_request(self, request):
        profile_path = reverse('edit_profile')
        if request.path != profile_path and request.user.is_authenticated() and\
           not request.user.profile.locality:
            messages.warning(request,
                           _('Please first set your place'))
            return HttpResponseRedirect('%s?next=%s' % (profile_path, request.path))
