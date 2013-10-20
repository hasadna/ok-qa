from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse

from django.test import TestCase

from entities.models import Domain, Division, Entity
from .models import *

class UserTest(TestCase):
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
        self.entity = Entity.objects.create(name="the moon", division=division)
        self.user = User.objects.create_user("user",
                                "user@example.com", "pass")
        self.user.profile.locality = self.entity
        self.user.profile.save()
        self.candidate = User.objects.create_user("candidate",
                                "candidate@example.com", "pass")
        self.candidate.profile.locality = self.entity
        self.candidate.profile.save()

    def test_edit_profile(self):
        c = Client()
        clist_url = reverse('edit_profile')
        response = c.get(clist_url)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(c.login(username="user", password="pass"))
        response = c.get(clist_url)
        self.assertEquals(response.status_code, 200)

    def test_public_profile(self):
        c = Client()
        # assert {% url %} and get_absolute_url are one and the same
        public_profile = reverse('public-profile',
                kwargs={'username': self.user.username})
        self.assertEquals(public_profile,
                Profile.objects.get(user=self.user).get_absolute_url())
        response = c.get(public_profile)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['entity'], self.entity)
        self.assertTemplateUsed(response, "user/public_profile.html")

