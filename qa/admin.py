from django.contrib import admin
from .models import Question, Answer, QuestionUpvote, QuestionFlag

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    pass


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    pass


@admin.register(QuestionUpvote)
class QuestionUpvoteAdmin(admin.ModelAdmin):
    pass


@admin.register(QuestionFlag)
class QuestionFlagAdmin(admin.ModelAdmin):
    pass
