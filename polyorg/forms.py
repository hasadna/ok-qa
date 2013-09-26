from django.forms import ModelForm, HiddenInput
from polyorg.models import CandidateList, Candidate

class CandidateListForm(ModelForm):

    class Meta:
        model = CandidateList
        exclude = ['entity', 'number_of_seats', 'candidates', 'surplus_partner']
        # widgets = {'entity': HiddenInput}

class CandidateForm(ModelForm):

    class Meta:
        model = Candidate
        fields = ['user','candidate_list', 'ordinal', 'for_mayor']
        widgets = {'candidate_list': HiddenInput}
