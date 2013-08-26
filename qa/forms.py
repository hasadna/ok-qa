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
        fields = ("subject", "content", "entity", "tags", )
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

        return cleaned_data

    def clean_subject(self):
        subject = self.cleaned_data['subject']
        if subject == 'post_q':
            raise ValidationError(_("Invalid question"))
        return subject

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        for tag in tags:
            if len(tag)>20:
                raise ValidationError(_('Tags are limited to 20 characters'))
        return tags
