import json

from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sites.models import Site
from social_auth.tests.client import SocialClient
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils import translation
from django.test import TestCase
from django.test.utils import override_settings

from mock import patch
from entities.models import Domain, Division, Entity
from polyorg.models import Candidate, CandidateList
from .models import *


# @override_settings(TEST_RUNNER='djcelery.contrib.test_runner.CeleryTestSuiteRunner')
@override_settings(CELERY_ALWAYS_EAGER = True)
class QuestionTest(TestCase):
    client = SocialClient
    user = {
        'first_name': 'Django',
        'last_name': 'Reinhardt',
        'verified': True,
        'name': 'Django Reinhardt',
        'locale': 'en_US',
        'hometown': {
            'id': '12345678',
            'name': 'Any Town, Any State'
        },
        'expires': '4812',
        'updated_time': '2012-01-29T19:27:32+0000',
        'access_token': 'dummyToken',
        'link': 'http://www.facebook.com/profile.php?id=1234',
        'location': {
            'id': '108659242498155',
            'name': 'Chicago, Illinois'
        },
        'gender': 'male',
        'timezone': -6,
        'id': '1234',
        'email': 'user@domain.com'
    }
    def setUp(self):
        domain = Domain.objects.create(name="test")
        division = Division.objects.create(name="localities", domain=domain, index="3")
        self.home = Entity.objects.create(name="earth", division=division,
                                            id=1111, code="1111")
        self.away = Entity.objects.create(name="the moon", division=division,
                                            id=9999, code="41")
        self.candidate_list = CandidateList.objects.create(name="list", ballot="l", 
                                                            entity=self.home)

        self.common_user = User.objects.create_user("commoner",
                                "commmon@example.com", "pass")
        self.common_user.profile.locality = self.home
        self.common_user.profile.save()
        self.common2_user = User.objects.create_user("commoner2", 
                                "commmon2@example.com", "pass")
        self.common2_user.profile.locality = self.home
        self.common2_user.profile.save()
        self.candidate_user = User.objects.create_user("candidate", 
                                "candidate@example.com", "pass")
        self.candidate_user.profile.locality = self.home
        self.candidate_user.profile.save()
        Candidate.objects.create(user=self.candidate_user, candidate_list=self.candidate_list)
        self.editor = User.objects.create_user("editor", 
                                "editor@example.com", "pass")
        self.editor.profile.locality = self.home
        self.editor.profile.is_editor = True
        self.editor.profile.save()
        self.q = Question.objects.create(author = self.common_user,
                        subject="why?", entity=self.home)
        self.a = self.q.answers.create(author = self.candidate_user,
                        content="because the world is round")
        self.site1 = Site.objects.create(domain='abc.com')
        self.site2 = Site.objects.create(domain='fun.com')
        self.q.tags.create(name="abc")
        self.q.tags.create(name="def")
        translation.deactivate_all()
        self.patch = patch('requests.session')
        self.mock_request = self.patch.start()().request

    def test_sites(self):
        I = Site.objects.get_current()
        self.assertEqual(Question.on_site.count(), 1)
        self.assertEqual(Answer.on_site.count(), 1)
        #TODO: self.assertEqual(TaggedQuestion.on_site.count(), 1)

    def test_post_question(self):
        c = Client()
        post_url = reverse('post_question')
        self.assertTrue(c.login(username="commoner", password="pass"))
        response = c.get(post_url)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Question.objects.filter(entity_id=self.home.id, unislug='Why?').count())
        response = c.post(post_url, {'subject':"Which?",
                        'entity': self.home.id,
                        })
        new_q = Question.objects.get(subject="Which?")
        self.assertRedirects(response, new_q.get_absolute_url())
        away_q = Question.objects.create(subject="Which?", entity=self.away, author=self.common_user)
        response = c.get(away_q.get_absolute_url())
        self.assertEquals(response.status_code, 200)

    def test_permissions(self):
        self.assertFalse(self.q.can_answer(self.common_user))
        self.assertTrue(self.q.can_answer(self.candidate_user))

    def test_local_home(self):
        c = Client()
        # According to issue #263, entity urls should only use id's.
        default_home = reverse('local_home',
                        kwargs={'entity_id': self.home.id})
        response = c.get(default_home)

        self.assertEquals(response.context['candidates'].count(), 0)
        self.assertEquals(response.context['users_count'], 4)
        self.assertEquals(response.context['questions'].count(), 1)
        self.assertEquals(response.context['answers_count'], 1)

        self.q.is_deleted = True
        self.q.save()
        response = c.get(default_home)
        self.assertFalse(response.context['questions'])
        self.assertEquals(response.context['answers_count'], 0)
        self.q.is_deleted = False
        self.q.save()

    def test_question_detail(self):
        c = Client()
        q_url = reverse('question_detail',
                         kwargs={'entity_slug': self.q.entity.slug, 'slug':self.q.unislug})

        response = c.get(q_url)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(response.context['can_answer'])
        self.assertTemplateUsed(response, "qa/question_detail.html")
        self.assertTrue(c.login(username="candidate", password="pass"))
        response = c.get(q_url)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context['can_answer'])

    def test_flags(self):
        ''' try to flag a question as an anonymous and get an error.
            login as a commoner.
            try to flag a question and get a thank you note.
            try flagging it again and get an error message. logout.
            login in as an editor from a diffrent locality and try to delete
            the question. get an error, so move the editor to the right locality
            and finally soft delete the damn question.
        '''
        self.q.flagged()
        self.assertEquals(self.q.flags_count, 1)
        c = Client()

        response = c.post(reverse('flag_question', kwargs={'q_id':self.q.id}))
        self.assertEquals(response.status_code, 200)
        login_url = response.content
        response = c.get(login_url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('messages', response.context)
        message = list(response.context['messages'])[0]
        self.assertEquals(message.message, 'Sorry, you have to login to flag questions')
        self.assertEquals(self.q.flags_count, 1)
        respone = c.post(login_url,
                {'username':"commoner2", 'password':"pass"})
        self.assertEquals(response.status_code, 200)
        response = c.post(reverse('flag_question', kwargs={'q_id':self.q.id}))
        self.assertEquals(response.status_code, 200)
        response = c.get(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertIn('messages', response.context)
        message = list(response.context['messages'])[0]
        self.assertEquals(message.message, 'Thank you for flagging the question. One of our editors will look at it shortly.')
        self.q = Question.objects.get(pk=self.q.id)
        self.assertEquals(self.q.flags_count, 2)
        response = c.get("%s?%s" % (reverse('local_home',
                                           kwargs={'entity_slug': self.home.slug}
                                    ),
                                   "filter=flagged"))
        self.assertEquals(response.context['questions'].count(), 1)

        response = c.post(reverse('flag_question', kwargs={'q_id':self.q.id}))
        self.assertEquals(response.status_code, 200)
        response = c.get(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertIn('messages', response.context)
        message = list(response.context['messages'])[0]
        self.assertEquals(message.message, 'Thanks.  You already reported this question')

    def test_editors(self):
        c = Client()
        self.editor.profile.locality = self.away
        self.editor.profile.save()
        self.assertTrue(c.login(username="editor", password="pass"))
        response = c.post(reverse('flag_question', kwargs={'q_id':self.q.id}))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, reverse('local_home', args=(self.q.entity.slug, )))
        response = c.get(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertIn('messages', response.context)
        message = list(response.context['messages'])[0]
        self.assertEquals(message.message, 'Thank you for flagging the question. One of our editors will look at it shortly.')
        self.editor.profile.locality = self.home
        self.editor.profile.save()

        response = c.post(reverse('flag_question', kwargs={'q_id':self.q.id}))
        self.assertEquals(response.status_code, 200)
        response = c.get(response.content)
        self.assertEquals(response.status_code, 200)
        message = list(response.context['messages'])[0]
        self.assertEquals(message.message, 'Question has been removed')

    def test_post_not_killing_upvote(self):
        '''
        Related to issue #365:

        When a user add a description to a question it looses all followers.
        '''

        # Create a new question
        c = Client()
        self.assertTrue(c.login(username="commoner", password="pass"))
        post_url = reverse('post_question')
        response = c.get(post_url)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Question.objects.filter(entity_id=self.home.id, unislug='Why?').count())
        response = c.post(post_url, {
                        'subject':"What?",
                        'entity': self.home.id,
                        'content': 'Yes!',
                        'tags': '',
                        })
        new_q = Question.objects.get(subject="What?")
        self.assertRedirects(response, new_q.get_absolute_url())

        # Upvote the question
        c = SocialClient()
        response = c.post(reverse('upvote_question', kwargs={'q_id':self.q.id}))
        self.assertEquals(response.status_code, 302)
        c.login(self.user, backend='facebook')
        u=User.objects.get(email='user@domain.com')
        u.profile.locality = self.common_user.profile.locality
        u.profile.save()
        self.mock_request.return_value.content = json.dumps({
            'id': 1
        })
        response = c.post(reverse('upvote_question', kwargs={'q_id':new_q.id}))
        self.assertEquals(response.status_code, 200)

        # Edit the question
        c = Client()
        post_url = reverse('edit_question', kwargs={'slug': new_q.unislug})
        self.assertTrue(c.login(username="commoner", password="pass"))
        response = c.get(post_url)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Question.objects.filter(entity_id=self.home.id, unislug='Why?').count())
        response = c.post(post_url, {
                        'id': new_q.id,
                        'content': 'Because we like it!',
                        'tags': '',
                        'subject':new_q.subject,
                        'entity': self.home.id,
                        })
        self.assertRedirects(response, new_q.get_absolute_url())

        # Check question's rating.
        # Before the bug fix, it used to be 1.
        updated_q = Question.objects.get(subject="What?")
        self.assertEquals(updated_q.rating, 2)


    def test_upvote(self):
        c = SocialClient()
        response = c.post(reverse('upvote_question', kwargs={'q_id':self.q.id}))
        self.assertEquals(response.status_code, 302)
        c.login(self.user, backend='facebook')
        u=User.objects.get(email='user@domain.com')
        u.profile.locality = self.common_user.profile.locality
        u.profile.save()
        self.mock_request.return_value.content = json.dumps({
            'id': 1
        })
        response = c.post(reverse('upvote_question', kwargs={'q_id':self.q.id}))
        self.assertEquals(response.status_code, 200)

        response = c.post(reverse('upvote_question', kwargs={'q_id':self.q.id}))
        self.assertEquals(response.status_code, 403)
        self.assertEquals(response.content, 'You already upvoted this question')
        self.mock_request.assert_called_with(
            'POST',
            'https://graph.facebook.com/me/localshot:join',
            files={},
            data={
                'question': 'http://example.com%s' % self.q.get_absolute_url(),
                'access_token': 'dummyToken'
            }
        )

        response = c.post(reverse('upvote_question', kwargs={'q_id':self.q.id}))
        self.assertEquals(response.status_code, 403)
        self.assertEquals(response.content, 'You already upvoted this question')

    def test_post_question_facebook(self):
        c = SocialClient()
        c.login(self.user, backend='facebook')
        u=User.objects.get(email='user@domain.com')
        u.profile.locality = self.home
        u.profile.save()
        post_url = reverse('post_question')
        self.mock_request.return_value.content = json.dumps({
            'id': 1
        })
        response = c.post(post_url, {'subject':"Where?",
                        'facebook_publish': 'on',
                        'home': self.home.id,
                        'entity': self.home.id,
                        })
        self.assertEquals(response.status_code, 302)
        new_q=Question.objects.get(subject="Where?")

        self.mock_request.assert_called_with(
            'POST',
            'https://graph.facebook.com/me/localshot:ask',
            files={},
            data={
                'question': 'http://example.com%s' % new_q.get_absolute_url(),
                'access_token': 'dummyToken'
            }
        )

    def test_post_answer_facebook(self):
        c = SocialClient()
        c.login(self.user, backend='facebook')
        u=User.objects.get(email='user@domain.com')
        u.profile.locality = self.home
        Candidate.objects.create(user=u,candidate_list=self.candidate_list)
        u.profile.save()
        post_url = reverse('post_answer', args=(self.q.id, ))
        self.mock_request.return_value.content = json.dumps({
            'id': 1
        })
        response = c.post(post_url, {'content':"42", })
        self.assertEquals(response.status_code, 302)
        new_a=Answer.objects.get(content="42")

        self.mock_request.assert_called_with(
            'POST',
            'https://graph.facebook.com/me/localshot:answer',
            files={},
            data={
                'question': 'http://example.com%s' % new_a.get_absolute_url(),
                'access_token': 'dummyToken'
            }
        )

    def test_can_delete(self):
        self.assertFalse(self.q.can_user_delete(AnonymousUser()))
        self.assertFalse(self.q.can_user_delete(self.common2_user))
        self.assertTrue(self.q.can_user_delete(self.q.author))
        self.assertTrue(self.q.can_user_delete(self.editor))

    def test_feeds(self):
        c = Client()
        response = c.get(reverse('atom_entity_questions', args=(self.home.id, )))
        self.assertEquals(response.status_code, 200)
        # TODO: test the result

    def test_repr(self):
        self.assertEqual("why?", unicode(self.q))

    def tearDown(self):
        self.q.delete()
        self.patch.stop()
