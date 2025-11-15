from django.urls import path
from . import views
from .user_view import signup

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', signup, name='signup'),
    path('<int:test_id>/ready_to_test/', views.ready_to_test, name='ready_to_test'),
    path('<int:test_id>/test/', views.test, name='test'),
    path('result/<int:checktest_id>/', views.test_result, name='test_result'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('create-test/', views.create_test, name='create_test'), 
    path('add-question-field/', views.add_question_field, name='add_question_field'), # <- QO'SHING
    path('my-tests/', views.my_tests, name='my_tests'),  # <- QO'SHING
    path('test/<int:test_id>/detail/', views.test_detail, name='test_detail'),  # <- QO'SHING
]