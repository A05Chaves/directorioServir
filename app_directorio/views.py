from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
import pandas as pd
from app_directorio.forms import CargaExcelForm, DirectorioForm
from .models import Directorio, Edificio
from io import BytesIO
from django.db import models
from django.http import JsonResponse
from django.db.models import Q

@login_required
def home(request):
    edificios = Edificio.objects.all()

    # Agregar un nuevo edificio
    if request.method == 'POST' and 'agregar' in request.POST:
        nuevo_edificio = request.POST.get('nombre').strip()
        if nuevo_edificio:
            if not Edificio.objects.filter(nombre=nuevo_edificio).exists():
                Edificio.objects.create(nombre=nuevo_edificio)
                messages.success(request, f'Edificio "{nuevo_edificio}" agregado correctamente.')
            else:
                messages.error(request, f'El edificio "{nuevo_edificio}" ya existe.')
        return redirect('home')

    return render(request, 'home.html', {'edificios': edificios})

# AJUSTE NUEVO 17 DE MAYO

@login_required
def directorio_edificio(request, edificio_id):
    edificio = get_object_or_404(Edificio, id=edificio_id)

    # Captura del filtro desde el formulario
    filtro = request.GET.get('filtro', '')

    # Filtrado de residentes por nombre o documento
    directorio = Directorio.objects.filter(edificio=edificio)
    if filtro:
        directorio = directorio.filter(
            models.Q(nombre_apellido__icontains=filtro) | models.Q(documento__icontains=filtro)
        )

    if request.method == 'POST':
        if 'carga_excel' in request.POST:
            form_excel = CargaExcelForm(request.POST, request.FILES)
            if form_excel.is_valid():
                archivo = request.FILES['archivo_excel']
                try:
                    # Verificar el tipo de archivo (Excel)
                    if not archivo.name.endswith(('.xls', '.xlsx')):
                        messages.error(request, 'Formato de archivo no soportado. Cargue un archivo Excel (.xls o .xlsx).')
                        return redirect('directorio_edificio', edificio_id=edificio.id)

                    # Leer el archivo Excel y reemplazar NaN con cadenas vacías
                    df = pd.read_excel(BytesIO(archivo.read())).fillna('')

                    # Convertir los números de celular a cadenas para evitar problemas de formato
                    df['CELULAR 1'] = df['CELULAR 1'].astype(str).str.replace(r'\.0$', '', regex=True)
                    df['CELULAR 2'] = df['CELULAR 2'].astype(str).str.replace(r'\.0$', '', regex=True)

                    # Validación de columnas
                    columnas_requeridas = [
                        'APTO', 'NOMBRE Y APELLIDO', 'DOCUMENTO', 'PARENTESCO', 'CELULAR 1', 'CELULAR 2', 'OBSERVACION'
                    ]
                    if not all(col in df.columns for col in columnas_requeridas):
                        messages.error(request, 'El archivo Excel no contiene las columnas requeridas.')
                        return redirect('directorio_edificio', edificio_id=edificio.id)

                    # Guardar cada fila en la base de datos
                    for _, row in df.iterrows():
                        Directorio.objects.update_or_create(
                            edificio=edificio,
                            nombre_apellido=row['NOMBRE Y APELLIDO'],
                            defaults={
                                'apto': row['APTO'],
                                'documento': str(row['DOCUMENTO']),
                                'parentesco': row['PARENTESCO'],
                                'celular1': str(row['CELULAR 1']),
                                'celular2': str(row['CELULAR 2']),
                                'observacion': row['OBSERVACION'],
                            }
                        )
                    messages.success(request, 'Directorio cargado desde Excel correctamente.')
                except Exception as e:
                    messages.error(request, f'Error al procesar el archivo: {str(e)}')
                return redirect('directorio_edificio', edificio_id=edificio.id)

        else:
            form = DirectorioForm(request.POST)
            if form.is_valid():
                nuevo_residente = form.save(commit=False)
                nuevo_residente.edificio = edificio
                nuevo_residente.save()
                messages.success(request, 'Residente agregado correctamente.')
            return redirect('directorio_edificio', edificio_id=edificio.id)

    form = DirectorioForm()
    form_excel = CargaExcelForm()

    context = {
        'edificio': edificio,
        'directorio': directorio,
        'form': form,
        'form_excel': form_excel,
        'filtro': filtro,
    }
    return render(request, 'directorio.html', context)

@login_required
def filtrar_residentes(request, edificio_id):
    filtro = request.GET.get('filtro', '')
    edificio = get_object_or_404(Edificio, id=edificio_id)

    # Filtrado de residentes por nombre, documento o apto
    directorio = Directorio.objects.filter(edificio=edificio)
    if filtro:
        directorio = directorio.filter(
            Q(nombre_apellido__icontains=filtro) |
            Q(documento__icontains=filtro) |
            Q(apto__icontains=filtro)
        )

    # Convertir los resultados a una lista de diccionarios
    resultados = list(directorio.values('apto', 'nombre_apellido', 'documento', 'parentesco', 'celular1', 'celular2', 'observacion'))
    return JsonResponse({'resultados': resultados})


@login_required
def editar_residente(request, edificio_id, residente_id):
    edificio = get_object_or_404(Edificio, id=edificio_id)
    residente = get_object_or_404(Directorio, id=residente_id)

    if request.method == 'POST':
        form = DirectorioForm(request.POST, instance=residente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Residente actualizado correctamente.')
            return redirect('directorio_edificio', edificio_id=edificio.id)
    else:
        form = DirectorioForm(instance=residente)

    context = {
        'edificio': edificio,
        'residente': residente,
        'form': form
    }
    return render(request, 'editar_residente.html', context)

@login_required
def agregar_residente(request, edificio_id):
    edificio = get_object_or_404(Edificio, id=edificio_id)

    if request.method == 'POST':
        form = DirectorioForm(request.POST)
        if form.is_valid():
            nuevo_residente = form.save(commit=False)
            nuevo_residente.edificio = edificio
            nuevo_residente.save()
            messages.success(request, 'Residente agregado correctamente.')
            return redirect('directorio_edificio', edificio_id=edificio.id)
    else:
        form = DirectorioForm()

    context = {
        'edificio': edificio,
        'form': form,
    }
    return render(request, 'agregar_residente.html', context)

@login_required
def eliminar_residente(request, edificio_id, residente_id):
    edificio = get_object_or_404(Edificio, id=edificio_id)
    try:
        residente = Directorio.objects.get(id=residente_id, edificio=edificio)
        residente.delete()
        messages.success(request, f'Registro eliminado correctamente.')
    except Directorio.DoesNotExist:
        messages.error(request, 'El residente no existe o ya fue eliminado.')
    return redirect('directorio_edificio', edificio_id=edificio.id)



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

def logout_view(request):
    logout(request)
    #messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('login')
