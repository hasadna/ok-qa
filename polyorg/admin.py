from django.contrib import admin
from django.contrib.contenttypes import generic

from models import Candidate, CandidateList, Party
from links.models import Link


class MembershipInline(admin.TabularInline):
    model = CandidateList.candidates.through
    extra = 1

class LinksInline(generic.GenericTabularInline):
    model = Link
    ct_fk_field = 'object_pk'
    extra = 1

class CandidateListAdmin(admin.ModelAdmin):
    list_display = ['name', 'ballot', 'entity']
    list_filter = ['ballot', 'entity']

admin.site.register(CandidateList, CandidateListAdmin)

class CandidateAdmin(admin.ModelAdmin):
    inlines = [LinksInline,]
    list_display = ['user', 'candidate_list', 'entity', 'for_mayor']
    list_filter = ['for_mayor', 'candidate_list__entity']


admin.site.register(Candidate, CandidateAdmin)


class PartyAdmin(admin.ModelAdmin):
    pass

admin.site.register(Party, PartyAdmin)
