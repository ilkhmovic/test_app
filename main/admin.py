from django.contrib import admin
from .models import Test, Question, Category, CheckQuestion, CheckTest

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1  # Qo'shimcha: yangi savol qo'shish uchun bo'sh joylar soni

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]  # QuestionInline dan foydalanish
    list_display = ['title', 'author', 'category', 'start_date', 'end_date']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question', 'test', 'true_answer']

@admin.register(CheckTest)
class CheckTestAdmin(admin.ModelAdmin):
    list_display = ['student', 'test', 'finded_questions', 'percentage', 'user_passed']

@admin.register(CheckQuestion)
class CheckQuestionAdmin(admin.ModelAdmin):
    list_display = ['checktest', 'question', 'given_answer', 'true_answer', 'is_true']