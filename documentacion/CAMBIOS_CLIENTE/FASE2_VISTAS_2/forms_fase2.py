# CREAR/MODIFICAR: apps/procedimientos/forms.py

from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Paciente, ValoracionProfesional, AdmisionTerapia, CodigoCIE10
from apps.grupos.models import Terapia


class PacienteRegistroForm(forms.ModelForm):
    """Registro simple sin admisión ni historia"""
    class Meta:
        model = Paciente
        fields = '__all__'  # Temporal - ajustar después
        exclude = ['numero_historia_clinica']  # Campo deprecado
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplicar clase form-control a todos los campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput, 
                                        forms.EmailInput, forms.Select, 
                                        forms.Textarea, forms.DateInput)):
                field.widget.attrs['class'] = 'form-control'
        
        # Select2 para código enfermedad si existe
        if 'codigo_enfermedad' in self.fields:
            self.fields['codigo_enfermedad'].widget.attrs['class'] = 'form-control select2'
            self.fields['codigo_enfermedad'].required = False
        
        # Fecha nacimiento como date input si existe
        if 'fecha_nacimiento' in self.fields:
            self.fields['fecha_nacimiento'].widget = forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            )


class ValoracionProfesionalForm(forms.ModelForm):
    """Valoración individual por terapeuta"""
    class Meta:
        model = ValoracionProfesional
        fields = [
            'terapia', 'estado_salud_general', 'observaciones',
            'recomendaciones', 'objetivos_terapeuticos'
        ]
        widgets = {
            'terapia': forms.Select(attrs={'class': 'form-control'}),
            'estado_salud_general': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recomendaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'objetivos_terapeuticos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AdmisionTerapiaForm(forms.ModelForm):
    """Admisión por terapia de EPS"""
    class Meta:
        model = AdmisionTerapia
        fields = [
            'terapia', 'numero_admision', 'cantidad_ordenada',
            'fecha_inicio'
        ]
        widgets = {
            'terapia': forms.Select(attrs={'class': 'form-control'}),
            'numero_admision': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad_ordenada': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fecha inicio por defecto: hoy
        if not self.instance.pk:
            self.fields['fecha_inicio'].initial = timezone.now().date()
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        
        if fecha_inicio:
            # Calcular fecha_fin (4 semanas = 28 días)
            cleaned_data['fecha_fin'] = fecha_inicio + timedelta(days=28)
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Calcular fecha_fin automáticamente
        instance.fecha_fin = instance.fecha_inicio + timedelta(days=28)
        if commit:
            instance.save()
        return instance


class CambioCupoGrupoForm(forms.Form):
    """Cambio de cupo máximo de grupo"""
    capacidad_maxima = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )
