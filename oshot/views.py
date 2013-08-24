# Django imports
from django import forms
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from django.template.context import RequestContext
# pluggable apps
from haystack.query import SearchQuerySet
from haystack.inputs import Exact
from haystack.views import basic_search
from entities.models import Entity
from chosen import forms as chosenforms
# our apps
from qa.models import Question

from oshot.forms import EntityChoiceForm

def place_search(request):
    """ A view to search in a specific place """
    entity_slug = request.GET.get('entity_slug', None)
    if entity_slug:
        searchqs = SearchQuerySet().filter(place=Exact(entity_slug))
        return basic_search(request, searchqueryset=searchqs)
    return basic_search(request)



