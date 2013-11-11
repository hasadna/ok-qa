import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from models import Answer, Question

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ("content",)

    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content) > 1000:
            raise ValidationError(_("Answers are limited to 1000 characters"))
        return content

class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ("subject", "content", "entity", "tags", )
        widgets = { 'subject': forms.Textarea(attrs={'cols': 70, 'rows': 2}),
                    'entity': forms.HiddenInput}
    def __init__(self, user, *args, **kwargs):
            super(QuestionForm, self).__init__(*args, **kwargs)
            if user.social_auth.filter(provider='facebook').count():
                self.fields['facebook_publish'] = \
                        forms.BooleanField(label=_("Publish to facebook?"), initial=True, required=False,
                            help_text=_("let your friends know you've asked a question"))

    def clean_subject(self):
        subject = self.cleaned_data['subject']
        if subject == 'post_q':
            raise ValidationError(_("Invalid question"))
        if re.search(r'^[,\'"]+$',subject):
            raise ValidationError(_('Illegal subject: %s') %(subject))    
        return subject

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        for tag in tags:
            if len(tag)>20:
                raise ValidationError(_('Tags are limited to 20 characters'))
            if re.search(r'^[,\'"]+$',tag):
                raise ValidationError(_('Illegal tag: %s') %(tag))
        return tags
