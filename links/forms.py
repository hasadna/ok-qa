# encoding: utf-8
# Django imports
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
# Project's apps
from models import *
from polyorg.models import Candidate

class LinkField(forms.URLField):
    def __init__(self, link_type=None, **kwargs):
        super(forms.URLField, self).__init__(**kwargs)
        if link_type:
            self.label = link_type.title

def add_link_fields(form, obj=None, threshold=-1):
    for i in LinkType.objects.filter(importance__gt=threshold):
        form.fields['link_%s' % i.pk] = LinkField(link_type=i, required=False)
    # fill the data for existing links
    if obj:
        for i in Link.objects.for_model(obj):
            form.initial['link_%s' % i.link_type.pk] = i.url

def save_links(form, obj):
    for (name, data) in form.cleaned_data.items():
        field = form.fields[name]
        if isinstance(field, LinkField):
            link_type_pk = int(name[5:])
            try:
                link = Link.objects.get(link_type__pk=link_type_pk,
                        object_pk=obj.pk,
                        content_type=ContentType.objects.get_for_model(obj))
                link.url = data
                link.save()
            except Link.DoesNotExist:
                if data:
                    Link.objects.create_for_model(model=obj, url=data,
                        link_type_id=link_type_pk)
