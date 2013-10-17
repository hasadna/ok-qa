from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.template.context import RequestContext
from django.views.decorators.http import require_POST
# Friends' apps
from actstream import follow
from actstream.models import Follow
# Project's apps
from qa.models import Question
from .forms import *
from .models import *

def public_profile(request, username=None, pk=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = get_object_or_404(User, username=pk)
    questions = user.questions.filter(is_deleted=False)
    answers = user.answers.filter(is_deleted=False)
    profile = user.profile
    if profile:
        setattr(request, 'entity', profile.locality)
    if profile.is_candidate:
        candidate_list = profile.candidate_list
    else:
        candidate_list = None

    context = RequestContext(request, {"friend": profile,
                                       "answers": answers,
                                       "questions": questions,
                                       "candidate_list": candidate_list,
                                       })

    # todo: support members as well as candidates
    return render(request, "user/public_profile.html", context)


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()

            local_home = profile.get_absolute_url()
            next = request.POST.get('next', local_home)
            if next == '/':
                next = local_home

            return HttpResponseRedirect(next)
    elif request.method == "GET":
        form = ProfileForm(request.user)

    setattr(request, 'entity', profile.locality)
    
    if request.user.candidatelist_set.exists():
        candidate_list = request.user.candidatelist_set.all()[0]
    else:
        candidate_list = None

    context = RequestContext(request, { "form": form,
                                        "following": profile.following,
                                        "candidate_list": candidate_list})
    return render(request, "user/edit_profile.html", context)


@login_required
@require_POST
def user_follow_unfollow(request):
    """Recieves POST parameters:

    verb - 'follow' or 'unfollow'
    what - string representing target object type ('member', 'agenda', ...)
    id - id of target object

    """
    FOLLOW_TYPES = {
        'question': Question,
        'user': User,
    }
    what = request.POST.get('what', None)
    target_id = request.POST.get('id', None)
    if not target_id:
        return HttpResponseBadRequest('need an id of an object to watch')

    verb = request.POST.get('verb', None)
    if verb not in ['follow', 'unfollow']:
        return HttpResponseBadRequest(
            "verb parameter has to be one of: 'follow', 'unfollow'")

    logged_in = request.user.is_authenticated()
    content_type = ContentType.objects.get_for_model(FOLLOW_TYPES[what])
    qs = Follow.objects.filter(object_id=target_id, content_type=content_type)

    if verb == 'follow':
        try:
            obj = get_object_or_404(FOLLOW_TYPES[what], pk=target_id)
            follow(request.user, obj)
        except:
            return HttpResponseBadRequest('object not found')
    else:  # unfollow
        Follow.objects.get(
            user=request.user,
            content_type=content_type, object_id=target_id).delete()

    res = {
        'can_watch': logged_in,
        'followers': qs.count(),
        'watched': logged_in and bool(qs.filter(user=request.user))
    }
    return HttpResponse(json.dumps(res), content_type='application/json')


@login_required
def editor_list(request):

    if not request.user.is_superuser:
        return HttpResponseForbidden(_('Only superusers have access to this page.'))

    editors = Profile.objects.filter(is_editor=True).order_by('locality__name')
    context = {'editors': editors}
    return render(request, 'user/editor_list.html', context)

