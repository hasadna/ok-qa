from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse

from user.models import *

from behave import *

@given("George is a registered user with no activity")
def step_impl(context):
    context.user = User.objects.create_user("user",
                            "user@example.com", "pass")
    context.user.profile.save()

@when("I'm looking at his public profile")
def step_impl(context):
    c = Client()
    public_profile = reverse('public-profile',
            kwargs={'username': context.user.username})
    assert public_profile == \
            Profile.objects.get(user=context.user).get_absolute_url()
    context.response = c.get(public_profile)

@then("I should see his username")
def step_impl(context):
    assert context.response.status_code == 200
    assert context.response.context["friend"].user == context.user
