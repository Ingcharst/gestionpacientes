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
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
            'fecha_alta': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
            'necesidades_especiales': forms.Textarea(attrs={'rows': 3}),
            'diagnostico_principal': forms.Textarea(attrs={'rows': 2}),
            'alergias': forms.Textarea(attrs={'rows': 2}),
            'medicamentos': forms.Textarea(attrs={'rows': 2}),
            'motivo_inactividad': forms.Textarea(attrs={'rows': 2}),
        }


class ProcedimientoForm(forms.ModelForm):
    """Formulario para crear/editar procedimientos."""
    
    class Meta:
        model = Procedimiento
        exclude = ['creado_por', 'fecha_creacion', 'fecha_actualizacion', 'duracion_minutos']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
            'motivo_consulta': forms.Textarea(attrs={'rows': 3}),
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'hallazgos': forms.Textarea(attrs={'rows': 3}),
            'diagnostico': forms.Textarea(attrs={'rows': 3}),
            'plan_tratamiento': forms.Textarea(attrs={'rows': 3}),
            'recomendaciones': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 2}),
            'motivo_cancelacion': forms.Textarea(attrs={'rows': 2}),
        }


class SesionTerapeuticaForm(forms.ModelForm):
    """Formulario para crear/editar sesiones terapéuticas."""
    
    class Meta:
        model = SesionTerapeutica
        exclude = [
            'creado_por', 'fecha_creacion', 'fecha_actualizacion',
            'duracion_real_minutos', 'procedimiento'
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
            'objetivos_sesion': forms.Textarea(attrs={'rows': 3}),
            'actividades_realizadas': forms.Textarea(attrs={'rows': 4}),
            'logros_sesion': forms.Textarea(attrs={'rows': 3}),
            'dificultades_presentadas': forms.Textarea(attrs={'rows': 3}),
            'observaciones_terapeuta': forms.Textarea(attrs={'rows': 3}),
            'recomendaciones_proxima_sesion': forms.Textarea(attrs={'rows': 3}),
            'tareas_casa': forms.Textarea(attrs={'rows': 3}),
            'motivo_cancelacion': forms.Textarea(attrs={'rows': 2}),
        }


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
