import os
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import get_current_site
from django.conf import settings

from entities.models import Entity

from oshot.forms import EntityChoiceForm

# the url names of pages that have a special entity form
SPECIAL_ENTITY_FORM = ('user_detail', )
def forms(request):
    q = request.GET.get("q", False)
    context = {"search_query": q} if q else {}
    try:
        kwargs = request.resolver_match.kwargs
        url_name = request.resolver_match.url_name
        # many ways to pass an entity
        entity = getattr(request, 'entity', None)
        # import pdb; pdb.set_trace()
        if entity:
            pass
        elif 'entity_slug' in kwargs:
            entity = Entity.objects.get(slug=kwargs['entity_slug'])
        elif 'entity' in request.GET:
            entity = Entity.objects.get(id=request.GET['entity'])
        elif 'entity_slug' in request.GET:
            entity = Entity.objects.get(slug=request.GET['entity_slug'])

        context['entity'] = entity
        # where the magic happens: set local or global scope urls
        if entity:
            initial = {'entity': entity.id}
            context['questions_url'] = reverse("qna", args=(entity.slug,))
            context['candidates_url'] = reverse("candidate_list", args=(entity.slug,))
        else:
            initial = {}
            context['questions_url'] = reverse("home")
            context['candidates_url'] = reverse("candidate_list")
        context['entity_form'] = EntityChoiceForm(initial=initial, auto_id=False)

    except AttributeError:
        pass

    if request.user.is_authenticated():
        context["profile"] = request.user.profile
    else:
        context["login_form"] = AuthenticationForm()
    context["site"] = get_current_site(request)
    context["ANALYTICS_ID"] = getattr(settings, 'ANALYTICS_ID', False)
    context["FACEBOOK_APP_ID"] = os.environ.get('FACEBOOK_APP_ID', '')

    return context


