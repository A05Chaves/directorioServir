from django.db import models

# Create your models here.

class Edificio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


# ACTUALIZACION DE MODELO PARA CARGAR LOS USUARIOS CON LA PLANTILLA

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