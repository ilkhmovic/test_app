from django.urls import path
from . import views
from .user_view import signup

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', signup, name='signup'),
    path('<int:test_id>/ready_to_test/', views.ready_to_test, name='ready_to_test'),
    path('<int:test_id>/test', views.test, name='test'),
]