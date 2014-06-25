from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse

from user.models import *

from behave import *

freds_question = None

@when("I'm looking at friend's public profile")
def step_impl(context):
    c = Client()
    public_profile = reverse('public-profile',
            kwargs={'username': context.user.username})
    assert public_profile == \
            Profile.objects.get(user=context.user).get_absolute_url()
    context.response = c.get(public_profile)

@then("I should see friend's username")
def step_impl(context):
    assert context.response.status_code == 200
    assert context.response.context["friend"].user == context.user

@given("George is a registered user with no activity")
def step_impl(context):
    context.user = User.objects.create_user("user",
                            "user@example.com", "pass")
    context.user.profile.save()

@given(u'Fred asked a question')
def impl(c):
    c.fred = User.objects.create_user("fred",
                            "fred@example.com", "pass")
    # TODO: this should be automated using Django
    c.fred.profile.save()
    freds_question = c.fred.profile.ask("WHY???", tags="general,why")

#When I'm looking at friend's public profile
@then(u'I should see his question')
def impl(c):
    r = c.response
    assert r.status_code == 200
    assert r.context["questions"] == [ freds_question ]

