from django import forms
from .models import Test, Question, Category

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['title', 'category', 'maximum_attempts', 'duration', 'pass_percentage']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Test nomi'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'maximum_attempts': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Daqiqalarda (masalan 20)'}),
            'pass_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question', 'a', 'b', 'c', 'd', 'true_answer']
        widgets = {
            'question': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Savol matnini kiriting'
            }),
            'a': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A variant'}),
            'b': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'B variant'}),
            'c': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'C variant'}),
            'd': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'D variant'}),
            'true_answer': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'To\'g\'ri javobni tanlang'),
                ('a', 'A variant'),
                ('b', 'B variant'),
                ('c', 'C variant'),
                ('d', 'D variant'),
            ]),
        }