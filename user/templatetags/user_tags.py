from django import template

register = template.Library()

@register.filter
def is_editor(self, entity):
    return self.is_editor(entity)

@register.filter
def can_answer(self, entity):
    return self.can_answer(entity)
