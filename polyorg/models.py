from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
# Project's apps
from qa.models import Answer

class CandidateList(models.Model):
    name = models.CharField(_('List Name'), max_length=80)
    ballot = models.CharField(_('Ballot'), max_length=5)
    candidates = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, null=True, through='Candidate')
    number_of_seats = models.IntegerField(blank=True, null=True)
    surplus_partner = models.ForeignKey('self', blank=True, null=True,
                help_text=_('The list with which is the surplus votes partner'))
    img_url = models.URLField(_('Image URL'), blank=True)
    homepage_url = models.URLField(_('Homepage URL'), blank=True, null=True)
    youtube_url = models.URLField(_('YouTube URL'), blank=True, null=True)
    facebook_url = models.URLField(_('Facebook URL'), blank=True, null=True)
    platform = models.TextField(_('Platform'), blank=True, null=True)
    entity = models.ForeignKey('entities.Entity', blank=True, null=True)

    def save(self, *args, **kwargs):
        super(CandidateList, self).save()
        if self.surplus_partner:
            self.surplus_partner.surplus_partner = self

    @models.permalink
    def get_absolute_url(self):
        return ('candidate-list-detail', [self.id])

    def __unicode__(self):
        return self.name

    def get_candidates(self):
        return Candidate.objects.get_verified().filter(candidate_list=self)

    def can_edit(self, user):
        return user.is_authenticated() and \
            ((user.profile.is_editor and user.profile.locality == self.entity)\
            or user in self.candidates.all()\
            or user.is_superuser)

    def answers(self):
        ''' returns all answers by candidates in the list '''
        return Answer.objects.filter(is_deleted=False,
                author__candidate__user__in=self.candidates.all())


class Party(models.Model):
    name = models.CharField(max_length=64)
    accepts_memberships = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'parties'

    def get_candidates(self):
        return Candidate.objects.get_verified().filter(party=self)

CANDIDATE_STATUS = (
    (u'S', 'Verification process started'),
    (u'V', 'Verified'),
    (u'X', 'Illegal'),
)


class CandidateManager(models.Manager):
    def get_in_process(self):
        return self.filter(status='S')

    def get_verified(self):
        return self.filter(status='V')

    def get_illegal(self):
        return self.filter(status='X')


class Candidate(models.Model):
    candidate_list = models.ForeignKey(CandidateList, verbose_name=_("candidate list"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"))
    ordinal = models.IntegerField(_('Ordinal'), blank=True, null=True)
    party = models.ForeignKey(Party, blank=True, null=True)
    votes = models.IntegerField(_('Elected by #'), blank=True, null=True, help_text=_('How many people voted for this candidate'))
    status = models.CharField(max_length=1, choices=CANDIDATE_STATUS, default='S')
    for_mayor = models.BooleanField(_('Mayorship candidate'), default=False)

    objects = CandidateManager()

    class Meta:
        ordering = ('ordinal',)

    def __unicode__(self):
        return u'%s - %s - %s' % (self.user.profile.get_full_name(), self.candidate_list.name, self.candidate_list.entity)

    @property
    def entity(self):
        return self.candidate_list.entity
