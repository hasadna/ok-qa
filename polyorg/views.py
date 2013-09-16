from django.utils.translation import ugettext as _
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from polyorg.models import CandidateList
from polyorg.forms import CandidateListForm

@login_required
def candiatelists_list(request):
    if not request.user.profile.is_editor:
        return HttpResponseForbidden(_("Only editors have access to this page."))
    entity = request.user.profile.locality
    candidatelists = CandidateList.objects.filter(entity=entity)
    return render(request, 'polyorg/candidatelist_list.html',{'candidatelists': candidatelists, 'entity': entity})

@login_required
def candiatelist_create(request):
    if not request.user.profile.is_editor:
        return HttpResponseForbidden(_("Only editors have access to this page."))
    
    entity = request.user.profile.locality
    if request.method == "POST":
        form = CandidateListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('candidate-list-list'))
    else:
        form = CandidateListForm(initial={'entity': entity})

    return render(request, "polyorg/candidatelist_form.html", {'form': form, 'entity': entity})
