from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from main.models import Organizer, Student

def student_login(request):
    # If already logged in, redirect to appropriate dashboard
    if request.user.is_authenticated:
        try:
            request.user.student
            return redirect('student-page')
        except Student.DoesNotExist:
            try:
                request.user.organizer
                return redirect('org-page')
            except Organizer.DoesNotExist:
                pass
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('student-page')

        messages.error(request, 'Invalid student credentials.')
        return redirect('home')

    return redirect('home')


def student_page(request):
    return render(request, 'student/dashboard.html')

def student_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')