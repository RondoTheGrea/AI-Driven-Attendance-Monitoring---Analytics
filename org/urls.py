# org/urls.py
from django.urls import path
from . import views  # Imports the views from the org folder

urlpatterns = [
    
    path('login/', views.org_login, name='org-login'),        # /org/login/
    path('dashboard/', views.org_page, name='org-page'),
]