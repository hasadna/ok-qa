from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _

from user.models import Profile

# TODO: remove this
class LocalityMiddleware(object):
    def process_request(self, request):
        profile_path = reverse('edit_profile')
        if request.user.is_authenticated() and \
           not request.path in (reverse('logout'), profile_path):
            profile, created = Profile.objects.get_or_create(user=request.user)
            if not profile.locality:
                messages.warning(request,
                               _('Please first set your place'))
                return HttpResponseRedirect('%s?next=%s' % (profile_path, request.path))
