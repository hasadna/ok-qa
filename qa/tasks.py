import httplib

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.models import Site

from facepy import GraphAPI
from facepy.exceptions import OAuthError
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

@task(max_retries=3, default_retry_delay=10)
def publish_question_to_facebook(question):
    graph = get_graph_api(question.author)
    if graph:
        question_url = get_full_url(question.get_absolute_url())
        try:
            graph.post(path="me/localshot:ask", question=question_url)
        except OAuthError, exc:
            publish_question_to_facebook.retry(exc=exc)
		

@task(max_retries=3, default_retry_delay=10)
def publish_upvote_to_facebook(upvote):
    graph = get_graph_api(upvote.user)
    if graph:
        question_url = get_full_url(upvote.question.get_absolute_url())
        try:
            graph.post(path="me/localshot:join", question=question_url)
        except OAuthError, exc:
            publish_upvote_to_facebook.retry(exc=exc)

@task(max_retries=3, default_retry_delay=10)
def publish_answer(answer):
    html_content = render_to_string("qa/email_new_answer.html",
            {'answer': answer,
             'ROOT_URL': get_root_url(),
            })
    text_content = 'Sorry, we only support html based email'
    msg = EmailMultiAlternatives(_("A new answer for your question"), text_content,
            settings.DEFAULT_FROM_EMAIL, ( answer.q.author.email, ))
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    graph = get_graph_api(answer.author)
    if graph:
        answer_url = get_full_url(answer.get_absolute_url())
        try:
            graph.post(path="me/localshot:answer", question=answer_url)
        except OAuthError, exc:
            publish_answer.retry(exc=exc)

