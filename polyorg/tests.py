"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from models import Candidate, CandidateList


class CreationTest(TestCase):
    def setUp(self):
        self.linus = User.objects.create(username='Linus')
        self.guido = User.objects.create(username='Guido')
        self.jacob = User.objects.create(username='Jacob')

    def test_candidatelist(self):
        """
        Tests the creation of candidateList and it's basic methods
        """
        cl1 = CandidateList.objects.create(name="Imagine", ballot="I")

        c = Candidate.objects.create(candidate_list=cl1, user=self.jacob, ordinal=1)
        self.assertFalse(cl1.get_candidates())
        c.status = 'V'
        c.save()
        self.assertEquals(cl1.get_candidates().count(), 1)
        c.status = 'X'
        c.save()
        self.assertFalse(cl1.get_candidates())
        cl1.delete()

    def teardown(self):
        for u in self.users: u.delete()

