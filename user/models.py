import urllib, hashlib, datetime
# Django imports
from django.db import models
from django.contrib.auth.models import User
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
# Friends' apps
from actstream.models import Follow
# Project's apps
from entities.models import Entity
from user.utils import create_avatar
from polyorg.models import Candidate, CandidateList

NOTIFICATION_PERIOD_CHOICES = (
    (u'N', _('No Email')),
    (u'D', _('Daily')),
    (u'W', _('Weekly')),
)
GENDER_CHOICES = (
    (u'M', _('Male')),
    (u'F', _('Female')),
)
VERIFICATION_STAGES = (
    (u'0', 'No verification needed'),
    (u'S', 'Verification process started'),
    (u'V', 'Verified'),
)


NEVER_SENT = datetime.datetime(1970,8,6)

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    public_profile = models.BooleanField(default=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    bio = models.TextField(null=True,blank=True)
    description = lambda self: self.bio
    email_notification = models.CharField(max_length=1, choices=NOTIFICATION_PERIOD_CHOICES, blank=True, null=True, default='D')
    avatar_uri = models.URLField(null=True, blank=True)
    last_email_update = models.DateTimeField(default=NEVER_SENT)
    verification = models.CharField(max_length=1, choices=VERIFICATION_STAGES, default='0')
    objects = models.Manager()

    def __unicode__(self):
        return self.user.get_full_name()

    @property
    def following(self):
        return map(lambda x: x.actor,
            Follow.objects.filter(user=self.user).prefetch_related('actor')
                  )

    def get_absolute_url(self):
        return reverse('public-profile', args=(self.user.username, ))

    def get_full_name(self):
        return self.user.get_full_name() or self.user.username

    def is_member_of(self, entity):
        return self.user.membership_set.filter(entity=entity).exists()

    def get_entity_ids(self, is_editor=None, can_answer=None):
        memberships = self.user.membership_set
        if is_editor:
            memberships = memberships.filter(is_editor=is_editor)
        if can_answer:
            memberships = memberships.filter(can_answer=can_answer)
        return memberships.values_list('entity', flat=True)

    @property
    def entities(self, is_editor=None, can_answer=None):
        return Entity.filter(id=get_entity_ids(is_editor, can_answer))

    @property
    def editor_in(self):
        return self.entities(is_editor=True)

    @property
    def candidate_in(self):
        return self.entities(can_answer=True)

    # TODO: rename this to can_answer
    def is_candidate(self, entity):
        try:
            return Membership.objects.get(user=self.user, entity=entity).can_answer
        except Membership.DoesNotExist:
            return False

    def is_editor(self, entity):
        try:
            return Membership.objects.get(user=self.user, entity=entity).is_editor
        except Membership.DoesNotExist:
            return False

    @cached_property
    def is_mayor_candidate(self):
        try:
            return Candidate.objects.only('for_mayor').get(user=self.user).for_mayor
        except:
            return False

    @cached_property
    def candidate_list(self):
        try:
            return Candidate.objects.only('candidate_list').get(user=self.user).candidate_list
        except:
            return None

    @cached_property
    def locality(self):
        try:
            return self.user.membership_set.get(entity__division__index=3).entity
        except Membership.DoesNotExist: # does not have a locality set
            return None
        except Membership.MultipleObjectsReturned, e: # does not have a locality set
            raise Membership.MultipleObjectsReturned("%s has multiple localities: %s" \
                    % (self.user, \
                    self.user.membership_set.filter(entity__division__index=3).\
                    values_list('entity__name', flat=True)), \
                    e)

    def add_entity(self, entity, is_editor=False):
        Membership.objects.create(user=self.user, entity=entity, is_editor=is_editor)

    def remove_entity(self, entity):
        self.user.membership_set.get(entity=entity).delete()

    def set_locality(self, entity, is_editor=False):
        if entity.division.index != 3:
            raise ValueError("%s is not a locality" % entity.name)
        try:
            self.user.membership_set.get(entity__division__index=3).delete()
        except Membership.DoesNotExist: # does not have a locality set
            pass
        self.add_entity(entity, is_editor)

class Membership(models.Model):
    user = models.ForeignKey(User)
    entity = models.ForeignKey(Entity)
    is_editor = models.BooleanField(default=False)
    can_answer = models.BooleanField(default=False)
    member_of = models.ForeignKey(CandidateList, null=True, blank=True)
