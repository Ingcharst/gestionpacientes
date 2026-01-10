"""
Formularios para el módulo de terapias.
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Div, HTML, Field, Fieldset
from .models import CategoriaTerapia, Terapia


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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            Row(
                Column('nombre', css_class='col-md-6'),
                Column('codigo', css_class='col-md-6'),
            ),
            'descripcion',
            Row(
                Column('color', css_class='col-md-4'),
                Column('icono', css_class='col-md-4'),
                Column('orden', css_class='col-md-4'),
            ),
            Field('activo', css_class='form-check-input'),
            Div(
                Submit('submit', 'Guardar', css_class='btn btn-primary'),
                HTML('<a href="{% url "categoria_list" %}" class="btn btn-secondary ms-2">Cancelar</a>'),
                css_class='mt-3'
            )
        )


class TerapiaForm(forms.ModelForm):
    """Formulario para crear y editar terapias."""
    
    class Meta:
        model = Terapia
        fields = [
            'nombre', 'codigo', 'categoria',
            'descripcion', 'descripcion_corta',
            'modalidad', 'especialidad', 'nivel_intensidad',
            'duracion_minutos', 'frecuencia_semanal_recomendada',
            'costo_sesion', 'permite_descuento',
            'edad_minima', 'edad_maxima',
            'requiere_evaluacion_previa', 'requiere_orden_medica',
            'capacidad_minima', 'capacidad_maxima',
            'requiere_acompanante',
            'disponible_online', 'disponible_domicilio',
            'activo', 'destacado'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'descripcion_corta': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
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
        self.helper.layout = Layout(
            Fieldset(
                'Información Básica',
                Row(
                    Column('nombre', css_class='col-md-6'),
                    Column('codigo', css_class='col-md-6'),
                ),
                'categoria',
                'descripcion',
                'descripcion_corta',
            ),
            Fieldset(
                'Clasificación',
                Row(
                    Column('modalidad', css_class='col-md-4'),
                    Column('especialidad', css_class='col-md-4'),
                    Column('nivel_intensidad', css_class='col-md-4'),
                ),
            ),
            Fieldset(
                'Duración y Costo',
                Row(
                    Column('duracion_minutos', css_class='col-md-4'),
                    Column('frecuencia_semanal_recomendada', css_class='col-md-4'),
                    Column('costo_sesion', css_class='col-md-4'),
                ),
                Field('permite_descuento', css_class='form-check-input'),
            ),
            Fieldset(
                'Requisitos',
                Row(
                    Column('edad_minima', css_class='col-md-6'),
                    Column('edad_maxima', css_class='col-md-6'),
                ),
                Field('requiere_evaluacion_previa', css_class='form-check-input'),
                Field('requiere_orden_medica', css_class='form-check-input'),
            ),
            Fieldset(
                'Capacidad',
                Row(
                    Column('capacidad_minima', css_class='col-md-6'),
                    Column('capacidad_maxima', css_class='col-md-6'),
                ),
                Field('requiere_acompanante', css_class='form-check-input'),
            ),
            Fieldset(
                'Disponibilidad',
                Field('disponible_online', css_class='form-check-input'),
                Field('disponible_domicilio', css_class='form-check-input'),
            ),
            Fieldset(
                'Estado',
                Field('activo', css_class='form-check-input'),
                Field('destacado', css_class='form-check-input'),
            ),
            Div(
                Submit('submit', 'Guardar', css_class='btn btn-primary'),
                HTML('<a href="{% url "terapia_list" %}" class="btn btn-secondary ms-2">Cancelar</a>'),
                css_class='mt-3'
            )
        )


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
