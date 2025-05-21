from django import forms
from .models import Directorio


class DirectorioForm(forms.ModelForm):
    class Meta:
        model = Directorio
<<<<<<< HEAD
        fields = ['apto', 'nombre_apellido', 'documento', 'parentesco', 'celular1', 'celular2', 'observacion']
        widgets = {
            'apto':forms.TextInput( attrs={'class': 'form-control'}),
=======
        fields = ['apto', 'nombre_apellido', 'documento', 'parentesco',
                  'celular1', 'celular2', 'observacion']
        widgets = {
            # Nuevo campo
            'apto': forms.TextInput(attrs={'class': 'form-control'}),
>>>>>>> 2ac13a41a0cc1aff3811d291c2f75f0f15db021c
            'nombre_apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'documento': forms.TextInput(attrs={'class': 'form-control'}),
            'parentesco': forms.TextInput(attrs={'class': 'form-control'}),
            'celular1': forms.TextInput(attrs={'class': 'form-control'}),
            'celular2': forms.TextInput(attrs={'class': 'form-control'}),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

# CARGA EL ARCHIVO EN FORMATO EXCEL


class CargaExcelForm(forms.Form):
    archivo_excel = forms.FileField(
        label='Subir archivo Excel',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
