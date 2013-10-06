from django import template

register = template.Library()

@register.filter
def can_vote(question, user):
    return question.can_vote(user)

@register.filter
def can_upvote(question, user):
    return question.can_vote(user) == "up"

@register.filter
def can_downvote(question, user):
    return question.can_vote(user) == "down"

@register.filter
def can_delete(question, user):
    return question.can_user_delete(user)
