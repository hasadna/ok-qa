import urllib, hashlib, datetime
# Django imports
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
# Friends' apps
from actstream.models import Follow
# Project's apps
from entities.models import Entity
from user.utils import create_avatar

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
MIN_EDITORS_PER_LOCALITY = 3

class ProfileManager(models.Manager):

    def need_editors(self, entity):
       return Profile.objects.filter(locality=entity).count() < MIN_EDITORS_PER_LOCALITY


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    public_profile = models.BooleanField(default=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    bio = models.TextField(null=True,blank=True)
    description = lambda self: self.bio
    email_notification = models.CharField(max_length=1, choices=NOTIFICATION_PERIOD_CHOICES, blank=True, null=True, default='D')
    avatar_uri = models.URLField(null=True, blank=True)
    last_email_update = models.DateTimeField(default=NEVER_SENT)
    locality = models.ForeignKey(Entity, null=True, verbose_name=_('Locality'))
    sites = models.ManyToManyField(Site)
    is_editor = models.BooleanField(default=False)
    verification = models.CharField(max_length=1, choices=VERIFICATION_STAGES, default='0')
    on_site = CurrentSiteManager()

    objects = ProfileManager()

    def __unicode__(self):
        return self.user.get_full_name()

    def save(self, **kwargs):
        if self.avatar_uri:
            create_avatar(self.user, self.avatar_uri)
        return super(Profile, self).save(**kwargs)

    def avatar_url(self, size=40):
        if self.avatar_uri:
            return self.avatar_uri
        ''' getting the avatar image url from Gravatar '''
        default = "http://oshot.hasadna.org.il/static/img/defaultavatar.png"
        email = self.user.email
        if self.avatar_uri:
            return self.avatar_uri

        if email:
            gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
            gravatar_url += urllib.urlencode({'d':default, 's':str(size)})
            return gravatar_url
        else:
            return default

    @property
    def following(self):
        return map(lambda x: x.actor,
            Follow.objects.filter(user=self.user).prefetch_related('actor')
                  )

    def get_absolute_url(self):
        return reverse('public-profile', args=(self.user.username, ))

    def get_full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def is_candidate(self):
        return self.user.candidate_set.exists()

    @property
    def is_mayor_candidate(self):
        if self.is_candidate:
            return self.user.candidate_set.all()[0].for_mayor
        return False

    @property
    def answer_percentage(self):
        questions = self.locality.questions.filter(is_deleted=False).count()
        answers = self.user.answers.filter(is_deleted=False).count()
        if questions:
            return int((float(answers) / questions) * 100)

    def candidate_list(self):
        if self.is_candidate:
            return self.user.candidate_set.all()[0].candidate_list
        return None
