from django import forms
from .models import Directorio


class DirectorioForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.edificio = kwargs.pop('edificio', None)
        super().__init__(*args, **kwargs)

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

    def clean(self):
        cleaned_data = super().clean()

        for campo, valor in cleaned_data.items():
            if isinstance(valor, str):
                cleaned_data[campo] = valor.upper().strip()

        return cleaned_data

    # METODO PARA VALIDAR PLACA NO MAYOR A 6 DIGITOS

    def clean_placa(self):
        placa = self.cleaned_data.get('placa')

        if placa:
            placa = placa.upper().strip()

            if len(placa) > 6:
                raise forms.ValidationError(
                    "La placa no puede tener más de 6 caracteres.")

        return placa

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')

        if cedula and self.edificio:
            cedula = cedula.strip()

            existe = Directorio.objects.filter(
                edificio=self.edificio,
                cedula=cedula
            )

            if self.instance.pk:
                existe = existe.exclude(pk=self.instance.pk)

            if existe.exists():
                raise forms.ValidationError(
                    "Ya existe un registro con esta cédula en este edificio."
                )

        return cedula


# CARGA EL ARCHIVO EN FORMATO EXCEL


class CargaExcelForm(forms.Form):
    archivo_excel = forms.FileField(
        label='Subir archivo Excel',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
