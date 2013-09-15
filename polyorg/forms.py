from django.forms import ModelForm, HiddenInput
from polyorg.models import CandidateList

class CandidateListForm(ModelForm):

    class Meta:
        model = CandidateList
        fields = ['name', 'ballot', 'entity']
        widgets = {'entity': HiddenInput}
