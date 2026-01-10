# student/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.student_login, name='student-login'),
    path('dashboard/', views.student_page, name='student-page'),
    path('logout/', views.student_logout, name='student-logout'),
]
