import urllib, hashlib, datetime
# Django imports
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
# Friends' apps
from taggit.managers import TaggableManager
from registration.models import RegistrationProfile
from actstream import follow
from actstream.models import Follow
# Project's apps
from entities.models import Entity

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
def invite_user(site, username, email, first_name="", last_name=""):
    ''' invite a new user to the system '''
    user, created = User.objects.get_or_create(username=username,
            defaults = {'email': email,
                        'first_name': first_name,
                        'last_name': last_name,
                       })
    if created:
        user.is_active = False
        user.save()
    elif user.is_active:
        return user
    else:
        user.registrationprofile_set.all().delete()


    registration_profile = RegistrationProfile.objects.create_profile(user)

    return user

class ProfileManager(models.Manager):
    def get_candidates(self, entity=None):
        ''' get all the candidates in an entity '''
        qs =  User.objects.filter(profile__is_candidate=True)
        if entity:
            qs = qs.filter(profile__locality = entity)
        return qs

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
    url = models.URLField(null=True, blank=True)
    last_email_update = models.DateTimeField(default=NEVER_SENT)
    locality = models.ForeignKey(Entity, null=True, verbose_name=_('Locality'))
    sites = models.ManyToManyField(Site)
    is_candidate = models.BooleanField(default=False)
    is_editor = models.BooleanField(default=False)
    verification = models.CharField(max_length=1, choices=VERIFICATION_STAGES, default='0')
    on_site = CurrentSiteManager()

    objects = ProfileManager()
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

    # @property
    # def is_candidate(self):
    #     if self.user.candidate_set.exists():
    #         return True
    #     return False

    @property
    def is_mayor_candidate(self):
        if self.is_candidate:
            return self.user.candidate_set.only()[0].for_mayor
        return False


