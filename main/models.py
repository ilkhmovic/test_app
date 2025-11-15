from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
import datetime

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Test(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    maximum_attempts = models.PositiveBigIntegerField()
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now() + datetime.timedelta(days=10))
    pass_percentage = models.PositiveBigIntegerField()

    def __str__(self):
        return self.title
    
class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question = models.CharField(max_length=300)
    a = models.CharField(max_length=200)
    b = models.CharField(max_length=200)
    c = models.CharField(max_length=200)
    d = models.CharField(max_length=200)
    true_answer = models.CharField(max_length=1, help_text="Enter the correct option (a/b/c/d)")

    def __str__(self):
        return self.question
    
class CheckTest(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    finded_questions = models.PositiveBigIntegerField(default=0)
    user_passed = models.BooleanField(default=False)
    percentage = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return "Test of " + str(self.student.username)
    
    def calculate_results(self):
        """Test natijalarini hisoblash"""
        check_questions = CheckQuestion.objects.filter(checktest=self)
        total_questions = check_questions.count()
        
        if total_questions > 0:
            correct_answers = check_questions.filter(is_true=True).count()
            self.finded_questions = correct_answers
            self.percentage = (correct_answers * 100) // total_questions
            self.user_passed = self.test.pass_percentage <= self.percentage
        else:
            self.finded_questions = 0
            self.percentage = 0
            self.user_passed = False
        
        # Signal cheksiz loopdan qochish uchun
        CheckTest.objects.filter(id=self.id).update(
            finded_questions=self.finded_questions,
            percentage=self.percentage,
            user_passed=self.user_passed
        )
    
class CheckQuestion(models.Model):
    checktest = models.ForeignKey(CheckTest, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    given_answer = models.CharField(max_length=1)
    true_answer = models.CharField(max_length=1)
    is_true = models.BooleanField(default=False)

@receiver(pre_save, sender=CheckQuestion)
def check_answer(sender, instance, *args, **kwargs):
    if instance.given_answer == instance.true_answer:
        instance.is_true = True
    else:
        instance.is_true = False

@receiver(post_save, sender=CheckQuestion)
def update_test_results(sender, instance, created, **kwargs):
    """CheckQuestion saqlandi, CheckTest natijalarini yangilash"""
    if created:
        instance.checktest.calculate_results()