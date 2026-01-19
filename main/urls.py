from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('<int:test_id>/ready_to_test/', views.ready_to_test, name='ready_to_test'),
    path('<int:test_id>/test/', views.test, name='test'),
    path('result/<int:checktest_id>/', views.test_result, name='test_result'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('create-test/', views.create_test, name='create_test'), 
    path('add-question-field/', views.add_question_field, name='add_question_field'), # <- QO'SHING
    path('my-tests/', views.my_tests, name='my_tests'),  # <- QO'SHING
    path('test/<int:test_id>/detail/', views.test_detail, name='test_detail'),  # <- QO'SHING
    path('test/<int:test_id>/import-questions/', views.import_questions, name='import_questions'),
    path('test/<int:test_id>/parse-questions/', views.parse_questions, name='parse_questions'),
    path('test/<int:test_id>/mass-create/', views.mass_create_questions, name='mass_create_questions'),
    path('test/<int:test_id>/add-question/', views.add_question, name='add_question'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('test/<int:test_id>/review/', views.add_review, name='add_review'),
    path('result/<int:checktest_id>/certificate/', views.generate_certificate, name='generate_certificate'),
]