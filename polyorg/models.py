from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

class CandidateList(models.Model):
    candidates = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, null=True, through='Candidate')
    name = models.CharField(_('List Name'), max_length=80)
    ballot = models.CharField(_('Ballot'), max_length=4)
    number_of_seats = models.IntegerField(blank=True, null=True)
    surplus_partner = models.ForeignKey('self', blank=True, null=True,
                help_text=_('The list with which is the surplus votes partner'))
    mpg_html_report = models.TextField(_('MPG report'), blank=True, null=True,
                help_text=_('The MPG report on the list, can use html'))
    img_url = models.URLField(blank=True)
    youtube_user = models.CharField(_('YouTube user'), max_length = 80, null=True, blank=True)
    wikipedia_page = models.CharField(_('Wikipedia page'), max_length = 80, null=True, blank=True)
    twitter_account = models.CharField(_('Twitter account'), max_length = 80, null=True, blank=True)
    facebook_url = models.URLField(blank=True, null=True)
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

    objects = CandidateManager()

    class Meta:
        ordering = ('ordinal',)

    def __unicode__(self):
        return u'%s - %s - %s' % (self.user.profile.get_full_name(), self.candidate_list.name, self.candidate_list.entity)
