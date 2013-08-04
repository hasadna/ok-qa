from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from qa.models import Question
from user.models import Profile

@receiver(post_save, sender=User)
def crate_profile(sender, created, instance, **kwargs):
    if created: # and instance._state.db=='default':
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Question)
def appoint_editors(sender, created, instance, **kwargs):
    ''' turn the first 3 askers in a locality into editors '''
    if created and \
       Profile.objects.need_editors(instance.entity):
        profile = instance.author.profile
        if not profile.is_editor:
            profile.is_editor = True
            profile.save()
            # TODO: notify the user by email he's an editor

