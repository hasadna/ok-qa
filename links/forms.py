# encoding: utf-8
# Django imports
from django import forms
from django.utils.translation import ugettext_lazy as _
# Project's apps
from models import *
from polyorg.models import Candidate

class LinkField(forms.URLField):
    def __init__(self, required, label, title):
        super(forms.URLField, self).__init__(required=required, label=label)
        self.link_type = LinkType.objects.get(title=title)
        self.link = None

class LinksForm(forms.Form):

    homepage_url = LinkField(required=False, label=_('Homepage URL'), title=u'default')
    youtube_url = LinkField(required=False, label=_('YouTube URL'), title=u'YouTube')
    facebook_url = LinkField(required=False, label=_('Facebook URL'), title=u'פייסבוק')
    twitter_url = LinkField(required=False, label=_('Twitter URL'), title=u'טוויטר')
    wikipedia_url = LinkField(required=False, label=_('Wikipedia URL'), title=u'ויקיפדיה')
    rss_url = LinkField(required=False, label=_('RSS Feed'), title=u'רסס')

    def __init__(self, user, *args, **kw):
        super(LinksForm, self).__init__(*args, **kw)
        self.user = user
        if self.user:
            try:
                self.candidate = user.candidate_set.get()
            except Candidate.DoesNotExist:
                self.candidate = None
            if self.candidate:
                for field in self.fields.values():
                    if isinstance(field, LinkField):
                        links = self.candidate.get_links(link_type=field.link_type)
                        if links:
                            link = links[0] # Only use first link
                            field.initial = link.url
                            field.link = link
            else: # Not a candidate; remove link fields from form
                self.fields = dict((field, data) for (field, data) in \
                        self.fields.items() if not isinstance(data, LinkField))

    def save(self, commit = True):
        if self.candidate:
            for (name, data) in self.cleaned_data.items():
                field = self.fields[name]
                if isinstance(field, LinkField):
                    if field.link:
                        field.link.url = data
                        if commit:
                            field.link.save()
                    elif data:
                        field.link = self.candidate.add_link(
                                url=data,
                                title=field.label, \
                                link_type=field.link_type)

            if commit:
                self.candidate.save()
        return self.user
