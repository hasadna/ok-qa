# -*- coding: utf-8 -*-
import urlparse
from datetime import datetime,timedelta
import re

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.utils import translation, timezone
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from flatblocks.models import FlatBlock

from user.models import Profile, NEVER_SENT
from qa.models import Question, QuestionUpvote,Answer
from actstream.models import Follow
from oshot.utils import get_root_url

class Command(BaseCommand):
    args = '[username1 username2 ...]'
    help = 'send email updates to users that want it'

    diffs = dict(D=timedelta(0, 23*3600),
                 W=timedelta(0, (23+6*24)*3600))

    fresh_content_re = re.compile("(new-content)|(updated-content)")
    cache = {}

    def handle (self, *args, **options):
        translation.activate(settings.LANGUAGE_CODE)
        self.start = timezone.now()
        self.q_ct = ContentType.objects.get_for_model(Question)
        self.stdout.write("> sending updates at %s" % self.start)
        if len(args):
            for user in User.objects.filter(email__in=args):
                self.update_user(user)
        else:
            for user in User.objects.all():
                self.update_user(user)

    def update_user(self, user):
        if not user.is_active or not user.email:
            ''' inactive users get nothing! '''
            return

        profile = user.profile
        last_sent = profile.last_email_update
        try:
            freq = self.diffs[user.profile.email_notification]
        except KeyError:
            return

        if self.start-last_sent < freq:
            ''' don't exceed the frequency! '''
            return

        context = {
                'ROOT_URL': get_root_url(),
                'last_sent': last_sent,
                'is_active': user.is_active,
                'user': user,
                }
        if profile.is_candidate:
            ''' handle andidates '''
            local_qs = Question.objects.filter(is_deleted=False, entity=profile.locality).\
                    exclude(answers__author=user)
            context['new_questions'] =  local_qs.filter(created_at__gte=last_sent).order_by('updated_at')
            context['old_questions'] = local_qs.filter(created_at__lt=last_sent).order_by('-rating')
            html_content = render_to_string("email/candidate_update.html", context)
        else:
            ''' handle voters '''
            # TODO: Develop a template for new upvotes
            # context['new_upvotes'] = QuestionUpvote.objects.filter(created_at__gte=last_sent, question__author=user).\
            #        order_by('question')
            context['new_answers'] = Answer.objects.filter(created_at__gte=last_sent,
                    is_deleted=False,
                    question__in = [x.actor for x in \
                            Follow.objects.filter(user=user, content_type=self.q_ct)]).\
                            order_by('question')
            context['new_questions'] = Question.objects.exclude(author=user).\
                    filter(entity=user.profile.locality,
                           is_deleted=False,
                           created_at__gte=last_sent).order_by('author')
            html_content = render_to_string("email/voter_update.html", context)

        subject = FlatBlock.objects.get(slug="candidate_update_email.subject").content
        # TODO: create a link for the update and send it to shaib
        text_content = 'Sorry, we only support html based email'
        # create the email, and attach the HTML version as well.
        try:
            msg = EmailMultiAlternatives(subject, text_content,
                    settings.DEFAULT_FROM_EMAIL, [user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except:
            ''' probably a bad email '''
            return
        self.stdout.write(">>> sent update to %(username)s at %(email)s is_active=%(is_active)s" % user.__dict__)
        if not settings.DEBUG:
            profile.last_email_update = self.start
            profile.save()
