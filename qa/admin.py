from django.contrib import admin
from .models import *

class QuestionFlagAdmin(admin.StackedInline):
    model = QuestionFlag
    extra = 0

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ QuestionFlagAdmin ]
    list_display = ('subject', 'author', 'entity', 'flags_count')
    list_filter = ('flags_count','entity',)

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('content', 'author', 'entity')
    list_filter = ('question__entity',)


admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
