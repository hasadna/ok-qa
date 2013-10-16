from django.db import models, transaction
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.core.validators import MaxLengthValidator
from django.core.cache import cache
from taggit.models import TaggedItemBase
from django.contrib.contenttypes.models import ContentType

from slugify import slugify as unislugify
from taggit_autosuggest.managers import TaggableManager
from entities.models import Entity
from actstream.models import Follow


MAX_LENGTH_Q_SUBJECT = 140
MAX_LENGTH_Q_CONTENT = 1000
MAX_LENGTH_A_SUBJECT = 80
MAX_LENGTH_A_CONTENT = 1000 

entity_home_key = lambda entity_id: "local_home_%s" % entity_id

class BaseModel(models.Model):
    ''' just a common time base for the models
    '''
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def delete(self, commit=True):
        self.is_deleted = True
        if commit:
            self.save()
        content_type = ContentType.objects.get_for_model(self)
        Follow.objects.filter(content_type=content_type, object_id=self.id).delete()

class TaggedQuestion(TaggedItemBase):
    content_object = models.ForeignKey("Question")
    sites = models.ManyToManyField(Site)
    # objects = models.Manager()
    # objects = CurrentSiteManager()

def can_vote(entity, user):
    ''' returns whether a secific user can upvote/downvote a question in the
        entity '''
    return user.is_authenticated() and user.profile.locality == entity
Entity.add_to_class('can_vote', can_vote)

class Question(BaseModel):

    # TODO: rename to just `slug`
    unislug = models.CharField(
        _('unicode slug'),
        max_length=MAX_LENGTH_Q_SUBJECT,
        null=True,
        blank=True,
        editable=False
    )
    author = models.ForeignKey(User, related_name="questions", verbose_name=_("author"))
    subject = models.CharField(_("question"), max_length=MAX_LENGTH_Q_SUBJECT)
    content = models.TextField(_("details"), validators=[MaxLengthValidator(MAX_LENGTH_Q_CONTENT)],
       help_text=_("Please enter your content in no more than %s letters") % MAX_LENGTH_Q_CONTENT,
       blank = True, default = '')
    rating = models.IntegerField(_("rating"), default=1)
    flags_count = models.IntegerField(_("flags counter"), default=0)
    tags = TaggableManager(through=TaggedQuestion, blank=True)
    sites = models.ManyToManyField(Site)
    # for easy access to current site questions
    objects = models.Manager()
    on_site = CurrentSiteManager()
    entity = models.ForeignKey(Entity, null=True, related_name="questions", verbose_name=_("entity"))

    class Meta:
        unique_together = ('unislug','entity')

    def __unicode__(self):
        return self.subject

    def can_answer(self, user):
        ''' Can a given user answer self? '''
        if user.is_authenticated():
            profile = user.profile
            return profile.is_candidate and profile.locality==self.entity
        else:
            return False

    def get_absolute_url(self):
        return reverse('question_detail', kwargs=dict(
                            entity_id=self.entity.id,
                            slug=self.unislug,
                            )
                      )

    def save(self, **kwargs):
        # make a unicode slug from the subject
        self.unislug = unislugify(self.subject)
        return super(Question, self).save(**kwargs)

    @transaction.commit_on_success
    def flagged(self):
        self.flags_count += 1
        self.save()
        return self.flags_count

    def can_user_delete(self, user):
        ''' returns whether a secific user can delete the question '''
        if self.author == user:
            return True
        if user.is_authenticated() and\
           user.profile.is_editor and\
           user.profile.locality == self.entity:
            return True
        return False

    def can_vote(self, user):
        ''' returns whether a secific user can upvote/downvote the question,
            or neither '''
        if self.entity.can_vote(user):
            if user.upvotes.filter(question=self).exists():
                return 'down'
            else:
                return 'up'
        return None

class Answer(BaseModel):
    author = models.ForeignKey(User, related_name="answers", verbose_name=_("author"))
    content = models.TextField(_("content"), validators=[MaxLengthValidator(MAX_LENGTH_A_CONTENT)],
        help_text=_("Please enter an answer in no more than %s letters") % MAX_LENGTH_A_CONTENT)
    rating = models.IntegerField(_("rating"), default=0)
    question = models.ForeignKey(Question, related_name="answers", verbose_name=_("question"))
    sites = models.ManyToManyField(Site)
    # for easy access to current site answers
    objects = models.Manager()
    on_site = CurrentSiteManager()

    def __unicode__(self):
        return u"%s: %s" % (self.author, self.content[:30])

    def get_absolute_url(self):
        return '%(url)s?answer=%(id)s#answer-%(id)s' % {'url': self.question.get_absolute_url(), 'id': self.id}

    @property
    def entity(self):
        return self.question.entity

class QuestionUpvote(BaseModel):
    question = models.ForeignKey(Question, related_name="upvotes")
    user = models.ForeignKey(User, related_name="upvotes")

class QuestionFlag(BaseModel):
    question = models.ForeignKey(Question, related_name="flags")
    reporter = models.ForeignKey(User, related_name="flags")

''' signals code, to ensure correct site is saved 
'''
@receiver(post_save)
def saved(sender, created, instance, **kwargs):
    if sender in (Question, Answer, TaggedQuestion):
        instance.sites.add(Site.objects.get_current())

@receiver(post_save)
def clear_entity_cache(sender, created, instance, **kwargs):
    ''' clear the local cache on new question or answer '''
    if sender == Question:
        cache.delete(entity_home_key(instance.entity_id))
    elif sender == Answer:
        cache.delete(entity_home_key(instance.question.entity_id))




