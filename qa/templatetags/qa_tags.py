from django import template

register = template.Library()

@register.filter
def can_vote(self, user):
    return self.can_vote(user)

@register.filter
def can_upvote(self, user):
    return self.can_vote(user) == "up"

@register.filter
def can_downvote(self, user):
    return self.can_vote(user) == "down"

@register.filter
def can_delete(self, user):
    return self.can_user_delete(user)
