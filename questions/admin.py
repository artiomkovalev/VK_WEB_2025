from django.contrib import admin
from .models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'rating')
    list_filter = ('created_at',)
    search_fields = ('title', 'text')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('author', 'question', 'rating', 'is_correct')

admin.site.register(QuestionLike)
admin.site.register(AnswerLike)
