from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render

def student_login(request):
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
    return render(request, 'main/student-page.html')