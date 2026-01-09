from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render


def home(request):
    # Send them straight to the dashboard if authenticated
    if request.user.is_authenticated:
        # Check if user is an organizer or student
        if hasattr(request.user, 'organizer'):
            return redirect('org-page')
        elif hasattr(request.user, 'student'):
            return redirect('student-page')
    
    # Landing page with the two login forms
    return render(request, 'main/index.html')


