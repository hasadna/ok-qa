from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from qa.models import Question, QuestionFlag
from user.models import Profile
from oshot.utils import get_root_url

@receiver(post_save, sender=User)
def create_profile(sender, created, instance, **kwargs):
    if created: # and instance._state.db=='default':
        profile = Profile.objects.create(user=instance)
        profile.sites.add(Site.objects.get_current())

@receiver(post_save, sender=Question)
def appoint_editors(sender, created, instance, **kwargs):
    ''' turn the first 3 askers in a locality into editors '''
    if created and Profile.objects.need_editors(instance.entity):
        profile = instance.author.profile
        if not profile.is_editor:
            profile.is_editor = True
            profile.save()
            # TODO: notify the user by email he's an editor

@receiver(post_save, sender=QuestionFlag)
def new_flag(sender, created, instance, **kwargs):
    if created:
        editors = User.objects.filter(profile__locality=instance.question.entity,
                    profile__is_editor=True).values_list('email', flat=True)
        html_content = render_to_string("user/emails/editors_question_flagged.html",
                {'question': instance.question,
                 'reoprter': instance.reporter,
                 'ROOT_URL': get_root_url(),
                 })
        text_content = 'Sorry, we only support html based email'
        msg = EmailMultiAlternatives(_("A question has been flagged"), text_content,
                settings.DEFAULT_FROM_EMAIL, editors)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
