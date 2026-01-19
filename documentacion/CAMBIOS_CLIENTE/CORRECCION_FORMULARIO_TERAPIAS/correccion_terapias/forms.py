"""
Formularios para el módulo de terapias - CORREGIDO COMPLETO
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Div, HTML, Field, Fieldset
from .models import CategoriaTerapia, Terapia


class TerapiaForm(forms.ModelForm):
    """Formulario para crear y editar terapias - COMPLETO."""
    
    class Meta:
        model = Terapia
        fields = [
            # Información Básica
            'nombre', 'codigo', 'categoria',
            'descripcion', 'descripcion_corta',
            'imagen',  # AGREGADO
            
            # Clasificación
            'modalidad', 'especialidad', 'nivel_intensidad',
            
            # Duración y Frecuencia
            'duracion_minutos', 'frecuencia_semanal_recomendada',
            
            # Costos
            'costo_sesion', 'permite_descuento',
            
            # Requisitos
            'edad_minima', 'edad_maxima',
            'requiere_evaluacion_previa', 'requiere_orden_medica',
            
            # Capacidad
            'capacidad_minima', 'capacidad_maxima',
            'requiere_acompanante',
            
            # Información Adicional - AGREGADOS
            'objetivos',
            'metodologia',
            'contraindicaciones',
            
            # Disponibilidad
            'disponible_online', 'disponible_domicilio',
            
            # Estado
            'activo', 'destacado'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'descripcion_corta': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),  # AGREGADO
            
            'modalidad': forms.Select(attrs={'class': 'form-select'}),
            'especialidad': forms.Select(attrs={'class': 'form-select'}),
            'nivel_intensidad': forms.Select(attrs={'class': 'form-select'}),
            
            'duracion_minutos': forms.NumberInput(attrs={'class': 'form-control'}),
            'frecuencia_semanal_recomendada': forms.NumberInput(attrs={'class': 'form-control'}),
            
            'costo_sesion': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'permite_descuento': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            
            'edad_minima': forms.NumberInput(attrs={'class': 'form-control'}),
            'edad_maxima': forms.NumberInput(attrs={'class': 'form-control'}),
            'requiere_evaluacion_previa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requiere_orden_medica': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            
            'capacidad_minima': forms.NumberInput(attrs={'class': 'form-control'}),
            'capacidad_maxima': forms.NumberInput(attrs={'class': 'form-control'}),
            'requiere_acompanante': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            
            # AGREGADOS
            'objetivos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'metodologia': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'contraindicaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
            'disponible_online': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'disponible_domicilio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'destacado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        # Layout removido - usar template manual


class CategoriaTerapiaForm(forms.ModelForm):
    """Formulario para crear y editar categorías de terapias."""
    
    class Meta:
        model = CategoriaTerapia
        fields = [
            'nombre', 'codigo', 'descripcion',
            'color', 'icono', 'orden', 'activo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'icono': forms.TextInput(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FiltroTerapiaForm(forms.Form):
    """Formulario para filtrar terapias."""
    
    categoria = forms.ModelChoiceField(
        queryset=CategoriaTerapia.objects.filter(activo=True),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    modalidad = forms.ChoiceField(
        choices=[('', 'Todas las modalidades')] + list(Terapia.Modalidad.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    especialidad = forms.ChoiceField(
        choices=[('', 'Todas las especialidades')] + list(Terapia.Especialidad.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    solo_destacadas = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, descripción...'
        })
    )
