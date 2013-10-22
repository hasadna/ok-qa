import os
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import get_current_site
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import Http404

from entities.models import Entity

from oshot.forms import EntityChoiceForm

# the url names of pages that have a special entity form
SPECIAL_ENTITY_FORM = ('user_detail', )
def forms(request):
    q = request.GET.get("q", False)
    context = {"search_query": q} if q else {}
    try:
        kwargs = request.resolver_match.kwargs
        # many ways to pass an entity
        entity = getattr(request, 'entity', None)
        if entity:
            pass
        elif 'entity_id' in kwargs:
            entity = get_object_or_404(Entity, pk=kwargs['entity_id'])
        elif 'entity_slug' in kwargs:
            entity = get_object_or_404(Entity, slug=kwargs['entity_slug'])
        elif request.user.is_authenticated():
            entity = request.user.profile.locality

        context['entity'] = entity
        context['questions_url'] = reverse("home_page")
        context['entity_form'] = EntityChoiceForm(initial={}, auto_id=False)

    except (AttributeError, Http404):
        pass

    if request.user.is_authenticated():
        context["profile"] = request.user.profile
    else:
        context["login_form"] = AuthenticationForm()
    context["site"] = get_current_site(request)
    context["ANALYTICS_ID"] = getattr(settings, 'ANALYTICS_ID', False)
    context["FACEBOOK_APP_ID"] = os.environ.get('FACEBOOK_APP_ID', '')

    return context


