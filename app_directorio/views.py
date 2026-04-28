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
import os
import subprocess
from django.conf import settings
import pandas as pd
from django.http import HttpResponse


@login_required
def home(request):
    edificios = Edificio.objects.all()

    if request.method == 'POST' and 'agregar' in request.POST:

        if not request.user.is_superuser:
            messages.error(
                request, "No tienes permisos para agregar edificios.")
            return redirect('home')

        nuevo_edificio = request.POST.get('nombre', '').strip().upper()

        if nuevo_edificio:
            if not Edificio.objects.filter(nombre=nuevo_edificio).exists():
                Edificio.objects.create(nombre=nuevo_edificio)
                messages.success(
                    request,
                    f'Edificio "{nuevo_edificio}" agregado correctamente.'
                )
            else:
                messages.error(
                    request,
                    f'El edificio "{nuevo_edificio}" ya existe.'
                )
        else:
            messages.error(request, "Debes ingresar un nombre válido.")

        return redirect('home')

    return render(request, 'home.html', {'edificios': edificios})

# AJUSTE NUEVO 17 DE MAYO


@login_required
def directorio_edificio(request, edificio_id):
    edificio = get_object_or_404(Edificio, id=edificio_id)

    filtro = request.GET.get('filtro', '')

    directorio = Directorio.objects.filter(edificio=edificio)

    if filtro:
        directorio = directorio.filter(
            models.Q(nombre__icontains=filtro) |
            models.Q(cedula__icontains=filtro) |
            models.Q(apto__icontains=filtro) |
            models.Q(telefono__icontains=filtro) |
            models.Q(telefono2__icontains=filtro) |
            models.Q(placa__icontains=filtro)
        )

    form_excel = CargaExcelForm()

    if request.method == 'POST' and 'carga_excel' in request.POST:
        form_excel = CargaExcelForm(request.POST, request.FILES)

        if form_excel.is_valid():
            archivo = request.FILES['archivo_excel']

            try:
                if not archivo.name.endswith(('.xls', '.xlsx')):
                    messages.error(
                        request, 'Formato no soportado. Cargue un archivo Excel.')
                    return redirect('directorio_edificio', edificio_id=edificio.id)

                df = pd.read_excel(BytesIO(archivo.read())).fillna('')

                columnas_requeridas = [
                    'TORRE/BLOQUE', 'OFICINA', 'NOMBRE OFICINA', 'APTO',
                    'NOMBRE', 'CÉDULA', 'TELÉFONO 1', 'TELÉFONO 2',
                    'INFORMACIÓN ADICIONAL', 'CORREO PROPIETARIO',
                    'NÚMERO PARQUEADERO', 'TIPO VEHÍCULO', 'MARCA',
                    'COLOR', 'PLACA (6 CARACTERES)', 'OBSERVACIONES'
                ]

                columnas_faltantes = [
                    col for col in columnas_requeridas if col not in df.columns
                ]

                if columnas_faltantes:
                    messages.error(
                        request,
                        f'Faltan columnas: {", ".join(columnas_faltantes)}'
                    )
                    return redirect('directorio_edificio', edificio_id=edificio.id)

                for col in columnas_requeridas:
                    df[col] = (
                        df[col]
                        .astype(str)
                        .str.replace(r'\.0$', '', regex=True)
                        .str.strip().str.upper()
                    )

                creados = 0
                actualizados = 0

                for _, row in df.iterrows():
                    nombre = row['NOMBRE']
                    cedula = row['CÉDULA']
                    apto = row['APTO']

                    if not nombre and not cedula and not apto:
                        continue

                    obj, creado = Directorio.objects.update_or_create(
                        edificio=edificio,
                        cedula=cedula,
                        defaults={
                            'torre_bloque': row['TORRE/BLOQUE'],
                            'oficina': row['OFICINA'],
                            'nombre_oficina': row['NOMBRE OFICINA'],
                            'apto': row['APTO'],
                            'nombre': row['NOMBRE'],
                            'telefono': row['TELÉFONO 1'],
                            'telefono2': row['TELÉFONO 2'],
                            'informacion_adicional': row['INFORMACIÓN ADICIONAL'],
                            'correo_propietario': row['CORREO PROPIETARIO'],
                            'numero_parqueadero': row['NÚMERO PARQUEADERO'],
                            'tipo_vehiculo': row['TIPO VEHÍCULO'],
                            'marca': row['MARCA'],
                            'color': row['COLOR'],
                            'placa': row['PLACA (6 CARACTERES)'],
                            'observaciones': row['OBSERVACIONES'],
                        }
                    )

                    if creado:
                        creados += 1
                    else:
                        actualizados += 1

                messages.success(
                    request,
                    f'Importación completada. Creados: {creados}. Actualizados: {actualizados}.'
                )

                return redirect('directorio_edificio', edificio_id=edificio.id)

            except Exception as e:
                messages.error(
                    request, f'Error al procesar el archivo: {str(e)}')
                return redirect('directorio_edificio', edificio_id=edificio.id)

    return render(request, 'directorio.html', {
        'edificio': edificio,
        'directorio': directorio,
        'form_excel': form_excel,
        'filtro': filtro,
    })


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
    resultados = list(directorio.values('apto', 'nombre_apellido',
                      'documento', 'parentesco', 'celular1', 'celular2', 'observacion'))
    return JsonResponse({'resultados': resultados})


@login_required
def editar_residente(request, edificio_id, residente_id):
    edificio = get_object_or_404(Edificio, id=edificio_id)
    residente = get_object_or_404(
        Directorio, id=residente_id, edificio=edificio)

    if request.method == 'POST':
        form = DirectorioForm(
            request.POST, instance=residente, edificio=edificio)
        if form.is_valid():
            residente_editado = form.save(commit=False)
            residente_editado.actualizado_por = request.user
            residente_editado.save()

            messages.success(request, 'Residente actualizado correctamente.')
            return redirect('directorio_edificio', edificio_id=edificio.id)
    else:
        form = DirectorioForm(instance=residente, edificio=edificio)

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
        form = DirectorioForm(request.POST, edificio=edificio)
        if form.is_valid():
            nuevo_residente = form.save(commit=False)
            nuevo_residente.edificio = edificio
            nuevo_residente.creado_por = request.user
            nuevo_residente.actualizado_por = request.user
            nuevo_residente.save()
            messages.success(request, 'Residente agregado correctamente.')
            return redirect('directorio_edificio', edificio_id=edificio.id)
    else:
        form = DirectorioForm(edificio=edificio)

    context = {
        'edificio': edificio,
        'form': form,
    }
    return render(request, 'agregar_residente.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
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
            messages.success(
                request, f'Edificio "{edificio.nombre}" eliminado correctamente.')
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
    return redirect('login')

# Función para realizar la llamada usando ADB
# def llamar_telefono(numero):
 #   comando = f'adb shell am start -a android.intent.action.CALL -d tel:{numero}'
  #  resultado = os.system(comando)
   # return resultado == 0

# METODO PARA REALIZAR LLAMADAS
# def llamar_telefono(numero):
    # comando = f'adb shell am start -a android.intent.action.CALL -d tel:{numero}' no funciono
    # adb_path = r'C:\adb\platform-tools\adb.exe'  # Usa tu ruta real aquí funcina local
    # comando = f'"{adb_path}" shell am start -a android.intent.action.CALL -d tel:{numero}' funciona local


def llamar_telefono(numero):
    adb_path = getattr(settings, "ADB_PATH", "adb")
    comando = f'"{adb_path}" shell am start -a android.intent.action.CALL -d tel:{numero}'
    ...

    try:
        resultado = subprocess.run(
            comando, shell=True, capture_output=True, text=True)
        print("STDOUT:", resultado.stdout)
        print("STDERR:", resultado.stderr)
        return resultado.returncode == 0
    except Exception as e:
        print("ERROR EJECUTANDO ADB:", e)
        return False

# Función para colgar la llamada usando ADB


def colgar_telefono():
    comando = "adb shell input keyevent KEYCODE_ENDCALL"
    resultado = os.system(comando)
    return resultado == 0

# Vista para realizar la llamada


@login_required
def realizar_llamada(request, edificio_id, telefono):
    if llamar_telefono(telefono):
        return JsonResponse({'status': 'success', 'message': f"Llamando al número {telefono}..."})
    else:
        return JsonResponse({'status': 'error', 'message': "Error al realizar la llamada."})

# Vista para colgar la llamada


@login_required
def colgar_llamada(request, edificio_id):
    if colgar_telefono():
        return JsonResponse({'status': 'success', 'message': "Llamada finalizada."})
    else:
        return JsonResponse({'status': 'error', 'message': "Error al colgar la llamada."})

# vista para exportar a Excel


@login_required
def exportar_directorio_excel(request, edificio_id):
    edificio = get_object_or_404(Edificio, id=edificio_id)
    registros = Directorio.objects.filter(edificio=edificio)

    data = []

    for r in registros:
        data.append({
            'TORRE/BLOQUE': r.torre_bloque or '',
            'OFICINA': r.oficina or '',
            'NOMBRE OFICINA': r.nombre_oficina or '',
            'APTO': r.apto or '',
            'NOMBRE': r.nombre or '',
            'CÉDULA': r.cedula or '',
            'TELÉFONO 1': r.telefono or '',
            'TELÉFONO 2': r.telefono2 or '',
            'INFORMACIÓN ADICIONAL': r.informacion_adicional or '',
            'CORREO PROPIETARIO': r.correo_propietario or '',
            'NÚMERO PARQUEADERO': r.numero_parqueadero or '',
            'TIPO VEHÍCULO': r.tipo_vehiculo or '',
            'MARCA': r.marca or '',
            'COLOR': r.color or '',
            'PLACA (6 CARACTERES)': r.placa or '',
            'OBSERVACIONES': r.observaciones or '',
        })

    df = pd.DataFrame(data)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    nombre_archivo = f"backup_directorio_{edificio.nombre}.xlsx".replace(
        " ", "_")

    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'

    df.to_excel(response, index=False)

    return response
