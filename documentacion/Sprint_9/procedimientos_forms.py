"""
Formularios Django para procedimientos.
"""
from django import forms
from apps.procedimientos.models import (
    Paciente, Procedimiento, SesionTerapeutica,
    ObjetivoTerapeutico, EvolucionPaciente
)


class PacienteForm(forms.ModelForm):
    """Formulario para crear/editar pacientes."""
    
    class Meta:
        model = Paciente
        exclude = ['creado_por', 'fecha_creacion', 'fecha_actualizacion']

        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_alta': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'necesidades_especiales': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'diagnostico_principal': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'alergias': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'medicamentos': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'motivo_inactividad': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS a todos los campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs['class'] = 'form-select'
            elif not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'


class ProcedimientoForm(forms.ModelForm):
    """Formulario para crear/editar procedimientos."""
    
    class Meta:
        model = Procedimiento
        exclude = ['creado_por', 'fecha_creacion', 'fecha_actualizacion', 'duracion_minutos', 'codigo']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'motivo_consulta': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'hallazgos': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'diagnostico': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'plan_tratamiento': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'recomendaciones': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'motivo_cancelacion': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS a todos los campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs['class'] = 'form-select'
            elif not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'
        
        # Configurar valores iniciales
        if not self.instance.pk:  # Solo para nuevas instancias
            from django.utils import timezone
            self.fields['fecha'].initial = timezone.now().date()
            self.fields['costo'].initial = 0.00


class SesionTerapeuticaForm(forms.ModelForm):
    """Formulario para crear/editar sesiones terapéuticas."""
    
    class Meta:
        model = SesionTerapeutica
        exclude = [
            'creado_por', 'fecha_creacion', 'fecha_actualizacion',
            'duracion_real_minutos', 'procedimiento', 'numero_sesion'
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'objetivos_sesion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'actividades_realizadas': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'logros_sesion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'dificultades_presentadas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'observaciones_terapeuta': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'recomendaciones_proxima_sesion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'tareas_casa': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'motivo_cancelacion': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS a todos los campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs['class'] = 'form-select'
            elif not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'
        
        # Configurar valores iniciales para campos opcionales pero importantes
        if not self.instance.pk:  # Solo para nuevas instancias
            from django.utils import timezone
            self.fields['fecha'].initial = timezone.now().date()
            self.fields['duracion_programada_minutos'].initial = 60  # 1 hora por defecto


class ObjetivoTerapeuticoForm(forms.ModelForm):
    """Formulario para crear/editar objetivos terapéuticos."""
    
    class Meta:
        model = ObjetivoTerapeutico
        exclude = ['creado_por', 'fecha_creacion', 'fecha_actualizacion']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_limite': forms.DateInput(attrs={'type': 'date'}),
            'fecha_logro': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'criterios_exito': forms.Textarea(attrs={'rows': 3}),
            'estrategias': forms.Textarea(attrs={'rows': 3}),
            'notas': forms.Textarea(attrs={'rows': 2}),
        }


class EvolucionPacienteForm(forms.ModelForm):
    """Formulario para crear/editar evoluciones."""
    
    class Meta:
        model = EvolucionPaciente
        exclude = ['fecha_creacion', 'fecha_actualizacion']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'contenido': forms.Textarea(attrs={'rows': 5}),
            'observaciones_conducta': forms.Textarea(attrs={'rows': 3}),
            'observaciones_comunicacion': forms.Textarea(attrs={'rows': 3}),
            'observaciones_socializacion': forms.Textarea(attrs={'rows': 3}),
            'cambios_medicacion': forms.Textarea(attrs={'rows': 2}),
        }
