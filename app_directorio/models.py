from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Edificio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Directorio(models.Model):
    edificio = models.ForeignKey(Edificio, on_delete=models.CASCADE)

    torre_bloque = models.CharField(max_length=50, blank=True, null=True)
    oficina = models.CharField(max_length=50, blank=True, null=True)
    nombre_oficina = models.CharField(max_length=100, blank=True, null=True)
    apto = models.CharField(max_length=50, blank=True, null=True)
    nombre = models.CharField(max_length=150, blank=True, null=True)
    cedula = models.CharField(max_length=30, blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    telefono2 = models.CharField(max_length=30, blank=True, null=True)
    informacion_adicional = models.TextField(blank=True, null=True)
    correo_propietario = models.EmailField(blank=True, null=True)
    numero_parqueadero = models.CharField(max_length=50, blank=True, null=True)
    tipo_vehiculo = models.CharField(max_length=50, blank=True, null=True)
    marca = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    placa = models.CharField(max_length=6, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='directorios_creados'
    )

    actualizado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='directorios_actualizados'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre or f"Registro {self.id}"
