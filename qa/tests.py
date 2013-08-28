import json

from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser, Permission
from django.contrib.sites.models import Site
from social_auth.tests.client import SocialClient
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils import translation
from django.test import TestCase
from django.test.utils import override_settings

from mock import patch
from entities.models import Domain, Division, Entity
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
        division = Division.objects.create(name="localities", domain=domain)
        self.entity = Entity.objects.create(name="the moon", division=division,
                                            id=settings.QNA_DEFAULT_ENTITY_ID)
        self.common_user = User.objects.create_user("commoner", 
                                "commmon@example.com", "pass")
        self.common_user.profile.locality = self.entity
        self.common_user.profile.save()
        self.common2_user = User.objects.create_user("commoner2", 
                                "commmon2@example.com", "pass")
        self.common2_user.profile.locality = self.entity
        self.common2_user.profile.save()
        self.candidate_user = User.objects.create_user("candidate", 
                                "candidate@example.com", "pass")
        self.candidate_user.profile.locality = self.entity
        self.candidate_user.profile.is_candidate = True
        self.candidate_user.profile.save()
        self.editor_user = User.objects.create_user("editor", 
                                "editor@example.com", "pass")
        self.editor_user.profile.locality = self.entity
        self.editor_user.profile.is_editor = True
        self.editor_user.profile.save()
        self.q = Question.objects.create(author = self.common_user,
                        subject="why?", entity=self.entity)
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
        post_url = reverse('post_question', args=(self.entity.slug, ))
        self.assertTrue(c.login(username="commoner", password="pass"))
        response = c.get(post_url)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Question.objects.filter(entity_id=self.entity.id, unislug='Why?').count())
        response = c.post(post_url, {'subject':"Which?",
                        'entity': self.entity.id,
                        })
        self.assertEquals(response.status_code, 302)
        self.assertTrue(Question.objects.get(subject="Which?"))
        response = c.post(post_url, {'subject':"Which?",
                        'entity': self.entity.id,
                        })
        self.assertEquals(response.status_code, 302)
        self.assertTrue(Question.objects.get(subject="Which?"))

    def test_permissions(self):
        self.assertFalse(self.q.can_answer(self.common_user))
        self.assertTrue(self.q.can_answer(self.candidate_user))

    def test_local_home(self):
        c = Client()
        response = c.get(reverse('local_home'))
        res2 = c.get(reverse('local_home',
                        kwargs={'entity_id': settings.QNA_DEFAULT_ENTITY_ID}))
        self.assertEquals(list(response.context['questions']), list(res2.context['questions']))
        self.assertEquals(response.context['candidates'].count(), 1)

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

    def test_flag(self):
        self.q.flagged()
        self.assertEquals(self.q.flags_count, 1)
        c = Client()
        response = c.post(reverse('flag_question', kwargs={'q_id':self.q.id}))
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('redirect', data)
        respone = c.post(data['redirect'],
                {'username':"commoner2", 'password':"pass"})
        response = c.post(reverse('flag_question', kwargs={'q_id':self.q.id}))
        data = json.loads(response.content)
        self.assertIn('message', data)
        self.assertEquals(data['message'], 'Thank you for flagging the question. One of our editors will look at it shortly.')
        self.q = Question.objects.get(pk=self.q.id)
        self.assertEquals(self.q.flags_count, 2)
        response = c.get(reverse('local_home')+"?filter=flagged")
        self.assertEquals(response.context['questions'].count(), 1)

        response = c.post(reverse('flag_question', kwargs={'q_id':self.q.id}))
        data = json.loads(response.content)
        self.assertIn('message', data)
        self.assertEquals(data['message'], 'Thanks.  You already reported this question')
        c.logout()
        self.assertTrue(c.login(username="editor", password="pass"))
        response = c.post(reverse('flag_question', kwargs={'q_id':self.q.id}))
        data = json.loads(response.content)
        self.assertIn('redirect', data)
        self.assertEquals(data['redirect'], reverse('local_home', args=(self.q.entity.slug, )))

    def test_upvote(self):
        c = SocialClient()
        response = c.post(reverse('upvote_question', kwargs={'q_id':self.q.id}))
        self.assertEquals(response.status_code, 302)
        c.login(self.user, backend='facebook')
        response = c.post(reverse('upvote_question', kwargs={'q_id':self.q.id}))
        self.assertEquals(response.status_code, 200)

        u=User.objects.get(email='user@domain.com')
        u.profile.locality = self.common_user.profile.locality
        u.profile.save()
        self.mock_request.return_value.content = json.dumps({
            'id': 1
        })
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
        u.profile.locality = self.entity
        u.profile.save()
        post_url = reverse('post_question', args=(self.entity.slug, ))
        self.mock_request.return_value.content = json.dumps({
            'id': 1
        })
        response = c.post(post_url, {'subject':"Where?",
                        'facebook_publish': 'on',
                        'entity': self.entity.id,
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

    def test_post_question_facebook(self):
        c = SocialClient()
        c.login(self.user, backend='facebook')
        u=User.objects.get(email='user@domain.com')
        u.profile.locality = self.entity
        u.profile.is_candidate = True
        u.profile.save()
        post_url = reverse('post_answer', args=(self.q.id, ))
        self.mock_request.return_value.content = json.dumps({
            'id': 1
        })
        response = c.post(post_url, {'content':"42",
                        })
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
    def test_repr(self):
        self.assertEqual("why?", unicode(self.q))

    def test_repr(self):
        self.assertEqual("why?", unicode(self.q))

    def tearDown(self):
        self.q.delete()
        self.patch.stop()
