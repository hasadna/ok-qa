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
        if 'entity_slug' in kwargs:
            entity = Entity.objects.get(slug=kwargs['entity_slug'])
            initial = {'entity': entity.id}
        elif 'entity_id' in kwargs:
            entity = Entity.objects.get(id=kwargs['entity_id'])
            initial = {'entity': entity.id}
        else:
            entity = {}
            initial = {}
        if entity:
            context['questions_url'] = reverse("qna", args=(entity.slug,))
            context['candidates_url'] = reverse("candidate_list", args=(entity.slug,))
        else:
            context['questions_url'] = reverse("home")
            context['candidates_url'] = reverse("candidate_list")

        if url_name not in SPECIAL_ENTITY_FORM:
            context['entity_form'] = EntityChoiceForm(initial=initial, auto_id=False)
    except AttributeError:
        pass

    if not request.user.is_authenticated():
        context["login_form"] = AuthenticationForm()
    # TODO: remove
    context["site"] = get_current_site(request)
    context["ANALYTICS_ID"] = getattr(settings, 'ANALYTICS_ID', False)
    context["FACEBOOK_APP_ID"] = os.environ.get('FACEBOOK_APP_ID', '')
    return context


