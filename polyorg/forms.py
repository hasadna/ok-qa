from django.forms import ModelForm, HiddenInput
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


from polyorg.models import CandidateList, Candidate

class CandidateListForm(ModelForm):

    class Meta:
        model = CandidateList
        exclude = ['entity', 'number_of_seats', 'candidates', 'surplus_partner']

    def clean_youtube_url(self):
        url = self.cleaned_data['youtube_url']
        if url and not 'youtube.com' in url:
            raise ValidationError(_('Enter a valid URL.'))
        return url

    def clean_facebook_url(self):
        url = self.cleaned_data['facebook_url']
        if url and not 'facebook.com' in url:
            raise ValidationError(_('Enter a valid URL.'))
        return url

class CandidateForm(ModelForm):

    class Meta:
        model = Candidate
        fields = ['user','candidate_list', 'ordinal', 'for_mayor']
        widgets = {'candidate_list': HiddenInput}
