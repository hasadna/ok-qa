from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from entities.models import Entity
from chosen import forms as chosenforms
from links.forms import add_link_fields, save_links

from models import *

class ProfileForm(forms.Form):
    first_name = forms.CharField(label=_('first name'), max_length = 15)
    last_name = forms.CharField(label=_('last name'), required=False, max_length = 20)
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^(?u)[ \w.@+-]{4,}$',
        help_text = _("Required. 4-30 characters (only letters, numbers spaces and @/./+/-/_ characters)."),
        error_message = _("Required. 4-30 characters (only letters, numbers spaces and @/./+/-/_ characters)."))
    email = forms.EmailField(required=False ,label=_(u'email address'),
                             help_text = _("We don't spam, and don't show your email to anyone")
                             )
    gender = forms.ChoiceField(choices = GENDER_CHOICES,
                               label = _('Gender'))
    locality = chosenforms.ChosenModelChoiceField(
                queryset=Entity.objects.filter(division__index=3),
                label=_('Locality'), required=False)
    bio = forms.CharField(required=False,
                                  label=_('Tell us and other users bit about yourself'),
                                  widget=forms.Textarea(attrs={'rows':4}))
    email_notification = forms.ChoiceField(choices = NOTIFICATION_PERIOD_CHOICES,
                                           label = _('E-Mail Notifications'),
                                           help_text = _('Should we send you e-mail notification about updates to things you follow on the site?'))

    def __init__(self, user, *args, **kw):
        super(ProfileForm, self).__init__(*args, **kw)
        self.user = user
        if self.user:
            self.profile = user.profile
            self.initial = {'username': self.user.username,
                            'email': self.user.email,
                            'first_name': self.user.first_name,
                            'last_name': self.user.last_name,
                            'bio': self.profile.bio,
                            'email_notification': self.profile.email_notification,
                            'gender': self.profile.gender,
                           }
            if self.profile.locality:
                self.fields['locality'].widget.attrs['disabled'] = True
                self.initial['locality'] = self.profile.locality
            add_link_fields(self, user)

    def clean_username(self):
        data = self.cleaned_data['username']
        if data == self.user.username:
            return data
        try:
            User.objects.get(username = data)
            raise forms.ValidationError(_("This username is already taken."))
        except User.DoesNotExist:
            return data

    def clean_locality(self):
         
        locality = self.cleaned_data['locality']
        if not locality and self.profile:
            locality = self.profile.locality
        if locality:
            return locality
        else:

            raise forms.ValidationError(_('Please set your locality'))

    def save(self, commit = True):
        user = self.user
        if self.cleaned_data['email']:
            if user.email != self.cleaned_data['email']: #email changed - user loses comment permissions, until he validates email again.
                #TODO: send validation email
                pass
            user.email = self.cleaned_data['email']
        user.is_active = True
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        self.profile.bio = self.cleaned_data['bio']
        self.profile.email_notification = self.cleaned_data['email_notification']
        self.profile.gender = self.cleaned_data['gender']
        if self.cleaned_data['locality']:
            self.profile.locality = self.cleaned_data['locality']

        if commit:
            user.save()
            self.profile.save()
            save_links(self, user)
        return user

