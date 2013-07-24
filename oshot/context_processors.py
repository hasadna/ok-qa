from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import get_current_site
from django.conf import settings

from haystack.forms import SearchForm
from entities.models import Entity

from oshot.forms import EntityChoiceForm

def forms(request):
    context = {"search_form": SearchForm()}
    kwargs = request.resolver_match.kwargs
    if 'entity_slug' in kwargs:
        entity = Entity.objects.get(slug=kwargs['entity_slug'])
        initial = {'entity': entity.id}
    elif 'entity_id' in kwargs:
        entity = Entity.objects.get(id=kwargs['entity_id'])
        initial = {'entity': entity.id}
    else:
        initial = {}
    context['entity_form'] = EntityChoiceForm(initial=initial, auto_id=False)

    if not request.user.is_authenticated():
        context["login_form"] = AuthenticationForm()
    # TODO: remove
    context["site"] = get_current_site(request)
    context["ANALYTICS_ID"] = getattr(settings, 'ANALYTICS_ID', False)
    return context


