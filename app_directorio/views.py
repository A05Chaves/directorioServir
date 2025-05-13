from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required,  user_passes_test
from .models import Edificio
from django.contrib import messages


@login_required
def home(request):
    edificios = Edificio.objects.all()

    # Agregar un nuevo edificio
    if request.method == 'POST' and 'agregar' in request.POST:
        nuevo_edificio = request.POST.get('nombre')
        if nuevo_edificio:
            if not Edificio.objects.filter(nombre=nuevo_edificio).exists():
                Edificio.objects.create(nombre=nuevo_edificio)
                messages.success(request, f'Edificio "{nuevo_edificio}" agregado correctamente.')
            else:
                messages.error(request, f'El edificio "{nuevo_edificio}" ya existe.')
        return redirect('home')

    return render(request, 'home.html', {'edificios': edificios})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def eliminar_edificio(request, edificio_id):
    if request.method == 'POST':
        try:
            edificio = Edificio.objects.get(id=edificio_id)
            edificio.delete()
            messages.success(request, f'Edificio "{edificio.nombre}" eliminado correctamente.')
        except Edificio.DoesNotExist:
            messages.error(request, 'El edificio no existe.')
        return redirect('home')
    return redirect('home')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return render(request, "login.html")
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('login')