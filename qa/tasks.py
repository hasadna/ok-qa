from celery import task
import httplib

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site

from celery.utils.log import get_task_logger
from social_auth.models import UserSocialAuth

logger = get_task_logger(__name__)

@task()
def publish_question_to_facebook(obj):
    obj_url = 'http://%s/%s' % (Site.objects.get_current().domain, obj.get_absolute_url())
    access_token = UserSocialAuth.objects.get(user=obj.author).extra_data['access_token']

    conn = httplib.HTTPConnection("https://graph.facebook.com/me/localshot:ask?\
        access_token=%s&method=POST&question=%s" % (access_token, obj_url))
    logger.info("Asking a '%s' on facebook for %s" % (obj.title, obj.author.username))
    return conn.request("POST")

@task()
def publish_upvote_to_facebook(upvote):
    try:
        access_token = UserSocialAuth.objects.get(provider='facebook', user=upvote.user).extra_data['access_token']
        obj_url = 'http://%s/%s' % (Site.objects.get_current().domain, upvote.question.get_absolute_url())
        conn = httplib.HTTPConnection("https://graph.facebook.com/me/localshot:join?\
            access_token=%s&method=POST&question=%s" % (access_token, obj_url))
        logger.info("published to faceboo that '%s' joined '%s'" % \
                (upvote.user.username, upvote.question.subject))
        return conn.request("POST")
    except ObjectDoesNotExist:
        return False

