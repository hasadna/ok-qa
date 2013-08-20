import httplib

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site

from facepy import GraphAPI
from celery import task
from celery.utils.log import get_task_logger
from social_auth.models import UserSocialAuth

logger = get_task_logger(__name__)

def get_graph_api(user):
    try:
        access_token = UserSocialAuth.objects.get(user=user).extra_data['access_token']
        return GraphAPI(access_token)
    except ObjectDoesNotExist:
        return None

def get_full_url(path):
    return 'http://%s%s' % (Site.objects.get_current().domain,path)

@task()
def publish_question_to_facebook(question):
    graph = get_graph_api(question.author)
    if graph:
        question_url = get_full_url(question.get_absolute_url())
        graph.post(path="me/localshot:ask", question=question_url)

@task()
def publish_upvote_to_facebook(upvote):
    graph = get_graph_api(upvote.user)
    if graph:
        question_url = get_full_url(upvote.question.get_absolute_url())
        graph.post(path="me/localshot:join", question=question_url)

@task()
def publish_answer_to_facebook(answer):
    graph = get_graph_api(answer.author)
    if graph:
        answer_url = get_full_url(answer.get_absolute_url())
        graph.post(path="me/localshot:answer", question=answer_url)

