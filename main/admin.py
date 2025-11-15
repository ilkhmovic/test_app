from django.contrib import admin
from .models import Test, Question, Category

class QuestionInline(admin.TabularInline):
    model = Question

class TestAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('title', 'author', 'category', 'maximum_attempts', 'start_date', 'end_date', 'pass_percentage')

admin.site.register([Question, Category])
admin.site.register(Test, TestAdmin)
