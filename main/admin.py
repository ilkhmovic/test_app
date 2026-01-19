from django.contrib import admin
from .models import Test, Question, Category, CheckQuestion, CheckTest, Review, Profile

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1  # Qo'shimcha: yangi savol qo'shish uchun bo'sh joylar soni

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]  # QuestionInline dan foydalanish
    list_display = ['title', 'author', 'category', 'duration']
    search_fields = ['title', 'author__username', 'category__name']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question', 'test', 'true_answer']
    search_fields = ['question', 'test__title']

@admin.register(CheckTest)
class CheckTestAdmin(admin.ModelAdmin):
    list_display = ['student', 'test', 'finded_questions', 'percentage', 'user_passed']

@admin.register(CheckQuestion)
class CheckQuestionAdmin(admin.ModelAdmin):
    list_display = ['checktest', 'question', 'given_answer', 'true_answer', 'is_true']
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'test', 'rating', 'created_at']
    search_fields = ['user__username', 'test__title']
    list_filter = ['rating']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_score']
    search_fields = ['user__username']
