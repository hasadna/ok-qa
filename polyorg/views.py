from django.utils.translation import ugettext as _
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from polyorg.models import CandidateList, Candidate
from polyorg.forms import CandidateListForm, CandidateForm

@login_required
def candidatelists_list(request):
    if not request.user.profile.is_editor:
        return HttpResponseForbidden(_("Only editors have access to this page."))
    entity = request.user.profile.locality
    candidatelists = CandidateList.objects.filter(entity=entity)
    return render(request, 'polyorg/candidatelist_list.html',{'candidatelists': candidatelists, 'entity': entity})


@login_required
def candidatelist_edit(request, candidatelist_id=None):
    if not request.user.profile.is_editor:
        return HttpResponseForbidden(_("Only editors have access to this page."))
    
    entity = request.user.profile.locality
    
    if candidatelist_id:
        candidatelist = CandidateList.objects.get(id=candidatelist_id)
    else:
        candidatelist = CandidateList(entity=entity)
    
    if request.method == "POST":
        form = CandidateListForm(request.POST, instance=candidatelist)
        if form.is_valid():
            form.save()
            
            return HttpResponseRedirect(reverse('candidate-list-list'))
    else:
        form = CandidateListForm(instance=candidatelist)

    return render(request, "polyorg/candidatelist_form.html", {'form': form, 'entity': entity, 'candidatelist_id': candidatelist_id})


@login_required
def candidates_list(request,candidatelist_id):
    if not request.user.profile.is_editor:
        return HttpResponseForbidden(_("Only editors have access to this page."))
    candidatelist = CandidateList.objects.get(id=candidatelist_id)
    return render(request, 'polyorg/candidate_list.html', \
        {'candidatelist': candidatelist})

@login_required
def candidate_create(request,candidatelist_id):
    if not request.user.profile.is_editor:
        return HttpResponseForbidden(_("Only editors have access to this page."))

    candidatelist = CandidateList.objects.get(id=candidatelist_id)
    if request.method == "POST":
        form = CandidateForm(request.POST)
        if form.is_valid():
            profile = form.cleaned_data['user'].profile
            profile.is_candidate = True
            profile.verification = u'V'
            profile.save()
            form.save()
            return HttpResponseRedirect(reverse('candidate-list', \
                kwargs={'candidatelist_id': candidatelist_id}))
    else:
        form = CandidateForm(initial={'candidate_list': candidatelist})
        form.fields["user"].queryset = \
            User.objects.filter(profile__locality=candidatelist.entity).\
            exclude(profile__is_candidate=True).exclude(profile__is_editor=True)

    return render(request, "polyorg/candidate_form.html", \
        {'form': form, 'candidatelist': candidatelist})

@login_required
def candidate_remove(request, candidatelist_id, candidate_id):
    if not request.user.profile.is_editor:
        return HttpResponseForbidden(_("Only editors have access to this page."))

    candidate_profile = get_object_or_404(User, pk=candidate_id).profile
    if request.user.profile.locality == candidate_profile.locality:
        candidate_profile.is_candidate = False
        candidate_profile.save()
        candidate = Candidate.objects.get(user__id=candidate_id)
        candidate.delete()
        # TODO: notify the candidate by email that he's fired
    else:
        return HttpResponseForbidden(_('Sorry, you are not authorized to remove %s from the candidate list')
                       % candidate_profile.user.get_full_name())

    return HttpResponseRedirect(reverse('candidate-list', \
                kwargs={'candidatelist_id': candidatelist_id}))
