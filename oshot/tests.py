from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

class OshotTest(TestCase):
    def test_home_page(self):
        c = Client()
        res2 = c.get(reverse('home_page'))
        self.assertTemplateUsed(res2, 'home_page.html')


