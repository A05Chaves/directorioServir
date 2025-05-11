from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def home(request):
    contexto = {}
    return render(request, "home.html", contexto)

def login_view(request):
    # Si el usuario ya está autenticado, redirigir al home
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, "login.html", {'error': 'Usuario o contraseña incorrectos'})
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect('login')