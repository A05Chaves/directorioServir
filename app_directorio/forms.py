from django import forms
from .models import Directorio


class DirectorioForm(forms.ModelForm):
    class Meta:
        model = Directorio
        fields = [
            'torre_bloque',
            'oficina',
            'nombre_oficina',
            'apto',
            'nombre',
            'cedula',
            'telefono',
            'telefono2',
            'informacion_adicional',
            'correo_propietario',
            'numero_parqueadero',
            'tipo_vehiculo',
            'marca',
            'color',
            'placa',
            'observaciones',
        ]

        widgets = {
            'torre_bloque': forms.TextInput(attrs={'class': 'form-control'}),
            'oficina': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_oficina': forms.TextInput(attrs={'class': 'form-control'}),
            'apto': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono2': forms.TextInput(attrs={'class': 'form-control'}),
            'informacion_adicional': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'correo_propietario': forms.EmailInput(attrs={'class': 'form-control'}),
            'numero_parqueadero': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_vehiculo': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'placa': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '6'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
# CARGA EL ARCHIVO EN FORMATO EXCEL


class CargaExcelForm(forms.Form):
    archivo_excel = forms.FileField(
        label='Subir archivo Excel',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
