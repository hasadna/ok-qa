from django.forms import ModelForm, HiddenInput
from polyorg.models import CandidateList, Candidate

class CandidateListForm(ModelForm):

    class Meta:
        model = CandidateList
        exclude = ['number_of_seats', 'candidates', 'surplus_partner']
        widgets = {'entity': HiddenInput}

class CandidateForm(ModelForm):

    class Meta:
        model = Candidate
        fields = ['user','candidate_list']
        widgets = {'candidate_list': HiddenInput}
