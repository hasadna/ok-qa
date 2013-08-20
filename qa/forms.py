from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from models import Answer, Question

from slugify import slugify as unislugify


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ("content",)


class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ("subject", "entity", "tags", )
        widgets = { 'subject': forms.Textarea(attrs={'cols': 70, 'rows': 2}),
                    'entity': forms.HiddenInput}
    def __init__(self, user, *args, **kwargs):
            super(QuestionForm, self).__init__(*args, **kwargs)
            if user.social_auth.filter(provider='facebook').count():
                self.fields['facebook_publish'] = \
                        forms.BooleanField(label=_("Publish to facebook?"), initial=True, required=False,
                            help_text=_("let your friends know you've asked a question"))

    def clean(self):
        cleaned_data = super(QuestionForm, self).clean()
        unislug = unislugify(cleaned_data.get('subject'))
        if Question.objects.filter(entity=cleaned_data['entity'], unislug=unislug).count():
            raise ValidationError(_("Question already exists."))

        return cleaned_data

    def clean_subject(self):
        subject = self.cleaned_data['subject']
        if subject == 'post_q':
            raise ValidationError(_("Invalid question"))
        return subject
