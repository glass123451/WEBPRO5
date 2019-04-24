from django.contrib import admin

# Register your models here.

from django.contrib.auth.models import Permission

from polls.models import Poll, Choice, Question, Comment

admin.site.register(Permission)

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


class PollAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'del_flag']
    list_per_page = 10

    list_filter = ['start_date', 'end_date', 'del_flag']
    search_fields = ['title']

    # fields = ['title', 'del_flag']
    # exclude = ['del_flag']
    fieldsets = [
        (None, {'fields': ['title', 'del_flag']}),
        ('Active Duration', {'fields': ['start_date', 'end_date'], 'classes': ['collapse']})
    ]

    inlines = [QuestionInline]


admin.site.register(Poll, PollAdmin)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'poll', 'text']
    list_per_page = 15

    inlines = [ChoiceInline]


admin.site.register(Question, QuestionAdmin)


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'text', 'value']
    list_per_page = 15


admin.site.register(Choice, ChoiceAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'email', 'tel', 'poll']
    list_per_page = 10

    search_fields = ['title']
    list_filter = ['poll']

admin.site.register(Comment, CommentAdmin)