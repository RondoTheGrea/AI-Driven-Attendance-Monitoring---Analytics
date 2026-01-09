from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.contrib import messages

def org_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('org-page')

        messages.error(request, 'Invalid organization credentials.')
        return redirect('home')

    # Non-POST should just show the login page
    return redirect('home')

def org_page(request):
    return render(request, 'main/org-page.html')
