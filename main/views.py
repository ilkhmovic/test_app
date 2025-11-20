from django.shortcuts import render, get_object_or_404, redirect
from .models import Test, Question, CheckQuestion, CheckTest, Category
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import TestForm, QuestionForm
from django.forms import formset_factory
from django.http import JsonResponse
from django.contrib import messages
import pandas as pd
import re
import csv
import os
import datetime
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from test_app import settings

def index(request):
    tests_list = Test.objects.all().order_by('-id')  # -id bo'lishi kerak
    
    # Paginator
    page = request.GET.get('page', 1)
    paginator = Paginator(tests_list, getattr(settings, 'TESTS_PER_PAGE', 6))
    
    try:
        tests = paginator.page(page)
    except PageNotAnInteger:
        tests = paginator.page(1)
    except EmptyPage:
        tests = paginator.page(paginator.num_pages)
    
    # Statistika
    total_tests_count = Test.objects.count()
    active_users_count = User.objects.filter(is_active=True).count()
    completed_tests_count = CheckTest.objects.count()
    
    context = {
        'tests': tests,  # Bu endi Page object
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
    categories = Category.objects.all()
    
    if request.method == 'POST':
        method = request.POST.get('method', 'basic')
        
        try:
            # Test ma'lumotlarini olish
            title = request.POST.get('title')
            category_id = request.POST.get('category')
            maximum_attempts = request.POST.get('maximum_attempts')
            pass_percentage = request.POST.get('pass_percentage')
            days_duration = request.POST.get('days_duration', 10)
            
            # Sanalarni hisoblash
            start_date = timezone.now()
            end_date = start_date + datetime.timedelta(days=int(days_duration))
            
            # Testni yaratish
            test = Test.objects.create(
                title=title,
                category_id=category_id,
                maximum_attempts=maximum_attempts,
                pass_percentage=pass_percentage,
                start_date=start_date,
                end_date=end_date,
                author=request.user
            )
            
            saved_questions = 0
            
            if method == 'manual':
                # Qo'lda kiritilgan savollarni saqlash
                manual_questions = request.POST.getlist('manual_questions[]')
                manual_a = request.POST.getlist('manual_a[]')
                manual_b = request.POST.getlist('manual_b[]')
                manual_c = request.POST.getlist('manual_c[]')
                manual_d = request.POST.getlist('manual_d[]')
                manual_true_answers = request.POST.getlist('manual_true_answer[]')
                
                for i in range(len(manual_questions)):
                    if manual_questions[i].strip():
                        Question.objects.create(
                            test=test,
                            question=manual_questions[i],
                            a=manual_a[i],
                            b=manual_b[i],
                            c=manual_c[i],
                            d=manual_d[i],
                            true_answer=manual_true_answers[i]
                        )
                        saved_questions += 1
            
            elif method == 'import':
                # Fayldan import qilish
                if request.FILES.get('import_file'):
                    uploaded_file = request.FILES['import_file']
                    import_count = process_import_file(uploaded_file, test)
                    saved_questions += import_count
            
            elif method == 'text':
                # Matndan import qilish
                questions_text = request.POST.get('questions_text', '').strip()
                if questions_text:
                    text_count = process_questions_text(questions_text, test)
                    saved_questions += text_count
            
            if saved_questions > 0:
                messages.success(request, f"✅ Test va {saved_questions} ta savol muvaffaqiyatli yaratildi!")
                return redirect('test_detail', test_id=test.id)
            else:
                test.delete()
                messages.error(request, "❌ Hech qanday savol qo'shilmadi!")
                return redirect('create_test')
                
        except Exception as e:
            messages.error(request, f"❌ Xatolik yuz berdi: {str(e)}")
            return redirect('create_test')
    
    return render(request, 'create_test.html', {
        'categories': categories
    })

def process_import_file(uploaded_file, test):
    """Fayldan savollarni import qilish"""
    try:
        fs = FileSystemStorage()
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        filename = fs.save(f"temp_import_{test.id}{file_extension}", uploaded_file)
        file_path = fs.path(filename)
        
        saved_count = 0
        
        if file_extension == '.csv':
            # CSV faylni o'qish
            with open(file_path, 'r', encoding='utf-8') as file:
                # Avtomatik delimiter aniqlash
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row in reader:
                    try:
                        if all(field in row for field in ['question', 'a', 'b', 'c', 'd', 'true_answer']):
                            question_text = row['question'].strip()
                            a_text = row['a'].strip()
                            b_text = row['b'].strip()
                            c_text = row['c'].strip()
                            d_text = row['d'].strip()
                            true_ans = row['true_answer'].strip().lower()
                            
                            if (question_text and a_text and b_text and c_text and d_text and 
                                true_ans in ['a', 'b', 'c', 'd']):
                                
                                Question.objects.create(
                                    test=test,
                                    question=question_text,
                                    a=a_text,
                                    b=b_text,
                                    c=c_text,
                                    d=d_text,
                                    true_answer=true_ans
                                )
                                saved_count += 1
                                
                    except Exception as e:
                        print(f"CSV qator xatosi: {e}")
                        continue
        
        elif file_extension in ['.xlsx', '.xls']:
            # Excel faylni o'qish
            df = pd.read_excel(file_path)
            
            if all(col in df.columns for col in ['question', 'a', 'b', 'c', 'd', 'true_answer']):
                for index, row in df.iterrows():
                    try:
                        question_text = str(row['question']).strip()
                        a_text = str(row['a']).strip()
                        b_text = str(row['b']).strip()
                        c_text = str(row['c']).strip()
                        d_text = str(row['d']).strip()
                        true_ans = str(row['true_answer']).strip().lower()
                        
                        if (question_text and a_text and b_text and c_text and d_text and 
                            true_ans in ['a', 'b', 'c', 'd'] and question_text != 'nan'):
                            
                            Question.objects.create(
                                test=test,
                                question=question_text,
                                a=a_text,
                                b=b_text,
                                c=c_text,
                                d=d_text,
                                true_answer=true_ans
                            )
                            saved_count += 1
                            
                    except Exception as e:
                        print(f"Excel qator xatosi: {e}")
                        continue
        
        # Vaqtincha faylni o'chirish
        if fs.exists(filename):
            fs.delete(filename)
            
        return saved_count
        
    except Exception as e:
        print(f"Fayl import xatosi: {e}")
        return 0

def process_questions_text(questions_text, test):
    """Matndan savollarni import qilish"""
    try:
        # Savollarni pars qilish
        pattern = r'(\d+)[\.\)]\s*(.*?)\s*A[\)\.]\s*(.*?)\s*B[\)\.]\s*(.*?)\s*C[\)\.]\s*(.*?)\s*D[\)\.]\s*(.*?)\s*Javob:\s*([A-D])'
        matches = re.findall(pattern, questions_text, re.DOTALL | re.IGNORECASE)
        
        saved_count = 0
        for match in matches:
            try:
                question_num, question_text, a, b, c, d, true_answer = match
                
                # Matnlarni tozalash
                question_text = question_text.strip()
                a = a.strip()
                b = b.strip()
                c = c.strip()
                d = d.strip()
                true_answer = true_answer.lower().strip()
                
                if (question_text and a and b and c and d and true_answer in ['a', 'b', 'c', 'd']):
                    Question.objects.create(
                        test=test,
                        question=question_text,
                        a=a,
                        b=b,
                        c=c,
                        d=d,
                        true_answer=true_answer
                    )
                    saved_count += 1
                    
            except Exception as e:
                print(f"Matn pars xatosi: {e}")
                continue
        
        return saved_count
        
    except Exception as e:
        print(f"Matn import xatosi: {e}")
        return 0


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

@login_required(login_url='login')
def import_questions(request, test_id):
    test = get_object_or_404(Test, id=test_id, author=request.user)
    
    if request.method == 'POST' and request.FILES.get('questions_file'):
        uploaded_file = request.FILES['questions_file']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(filename)
        
        try:
            # CSV faylni o'qish
            if filename.endswith('.csv'):
                df = pd.read_csv(file_path)
            # Excel faylni o'qish
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                messages.error(request, "Faqat CSV yoki Excel fayllarni yuklash mumkin")
                return redirect('test_detail', test_id=test_id)
            
            # Savollarni saqlash
            saved_count = 0
            for index, row in df.iterrows():
                if all(k in row for k in ['question', 'a', 'b', 'c', 'd', 'true_answer']):
                    Question.objects.create(
                        test=test,
                        question=row['question'],
                        a=row['a'],
                        b=row['b'],
                        c=row['c'],
                        d=row['d'],
                        true_answer=row['true_answer']
                    )
                    saved_count += 1
            
            messages.success(request, f"{saved_count} ta savol muvaffaqiyatli qo'shildi")
            
        except Exception as e:
            messages.error(request, f"Faylni o'qishda xatolik: {str(e)}")
        finally:
            # Vaqtincha faylni o'chirish
            if fs.exists(filename):
                fs.delete(filename)
        
        return redirect('test_detail', test_id=test_id)
    
    return render(request, 'import_questions.html', {'test': test})

@login_required(login_url='login')
def parse_questions(request, test_id):
    test = get_object_or_404(Test, id=test_id, author=request.user)
    
    if request.method == 'POST':
        questions_text = request.POST.get('questions_text', '')
        
        if not questions_text:
            messages.error(request, "Savollar matni kiritilmagan")
            return redirect('mass_create_questions', test_id=test_id)
        
        # Savollarni pars qilish
        pattern = r'(\d+)\.\s*(.*?)\s*A\)\s*(.*?)\s*B\)\s*(.*?)\s*C\)\s*(.*?)\s*D\)\s*(.*?)\s*Javob:\s*([A-D])'
        matches = re.findall(pattern, questions_text, re.DOTALL | re.IGNORECASE)
        
        saved_count = 0
        for match in matches:
            try:
                question_num, question_text, a, b, c, d, true_answer = match
                
                Question.objects.create(
                    test=test,
                    question=question_text.strip(),
                    a=a.strip(),
                    b=b.strip(),
                    c=c.strip(),
                    d=d.strip(),
                    true_answer=true_answer.lower().strip()
                )
                saved_count += 1
                
            except Exception as e:
                continue
        
        if saved_count > 0:
            messages.success(request, f"{saved_count} ta savol muvaffaqiyatli qo'shildi")
        else:
            messages.error(request, "Hech qanday savol topilmadi yoki format noto'g'ri")
        
        return redirect('test_detail', test_id=test_id)
    
    return redirect('mass_create_questions', test_id=test_id)

@login_required(login_url='login')
def add_question(request, test_id):
    test = get_object_or_404(Test, id=test_id, author=request.user)
    
    if request.method == 'POST':
        try:
            # Form ma'lumotlarini olish
            question_text = request.POST.get('question', '').strip()
            a_text = request.POST.get('a', '').strip()
            b_text = request.POST.get('b', '').strip()
            c_text = request.POST.get('c', '').strip()
            d_text = request.POST.get('d', '').strip()
            true_answer = request.POST.get('true_answer', '').strip().lower()
            
            # Ma'lumotlarni tekshirish
            if not all([question_text, a_text, b_text, c_text, d_text, true_answer]):
                return JsonResponse({'success': False, 'error': 'Barcha maydonlarni to\'ldiring'})
            
            if true_answer not in ['a', 'b', 'c', 'd']:
                return JsonResponse({'success': False, 'error': 'Noto\'g\'ri javob formati'})
            
            # Savolni saqlash
            question = Question.objects.create(
                test=test,
                question=question_text,
                a=a_text,
                b=b_text,
                c=c_text,
                d=d_text,
                true_answer=true_answer
            )
            
            # AJAX so'rovi bo'lsa JSON qaytarish
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': 'Savol muvaffaqiyatli saqlandi',
                    'question_id': question.id
                })
            
            # Oddiy POST so'rovi bo'lsa
            request.session['success_message'] = "Savol muvaffaqiyatli qo'shildi"
            return redirect('mass_create_questions', test_id=test_id)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            
            request.session['error_message'] = f"Xatolik: {str(e)}"
            return redirect('add_question', test_id=test_id)
    
    # GET so'rovi
    success_message = request.session.pop('success_message', None)
    error_message = request.session.pop('error_message', None)
    
    return render(request, 'add_question.html', {
        'test': test,
        'success_message': success_message,
        'error_message': error_message,
    })
@login_required(login_url='login')
def mass_create_questions(request, test_id):
    try:
        test = get_object_or_404(Test, id=test_id, author=request.user)
        
        # Session dan xabarlarni olish va o'chirish
        success_message = request.session.pop('success_message', None)
        error_message = request.session.pop('error_message', None)
        
        context = {
            'test': test,
            'success_message': success_message,
            'error_message': error_message,
        }
        
        return render(request, 'mass_create_questions.html', context)
    
    except Exception as e:
        print(f"Xatolik: {str(e)}")  # Debug uchun
        return render(request, 'error.html', {'error': str(e)})
