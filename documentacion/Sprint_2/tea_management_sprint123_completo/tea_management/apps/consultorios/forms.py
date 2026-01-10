"""
Formularios para el módulo de consultorios.
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Div, HTML, Field
from .models import Consultorio, Sala, AsignacionConsultorio, DisponibilidadConsultorio


class ConsultorioForm(forms.ModelForm):
    """Formulario para crear y editar consultorios."""
    
    class Meta:
        model = Consultorio
        fields = [
            'nombre', 'codigo', 'tipo', 'piso', 'numero',
            'capacidad', 'area_metros', 'estado', 'equipamiento',
            'caracteristicas', 'foto', 'tiene_ventana',
            'tiene_aire_acondicionado', 'accesible_silla_ruedas',
            'observaciones', 'activo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'piso': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '10'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '50'}),
            'area_metros': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'equipamiento': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'JSON: [{"nombre": "...", "cantidad": ...}]'
            }),
            'caracteristicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'tiene_ventana': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tiene_aire_acondicionado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'accesible_silla_ruedas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
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
            Row(
                Column('tipo', css_class='col-md-6'),
                Column('estado', css_class='col-md-6'),
            ),
            Row(
                Column('piso', css_class='col-md-4'),
                Column('numero', css_class='col-md-4'),
                Column('capacidad', css_class='col-md-4'),
            ),
            Row(
                Column('area_metros', css_class='col-md-6'),
                Column('foto', css_class='col-md-6'),
            ),
            Row(
                Column(
                    Field('tiene_ventana', css_class='form-check-input'),
                    css_class='col-md-4'
                ),
                Column(
                    Field('tiene_aire_acondicionado', css_class='form-check-input'),
                    css_class='col-md-4'
                ),
                Column(
                    Field('accesible_silla_ruedas', css_class='form-check-input'),
                    css_class='col-md-4'
                ),
            ),
            'caracteristicas',
            'equipamiento',
            'observaciones',
            Field('activo', css_class='form-check-input'),
            Div(
                Submit('submit', 'Guardar', css_class='btn btn-primary'),
                HTML('<a href="{% url "consultorio_list" %}" class="btn btn-secondary ms-2">Cancelar</a>'),
                css_class='mt-3'
            )
        )


class SalaForm(forms.ModelForm):
    """Formulario para crear y editar salas."""
    
    class Meta:
        model = Sala
        fields = [
            'consultorio', 'nombre', 'tipo',
            'area_metros', 'descripcion',
            'equipamiento_especifico', 'activo'
        ]
        widgets = {
            'consultorio': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'area_metros': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'equipamiento_especifico': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'JSON: [{"nombre": "...", "cantidad": ...}]'
            }),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            'consultorio',
            Row(
                Column('nombre', css_class='col-md-6'),
                Column('tipo', css_class='col-md-6'),
            ),
            Row(
                Column('area_metros', css_class='col-md-6'),
                Column(Field('activo', css_class='form-check-input'), css_class='col-md-6'),
            ),
            'descripcion',
            'equipamiento_especifico',
            Div(
                Submit('submit', 'Guardar', css_class='btn btn-primary'),
                HTML('<a href="{% url "consultorio_list" %}" class="btn btn-secondary ms-2">Cancelar</a>'),
                css_class='mt-3'
            )
        )


class AsignacionConsultorioForm(forms.ModelForm):
    """Formulario para crear y editar asignaciones."""
    
    class Meta:
        model = AsignacionConsultorio
        fields = [
            'consultorio', 'terapeuta', 'tipo_asignacion',
            'fecha_inicio', 'fecha_fin', 'horario',
            'dias_semana', 'prioridad', 'notas', 'activo'
        ]
        widgets = {
            'consultorio': forms.Select(attrs={'class': 'form-select'}),
            'terapeuta': forms.Select(attrs={'class': 'form-select'}),
            'tipo_asignacion': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'horario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'JSON: {"Lunes": {"hora_inicio": "09:00", "hora_fin": "12:00"}}'
            }),
            'dias_semana': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'JSON: ["Lunes", "Martes", "Miércoles"]'
            }),
            'prioridad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '5'
            }),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo terapeutas
        from apps.usuarios.models import Usuario
        self.fields['terapeuta'].queryset = Usuario.objects.filter(
            rol__in=[Usuario.Rol.TERAPEUTA, Usuario.Rol.PSICOLOGO, Usuario.Rol.MEDICO]
        )
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            Row(
                Column('consultorio', css_class='col-md-6'),
                Column('terapeuta', css_class='col-md-6'),
            ),
            Row(
                Column('tipo_asignacion', css_class='col-md-6'),
                Column('prioridad', css_class='col-md-6'),
            ),
            Row(
                Column('fecha_inicio', css_class='col-md-6'),
                Column('fecha_fin', css_class='col-md-6'),
            ),
            'dias_semana',
            'horario',
            'notas',
            Field('activo', css_class='form-check-input'),
            Div(
                Submit('submit', 'Guardar', css_class='btn btn-primary'),
                HTML('<a href="{% url "asignacion_list" %}" class="btn btn-secondary ms-2">Cancelar</a>'),
                css_class='mt-3'
            )
        )
    
    def clean(self):
        """Validaciones personalizadas."""
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_fin and fecha_inicio and fecha_inicio > fecha_fin:
            raise forms.ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })
        
        return cleaned_data


class DisponibilidadConsultorioForm(forms.ModelForm):
    """Formulario para gestionar disponibilidad de consultorios."""
    
    class Meta:
        model = DisponibilidadConsultorio
        fields = [
            'consultorio', 'fecha', 'hora_inicio', 'hora_fin',
            'estado', 'terapeuta', 'motivo_bloqueo', 'notas'
        ]
        widgets = {
            'consultorio': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'terapeuta': forms.Select(attrs={'class': 'form-select'}),
            'motivo_bloqueo': forms.TextInput(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo terapeutas
        from apps.usuarios.models import Usuario
        self.fields['terapeuta'].queryset = Usuario.objects.filter(
            rol__in=[Usuario.Rol.TERAPEUTA, Usuario.Rol.PSICOLOGO, Usuario.Rol.MEDICO]
        )
        self.fields['terapeuta'].required = False
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            Row(
                Column('consultorio', css_class='col-md-6'),
                Column('estado', css_class='col-md-6'),
            ),
            Row(
                Column('fecha', css_class='col-md-6'),
                Column('terapeuta', css_class='col-md-6'),
            ),
            Row(
                Column('hora_inicio', css_class='col-md-6'),
                Column('hora_fin', css_class='col-md-6'),
            ),
            'motivo_bloqueo',
            'notas',
            Div(
                Submit('submit', 'Guardar', css_class='btn btn-primary'),
                HTML('<a href="{% url "disponibilidad_list" %}" class="btn btn-secondary ms-2">Cancelar</a>'),
                css_class='mt-3'
            )
        )
    
    def clean(self):
        """Validaciones personalizadas."""
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        
        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise forms.ValidationError({
                'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio.'
            })
        
        return cleaned_data


class FiltroConsultorioForm(forms.Form):
    """Formulario para filtrar consultorios."""
    
    tipo = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + list(Consultorio.TipoConsultorio.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + list(Consultorio.EstadoConsultorio.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    piso = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Piso'
        })
    )
    
    activo = forms.ChoiceField(
        choices=[('', 'Todos'), ('true', 'Activos'), ('false', 'Inactivos')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, código o número...'
        })
    )
