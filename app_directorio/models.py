from django.db import models

# Create your models here.


class Edificio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


# ACTUALIZACION DE MODELO PARA CARGAR LOS USUARIOS CON LA PLANTILLA
"""
class Directorio(models.Model):
    edificio = models.ForeignKey(Edificio, on_delete=models.CASCADE)
    apto = models.CharField(max_length=50, blank=True, null=True)  # Nuevo campo
    nombre_apellido = models.CharField(max_length=100)
    documento = models.CharField(max_length=50)
    parentesco = models.CharField(max_length=50)
    celular1 = models.CharField(max_length=20, blank=True, null=True)
    celular2 = models.CharField(max_length=20, blank=True, null=True)
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_apellido} - {self.edificio.nombre}"
    
"""


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

    def __str__(self):
        return self.nombre
