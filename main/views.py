from django.shortcuts import render,get_object_or_404,redirect
from .models import Test, Question,CheckQuestion,CheckTest
from django.contrib.auth.decorators import login_required

def index(request):
    tests = Test.objects.all()
    return render(request, 'index.html', {'tests': tests})

@login_required(login_url='login')
def ready_to_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    return render(request, 'ready_to_test.html', {'test': test})

@login_required(login_url='login')
def test(request,test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = Question.objects.filter(test=test)
    if request.method == "POST":
        checktest = CheckTest.objects.create(student = request.user , test = test)
        for question in questions:
            given_answer = request.POST[str(question.id)]
            CheckQuestion.objects.create(checktest = checktest,question = question,given_answer = given_answer,true_answer = question.true_answer)

    context = {"test":test,"questions":questions}

    return render(request,"test.html",context)