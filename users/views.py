from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Usuário ou senha inválida.')

    return render(request, 'users/login.html')
    #return render(request, 'users/login_alt.html') # Login Alternativo


def logout_view(request):
    logout(request)
    return render(request, 'users/logout.html')

@login_required
def profile_view(request):
    return render(request, 'users/profile.html')