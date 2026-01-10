from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from main.models import Organizer, Student


def home(request):
    # Send them straight to the dashboard if authenticated
    if request.user.is_authenticated:
        # Check if user is an organizer or student using try/except for OneToOne relationships
        try:
            # Try to access the reverse OneToOne relationship
            organizer = request.user.organizer
            return redirect('org-page')
        except Organizer.DoesNotExist:
            pass
        
        try:
            # Try to access the reverse OneToOne relationship
            student = request.user.student
            return redirect('student-page')
        except Student.DoesNotExist:
            pass
    
    # Landing page with the two login forms
    return render(request, 'main/index.html')


