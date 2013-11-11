from django.utils.translation import ugettext as _
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.template.context import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from entities.models import Entity
from polyorg.models import CandidateList, Candidate
from polyorg.forms import CandidateListForm, CandidateForm
from qa.models import Answer

@login_required
def candidatelists_list(request, entity_id=None):

    if not entity_id:
        entity = request.user.profile.locality
    else:
        entity = get_object_or_404(Entity, id=entity_id)

    if not ((request.user.profile.is_editor and entity == request.user.profile.locality)\
            or request.user.is_superuser):
        return HttpResponseForbidden(_("Only editors have access to this page."))

    candidatelists = CandidateList.objects.filter(entity=entity)

    context = RequestContext(request, {'candidatelists': candidatelists,
                                       'entity': entity,
                                      })
    return render(request, 'polyorg/candidatelist_list.html', context)


@login_required
def candidatelist_edit(request, candidatelist_id=None, entity_id=None):

    if not entity_id:
        entity = request.user.profile.locality
    else:
        entity = get_object_or_404(Entity, id=entity_id)

    if candidatelist_id:
        candidatelist = get_object_or_404(CandidateList, id=candidatelist_id)
    else:
        candidatelist = CandidateList(entity=entity)


    if not candidatelist.can_edit(request.user):
        return HttpResponseForbidden(_("Only editors have access to this page."))

    if request.method == "POST":
        form = CandidateListForm(request.POST, instance=candidatelist)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('candidate-list', kwargs={'candidatelist_id': candidatelist.id}))
    else:
        form = CandidateListForm(instance=candidatelist)

    context = RequestContext(request, {'form': form,
                                       'entity': entity,
                                       'candidatelist_id': candidatelist_id,
                                      })
    return render(request, "polyorg/candidatelist_form.html", context)


def candidates_list(request,candidatelist_id):
    candidatelist = get_object_or_404(CandidateList, id=candidatelist_id)
    can_edit = candidatelist.can_edit(request.user)
    candidates = candidatelist.candidates.order_by('candidate__ordinal')

    context = RequestContext(request, {'candidatelist': candidatelist,
                                       'can_edit': can_edit,
                                       'candidates' : candidates,
                                      })
    return render(request, 'polyorg/candidate_list.html', context)


@login_required
def candidate_create(request,candidatelist_id):

    candidatelist = get_object_or_404(CandidateList, id=candidatelist_id)

    if not candidatelist.can_edit(request.user):
        return HttpResponseForbidden(_("Only editors have access to this page."))

    if request.method == "POST":
        form = CandidateForm(request.POST)
        if form.is_valid():
            profile = form.cleaned_data['user'].profile
            profile.verification = u'V'
            profile.save()
            form.save()
            return HttpResponseRedirect(reverse('candidate-list', \
                kwargs={'candidatelist_id': candidatelist_id}))
    else:
        form = CandidateForm(initial={'candidate_list': candidatelist})
    form.fields["user"].queryset = \
        User.objects.filter(profile__locality=candidatelist.entity).\
        filter(candidate__isnull=True).exclude(profile__is_editor=True)

    context = RequestContext(request, {'form': form,
                                       'candidatelist': candidatelist,
                                      })
    return render(request, "polyorg/candidate_form.html", context)

@login_required
def candidate_remove(request, candidatelist_id, candidate_id):

    candidatelist = get_object_or_404(CandidateList, id=candidatelist_id)

    if not candidatelist.can_edit(request.user):
        return HttpResponseForbidden(_("Only editors have access to this page."))

    candidate_profile = get_object_or_404(User, pk=candidate_id).profile
    candidate_profile.save()
    candidate = Candidate.objects.filter(user__id=candidate_id)
    for c in candidate:
        if c.candidate_list == candidatelist:
            c.delete()
    # TODO: notify the candidate by email that he's fired

    return HttpResponseRedirect(reverse('candidate-list', \
                kwargs={'candidatelist_id': candidatelist_id}))
