# Django imports
from django import forms
from django.utils.translation import ugettext as _
# pluggable apps
from chosen import forms as chosenforms
from entities.models import Entity

class EntityChoiceForm(forms.Form):
    """ this form is used only to display the field, input
        is handled by the client
    """
    entity = chosenforms.ChosenModelChoiceField(
            queryset=Entity.objects.exclude(candidatelist__isnull=True).filter(division__index=3),
            label= "",
            empty_label=_("Choose a Place"),
            required=False)
