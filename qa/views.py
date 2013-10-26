import os
import json

from django.db.models import Count
from django.http import HttpResponse, HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import Http404
from django.views.decorators.http import require_POST
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.contrib import messages
from django.conf import settings
from django.views.generic.detail import SingleObjectTemplateResponseMixin, BaseDetailView
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.core.cache import cache

from entities.models import Entity
from taggit.models import Tag
from actstream import follow, unfollow

from user.models import Profile
from qa.forms import AnswerForm, QuestionForm
from qa.models import *
from qa.tasks import publish_question_to_facebook, publish_upvote_to_facebook,\
    publish_answer
from qa.mixins import JSONResponseMixin

from polyorg.models import CandidateList

# the order options for the list views
ORDER_OPTIONS = {'date': '-created_at', 'rating': '-rating', 'flagcount': '-flags_count'}
# CBS locality stats
CBS_STATS = json.load(open(os.path.join(settings.STATICFILES_ROOT, 'js/entity_stats.js')))

class JsonpResponse(HttpResponse):
    def __init__(self, data, callback, *args, **kwargs):
        jsonp = "%s(%s)" % (callback, json.dumps(data))
        super(JsonpResponse, self).__init__(
            content=jsonp,
            content_type='application/javascript',
            *args, **kwargs)


def local_home(request, entity_slug=None, entity_id=None, tags=None,
        template="qa/question_list.html"):
    """
    A home page for an entity including questions and candidates
    """
    if request.user.is_anonymous() and not tags and not request.GET:
        ret = cache.get(entity_home_key(entity_id))
        if ret:
            return ret
    context = RequestContext(request)
    entity = context.get('entity', None)
    if not entity or entity.division.index != 3:
        raise Http404(_("Bad Entity"))

    if request.user.is_authenticated() and not request.user.profile.locality:
        messages.error(request,_('Please update your locality in your user profile to use the site'))
        return HttpResponseRedirect(reverse('edit_profile'))

    questions = Question.on_site.select_related('author', 'entity').prefetch_related('answers__author').filter(entity=entity, is_deleted=False)

    only_flagged = request.GET.get('filter', False) == 'flagged'
    if only_flagged:
        questions = questions.filter(flags_count__gte = 1)
        order_opt = False
        order = 'flags_count'
    else:
        order_opt = request.GET.get('order', 'rating')
        try:
            order = ORDER_OPTIONS[order_opt]
        except KeyError:
            order = ORDER_OPTIONS['rating']
    questions = questions.order_by(order)

    if tags:
        current_tags = Tag.objects.filter(slug__in=tags.split(','))
        questions = questions.filter(tags__in=current_tags)
    else:
        current_tags = None

    if entity:
        tags = Tag.objects.filter(qa_taggedquestion_items__content_object__entity=entity,\
            qa_taggedquestion_items__content_object__is_deleted=False).\
                annotate(num_times=Count('qa_taggedquestion_items')).\
                order_by("-num_times","slug")
        need_editors = Profile.objects.need_editors(entity)
        users_count = entity.profile_set.count()
    else:
        users_count = Profile.objects.count()

    candidate_lists = CandidateList.objects.select_related().filter(entity=entity)
    candidates = User.objects.filter(candidate__isnull=False).filter(profile__locality=entity)

    list_id = request.GET.get('list', default='mayor')
    if list_id == 'mayor':
        candidate_list = None
        candidates = candidates.filter(candidate__for_mayor=True)
    else:
        try:
            candidate_list = candidate_lists.get(pk=list_id)
        except (CandidateList.DoesNotExist, ValueError):
            messages.error(request, _('No such candidate list: ' + list_id))
            return HttpResponseRedirect(request.path)
        candidates = candidates.filter(candidate__candidate_list=candidate_list)

    candidates = candidates.annotate(num_answers=models.Count('answers')).\
                            order_by('-num_answers')

    candidate_lists = candidate_lists.annotate( \
                            num_answers=models.Count('candidates__answers')).\
                            order_by('-num_answers')

    answers_count = Answer.objects.filter(question__entity=entity, question__is_deleted=False).count()
    
    stats = CBS_STATS.get(entity.code, {"totalpopulation": 0, "numofcouncilman": "", "socioeco": "", "voting":""})

    context.update({ 'tags': tags,
        'questions': questions,
        'by_date': order_opt == 'date',
        'by_rating': order_opt == 'rating',
        'only_flagged': only_flagged,
        'current_tags': current_tags,
        'need_editors': need_editors,
        'candidates': candidates,
        'candidate_list': candidate_list,
        'candidate_lists': candidate_lists,
        'users_count': users_count,
        'answers_count': answers_count,
        'stats': stats,
        })

    ret = render(request, template, context)
    if request.user.is_anonymous() and not tags and not request.GET:
        cache.set('local_home_%s' % entity_id, ret, timeout = 36000)
    return ret

class QuestionDetail(JSONResponseMixin, SingleObjectTemplateResponseMixin, BaseDetailView):
    model = Question
    template_name = 'qa/question_detail.html'
    context_object_name = 'question'
    slug_field = 'unislug'

    def get_queryset(self, queryset=None):
        if 'entity_id' in self.kwargs:
            return Question.objects.filter(entity__id=self.kwargs['entity_id'])
        elif 'entity_slug' in self.kwargs:
            return Question.objects.filter(entity__slug=self.kwargs['entity_slug'])

    def get_context_data(self, **kwargs):
        user = self.request.user
        question = self.object
        context = super(QuestionDetail, self).get_context_data(**kwargs)
        context['max_length_a_content'] = MAX_LENGTH_A_CONTENT
        context['answers'] = question.answers.filter(is_deleted=False)
        context['entity'] = question.entity
        can_answer = question.can_answer(user)
        context['can_answer'] = can_answer
        if can_answer:
            try:
                user_answer = question.answers.get(author=user)
                context['my_answer_form'] = AnswerForm(instance=user_answer)
                context['my_answer_id'] = user_answer.id
            except question.answers.model.DoesNotExist:
                context['my_answer_form'] = AnswerForm()
        context['can_flag'] = True
        if 'answer' in self.request.GET:
            try:
                answer = Answer.objects.get(pk=self.request.GET['answer'])
                context['fb_message'] = answer.content
            except:
                pass

        supporters = [vote.user for vote in question.upvotes.all()]
        supporters = [question.author] + supporters
        if user in supporters and user != question.author:
            supporters = [user] + [u for u in supporters if u != user]
        context['supporters'] = supporters

        return context

    def render_to_response(self, context):
        # Look for a 'format=json' GET argument
        if self.request.GET.get('format', 'html') == 'json' or self.request.is_ajax():
            data = {
                'question': {
                    'subject': self.object.subject,
                    'content': self.object.content,
                    'author': self.object.author.username
                }
            }

            return JSONResponseMixin.render_to_response(self, data)
        else:
            return SingleObjectTemplateResponseMixin.render_to_response(self, context)


@login_required
def post_answer(request, q_id):
    question = Question.objects.get(id=q_id)

    if not question.can_answer(request.user):
        return HttpResponseForbidden(_("You must be logged in as a candidate to post answers"))

    try:
        # If the user already answered, update his answer
        answer = question.answers.get(author=request.user)
        is_new_answer = False
    except question.answers.model.DoesNotExist:
        answer = Answer(author=request.user, question=question)
        is_new_answer = True
        follow(request.user, question)

    answer.content = request.POST.get("content")

    answer.save()
    publish_answer.delay(answer, send_email=is_new_answer)

    return HttpResponseRedirect(question.get_absolute_url())

def post_question(request, entity_id=None, slug=None):
    if request.user.is_anonymous():
        messages.error(request, _('Sorry but only connected users can post questions'))
        return HttpResponseRedirect(settings.LOGIN_URL)

    profile = request.user.profile

    if entity_id:
        entity = Entity.objects.get(pk=entity_id)
        if entity != profile.locality:
            messages.warning(request, _('Sorry, you may only post questions in your locality') +
                "\n" +
                _('Before posting a new question, please check if it already exists in this page'))
            return HttpResponseRedirect(reverse('local_home',
                                        kwargs={'entity_id': profile.locality.id,}))

    entity = profile.locality

    q = slug and get_object_or_404(Question, unislug=slug, entity=entity)

    if request.method == "POST":
        form = QuestionForm(request.user, request.POST, instance=q)
        if form.is_valid():
            ''' carefull when changing a question's history '''
            if not q:
                try:
                    q = Question.objects.get(author=request.user, subject=form.cleaned_data['subject'])
                except:
                    pass
            question = form.save(commit=False)
            if q:
                if q.author != request.user:
                    return HttpResponseForibdden(_("You can only edit your own questions."))
                if q.answers.count():
                    return HttpResponseForbidden(_("Question has been answered, editing disabled."))
                question.id = q.id
                question.created_at = q.created_at

            question.author = request.user
            question.save()
            form.save_m2m()
            if form.cleaned_data.get('facebook_publish', False):
                publish_question_to_facebook.delay(question)
            follow(request.user, question)
            return HttpResponseRedirect(question.get_absolute_url())
    else:
        if q:
            form = QuestionForm(request.user, instance=q)
        else:
            form = QuestionForm(request.user, initial={'entity': entity})

    becoming_editor = not profile.is_editor and\
                      Profile.objects.need_editors(entity)
    context = RequestContext(request, {"form": form,
                                       "entity": entity,
                                       "max_length_q_subject": MAX_LENGTH_Q_SUBJECT,
                                       "slug": slug,
                                       "becoming_editor": becoming_editor,
                                      })
    return render(request, "qa/post_question.html", context)


def upvote_question(request, q_id):
    if request.user.is_anonymous():
        messages.error(request, _('Sorry but only connected users can upvote questions'))
        return HttpResponseRedirect(settings.LOGIN_URL)

    if request.method == "POST":
        q = get_object_or_404(Question, id=q_id)
        user = request.user
        if q.entity != user.profile.locality:
            return HttpResponseForbidden(_('You may only support questions in your locality'))
        if q.author == user:
            return HttpResponseForbidden(_("You may not support your own question"))
        if user.upvotes.filter(question=q):
            return HttpResponseForbidden(_("You already upvoted this question"))
        else:
            upvote = QuestionUpvote.objects.create(question=q, user=user)
            #TODO: use signals so the next line won't be necesary
            new_count = change_rating(q, 1)
            follow(request.user, q)

            publish_upvote_to_facebook.delay(upvote)
            return HttpResponse(new_count)
    else:
        return HttpResponseForbidden(_("Use POST to upvote a question"))

@login_required
def downvote_question(request, q_id):
    if request.method == "POST":
        q = get_object_or_404(Question, id=q_id)
        user = request.user
        if q.author == user:
            return HttpResponseForbidden(_("Cannot downvote your own question"))
        elif not user.upvotes.filter(question=q):
            return HttpResponseForbidden(_("You already downvoted this question"))
        else:
            QuestionUpvote.objects.filter(question=q, user=user).delete()
            new_count = change_rating(q, -1)
            unfollow(request.user, q)

            # TODO: publish_downvote_to_facebook.delay(upvote)
            return HttpResponse(new_count)
    else:
        return HttpResponseForbidden(_("Use POST to upvote a question"))


@transaction.commit_on_success
def change_rating(q, change):
    q = Question.objects.get(id=q.id)
    q.rating += change
    q.save()
    return q.rating


class RssQuestionFeed(Feed):
    """Simple feed to get all questions"""
    title = _('OK QA Question Feed')
    link = "/"
    description = _('Questions from OKQA')

    def items(self):
        return Question.objects.order_by('-updated_at')

    def item_title(self, item):
        return item.subject

    def item_description(self, item):
        return item.content


class AtomQuestionFeed(Feed):
    feed_type = Atom1Feed

    def get_object(self, request, entity_id):
        return get_object_or_404(Entity, pk=entity_id)

    def title(self, obj):
        return _("Questions feed for %s") % unicode(obj)

    def subtitle(self, obj):
        # TODO: add a `Site` key to `Entity` so we can use obj
        return _('Brought to you by "%s"') % (Site.objects.get_current().name, )

    def link(self, obj):
        return reverse('local_home', args=(obj.id, ))

    def item_title(self, item):
        return item.subject

    def item_subtitle(self, item):
        return item.content
    item_description = item_subtitle

    def items(self, obj):
        return Question.objects.filter(is_deleted=False, entity=obj).order_by('-created_at')[:30]

class RssQuestionAnswerFeed(Feed):
    """"Give question, get all answers for that question"""

    def get_object(self, request, q_id):
        return get_object_or_404(Question, pk=q_id)

    def title(self, obj):
        return _('Answers for the question') + ' "%s' % obj.subject + '"'

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return _('A feed of all answers for the question') + ' "%s' % obj.subject + '"'

    def items(self, obj):
        return Answer.objects.filter(question=obj).order_by('-updated_at')


class AtomQuestionAnswerFeed(RssQuestionAnswerFeed):
    feed_type = Atom1Feed
    subtitle = RssQuestionAnswerFeed.description


''' an interface that returns a `message` and a `redirect` url. '''
@require_POST
def flag_question(request, q_id):
    q = get_object_or_404(Question, id=q_id)
    user = request.user
    tbd = False # to-be-deleted
    ''' permissionssss '''
    if user.is_anonymous():
        ''' first kick anonymous users '''
        messages.error(request, _('Sorry, you have to login to flag questions'))
        redirect = '%s?next=%s' % (settings.LOGIN_URL, q.get_absolute_url())
        return HttpResponse(redirect, content_type="text/plain")

    elif user == q.author:
        ''' handle authors '''
        if q.answers.filter(is_deleted=False):
            messages.error(request, _('Sorry, can not delete a question with answers'))
        else:
            tbd = True
    elif user.profile.is_editor:
        ''' handle editors '''
        if user.profile.locality == q.entity:
            tbd = True

    if tbd:
        ''' seems like we have to delete the question '''
        q.delete()
        messages.success(request, _('Question has been removed'))
    else:
        if user.flags.filter(question=q):
            messages.error(request, _('Thanks.  You already reported this question'))
        else:
            ''' raising the flag '''
            flag = QuestionFlag.objects.create(question=q, reporter=user)
            #TODO: use signals so the next line won't be necesary
            q.flagged()
            messages.success(request,
                _('Thank you for flagging the question. One of our editors will look at it shortly.'))

    redirect = reverse('local_home', args=(q.entity.slug,))
    return HttpResponse(redirect, content_type="text/plain")
