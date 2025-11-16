from django.shortcuts import render, get_object_or_404, redirect
from .models import Test, Question, CheckQuestion, CheckTest, Category
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import TestForm, QuestionForm
from django.forms import formset_factory
from django.http import JsonResponse

def index(request):
    tests = Test.objects.all()
    
    # Statistika
    total_tests_count = Test.objects.count()
    active_users_count = User.objects.filter(is_active=True).count()
    completed_tests_count = CheckTest.objects.count()
    
    context = {
        'tests': tests,
        'total_tests_count': total_tests_count,
        'active_users_count': active_users_count,
        'completed_tests_count': completed_tests_count,
    }
    return render(request, 'index.html', context)

@login_required(login_url='login')
def ready_to_test(request, test_id):
    tests = Test.objects.all()
    test = get_object_or_404(Test, id=test_id)
    total_tests_count = Test.objects.count()
    active_users_count = User.objects.filter(is_active=True).count()
    completed_tests_count = CheckTest.objects.count()
    
    context = {
        'tests': tests,
        'test': test,
        'total_tests_count': total_tests_count,
        'active_users_count': active_users_count,
        'completed_tests_count': completed_tests_count,
    }
    return render(request, 'ready_to_test.html', context)

@login_required(login_url='login')
def test(request, test_id):
    tests = Test.objects.all()
    test = get_object_or_404(Test, id=test_id)
    total_tests_count = Test.objects.count()
    active_users_count = User.objects.filter(is_active=True).count()
    completed_tests_count = CheckTest.objects.count()
    questions = Question.objects.filter(test=test)
    
    if request.method == "POST":
        checktest = CheckTest.objects.create(student=request.user, test=test)
        
        for question in questions:
            answer_key = str(question.id)
            if answer_key in request.POST:
                given_answer = request.POST[answer_key].strip().lower()[:1]
                true_answer = question.true_answer.strip().lower()[:1]
                
                CheckQuestion.objects.create(
                    checktest=checktest,
                    question=question,
                    given_answer=given_answer,
                    true_answer=true_answer
                )
        
        checktest.calculate_results()
        return redirect('test_result', checktest_id=checktest.id)
    
    context = {
        "test": test, 
        "questions": questions,
        'tests': tests,
        'total_tests_count': total_tests_count,
        'active_users_count': active_users_count,
        'completed_tests_count': completed_tests_count,}
    return render(request, "test.html", context)

@login_required(login_url='login')
def test_result(request, checktest_id):
    checktest = get_object_or_404(CheckTest, id=checktest_id, student=request.user)
    check_questions = CheckQuestion.objects.filter(checktest=checktest)
    total_tests_count = Test.objects.count()
    active_users_count = User.objects.filter(is_active=True).count()
    completed_tests_count = CheckTest.objects.count()
    context = {
        'checktest': checktest,
        'check_questions': check_questions,
        'total_tests_count': total_tests_count,
        'active_users_count': active_users_count,
        'completed_tests_count': completed_tests_count,
    }
    return render(request, 'test_result.html', context)

@login_required(login_url='login')
def profile(request, username):
    user = get_object_or_404(User, username=username)
    user_tests = Test.objects.filter(author=user)
    user_checktests = CheckTest.objects.filter(student=user)
    
    total_tests_created = user_tests.count()
    total_tests_taken = user_checktests.count()
    passed_tests = user_checktests.filter(user_passed=True).count()

    total_tests_count = Test.objects.count()
    active_users_count = User.objects.filter(is_active=True).count()
    completed_tests_count = CheckTest.objects.count()
    
    context = {
        'profile_user': user,
        'user_tests': user_tests,
        'user_checktests': user_checktests.order_by('-id')[:10],
        'total_tests_created': total_tests_created,
        'total_tests_taken': total_tests_taken,
        'passed_tests': passed_tests,
        'success_rate': (passed_tests * 100 // total_tests_taken) if total_tests_taken > 0 else 0,
        'total_tests_count': total_tests_count,
        'active_users_count': active_users_count,
        'completed_tests_count': completed_tests_count,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='login')
def create_test(request):
    # Boshlang'ich 1 ta savol bilan boshlaymiz
    QuestionFormSet = formset_factory(QuestionForm, extra=1)

    total_tests_count = Test.objects.count()
    active_users_count = User.objects.filter(is_active=True).count()
    completed_tests_count = CheckTest.objects.count()
    
    if request.method == 'POST':
        test_form = TestForm(request.POST)
        question_formset = QuestionFormSet(request.POST, prefix='questions')
        
        if test_form.is_valid():
            # Formsetni alohida tekshiramiz
            valid_questions = 0
            for form in question_formset:
                if form.is_valid() and form.cleaned_data.get('question'):
                    valid_questions += 1
            
            if valid_questions > 0:
                test = test_form.save(commit=False)
                test.author = request.user
                test.save()
                
                # Faqat to'ldirilgan savollarni saqlaymiz
                for form in question_formset:
                    if form.is_valid() and form.cleaned_data.get('question'):
                        question = form.save(commit=False)
                        question.test = test
                        question.save()
                
                return redirect('my_tests')
            else:
                test_form.add_error(None, "Kamida bitta savol qo'shishingiz kerak")
        else:
            # Form xatolari bo'lsa
            print("Form xatolari:", test_form.errors)
    else:
        test_form = TestForm()
        question_formset = QuestionFormSet(prefix='questions')
    
    context = {
        'test_form': test_form,
        'question_formset': question_formset,
        'total_tests_count': total_tests_count,
        'active_users_count': active_users_count,
        'completed_tests_count': completed_tests_count,
    }
    return render(request, 'create_test.html', context)

@login_required(login_url='login')
def add_question_field(request):
    """Yangi savol maydonini qaytaradi"""
    form = QuestionForm()
    
    index = request.GET.get('index', 0)
    
    html = f"""
    <div class="question-form card mb-3" id="question-{index}">
        <div class="card-header bg-light d-flex justify-content-between align-items-center">
            <h6 class="mb-0">Savol {int(index) + 1}</h6>
            <button type="button" class="btn btn-danger btn-sm remove-question" data-index="{index}">
                <i class="fas fa-times"></i> O'chirish
            </button>
        </div>
        <div class="card-body">
            <div class="mb-3">
                <label class="form-label">Savol Matni</label>
                <textarea name="questions-{index}-question" class="form-control" rows="2" placeholder="Savol matnini kiriting" id="id_questions-{index}-question"></textarea>
            </div>
            
            <div class="row">
                <div class="col-md-6 mb-2">
                    <label class="form-label">A Variant</label>
                    <input type="text" name="questions-{index}-a" class="form-control" placeholder="A variant" id="id_questions-{index}-a">
                </div>
                <div class="col-md-6 mb-2">
                    <label class="form-label">B Variant</label>
                    <input type="text" name="questions-{index}-b" class="form-control" placeholder="B variant" id="id_questions-{index}-b">
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6 mb-2">
                    <label class="form-label">C Variant</label>
                    <input type="text" name="questions-{index}-c" class="form-control" placeholder="C variant" id="id_questions-{index}-c">
                </div>
                <div class="col-md-6 mb-2">
                    <label class="form-label">D Variant</label>
                    <input type="text" name="questions-{index}-d" class="form-control" placeholder="D variant" id="id_questions-{index}-d">
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <label class="form-label">To'g'ri Javob</label>
                    <select name="questions-{index}-true_answer" class="form-control" id="id_questions-{index}-true_answer">
                        <option value="">To'g'ri javobni tanlang</option>
                        <option value="a">A variant</option>
                        <option value="b">B variant</option>
                        <option value="c">C variant</option>
                        <option value="d">D variant</option>
                    </select>
                </div>
            </div>
        </div>
    </div>
    """
    
    return JsonResponse({'html': html})

@login_required(login_url='login')
def test_detail(request, test_id):
    test = get_object_or_404(Test, id=test_id, author=request.user)
    questions = Question.objects.filter(test=test)
    total_tests_count = Test.objects.count()
    active_users_count = User.objects.filter(is_active=True).count()
    completed_tests_count = CheckTest.objects.count()
    
    context = {
        'test': test,
        'questions': questions,
        'total_tests_count': total_tests_count,
        'active_users_count': active_users_count,
        'completed_tests_count': completed_tests_count,
    }
    return render(request, 'test_detail.html', context)

@login_required(login_url='login')
def my_tests(request):
    user_tests = Test.objects.filter(author=request.user).order_by('-id')
    total_tests_count = Test.objects.count()
    active_users_count = User.objects.filter(is_active=True).count()
    completed_tests_count = CheckTest.objects.count()
    
    context = {
        'user_tests': user_tests,
        'total_tests_count': total_tests_count,
        'active_users_count': active_users_count,
        'completed_tests_count': completed_tests_count,
    }
    return render(request, 'my_tests.html', context)