from django.forms import ModelForm, HiddenInput
from polyorg.models import CandidateList, Candidate

class CandidateListForm(ModelForm):

    class Meta:
        model = CandidateList
        fields = ['name', 'ballot', 'entity']
        widgets = {'entity': HiddenInput}

class CandidateForm(ModelForm):

    class Meta:
        model = Candidate
        fields = ['user','candidate_list']
        widgets = {'candidate_list': HiddenInput}
