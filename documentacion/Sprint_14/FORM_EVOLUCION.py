# FORMULARIO: EVOLUCIÓN DE PACIENTE
# Archivo: apps/procedimientos/forms.py
# AGREGAR esta clase

from django import forms
from .models import EvolucionPaciente

class EvolucionPacienteForm(forms.ModelForm):
    """Formulario para registrar evolución de paciente"""
    
    class Meta:
        model = EvolucionPaciente
        fields = [
            'paciente',
            'terapia',
            'grupo',
            'fecha_sesion',
            'hora_inicio',
            'hora_fin',
            'tipo_sesion',
            'asistio',
            'objetivos_trabajados',
            'actividades_realizadas',
            'desempeno',
            'logros_obtenidos',
            'dificultades_observadas',
            'observaciones_conducta',
            'observaciones_generales',
            'nivel_atencion',
            'nivel_participacion',
            'nivel_colaboracion',
            'nivel_comprension',
            'material_utilizado',
            'tarea_asignada',
            'recomendaciones',
            'proximos_objetivos',
            'firmado',
        ]
        
        widgets = {
            'paciente': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'terapia': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'grupo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_sesion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'required': True
            }),
            'hora_fin': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'required': True
            }),
            'tipo_sesion': forms.Select(attrs={
                'class': 'form-select'
            }),
            'asistio': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'objetivos_trabajados': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describa los objetivos terapéuticos trabajados en esta sesión...',
                'required': True
            }),
            'actividades_realizadas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Detalle las actividades y ejercicios realizados...',
                'required': True
            }),
            'desempeno': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'logros_obtenidos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa los avances y logros observados...'
            }),
            'dificultades_observadas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa las dificultades encontradas...'
            }),
            'observaciones_conducta': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones sobre el comportamiento del paciente...'
            }),
            'observaciones_generales': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Otras observaciones relevantes...'
            }),
            'nivel_atencion': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nivel_participacion': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nivel_colaboracion': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nivel_comprension': forms.Select(attrs={
                'class': 'form-select'
            }),
            'material_utilizado': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Material didáctico utilizado...'
            }),
            'tarea_asignada': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tareas o ejercicios para realizar en casa...'
            }),
            'recomendaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Recomendaciones para próximas sesiones o para el hogar...'
            }),
            'proximos_objetivos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Objetivos a trabajar en próximas sesiones...'
            }),
            'firmado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
        labels = {
            'asistio': 'El paciente asistió a la sesión',
            'firmado': 'Finalizar y firmar evolución (no se podrá editar)',
        }
    
    def __init__(self, *args, **kwargs):
        # Capturar parámetros adicionales
        profesional = kwargs.pop('profesional', None)
        paciente_id = kwargs.pop('paciente_id', None)
        grupo_id = kwargs.pop('grupo_id', None)
        
        super().__init__(*args, **kwargs)
        
        # Configurar valores iniciales
        if paciente_id:
            self.fields['paciente'].initial = paciente_id
            # Filtrar grupos del paciente
            from apps.grupos.models import AsignacionGrupo
            grupos_paciente = AsignacionGrupo.objects.filter(
                paciente_id=paciente_id,
                estado='ACTIVA'
            ).values_list('grupo_id', flat=True)
            self.fields['grupo'].queryset = self.fields['grupo'].queryset.filter(
                id__in=grupos_paciente
            )
        
        if grupo_id:
            self.fields['grupo'].initial = grupo_id
            # Establecer terapia del grupo
            from apps.grupos.models import GrupoTerapeutico
            try:
                grupo = GrupoTerapeutico.objects.get(id=grupo_id)
                self.fields['terapia'].initial = grupo.terapia_id
            except:
                pass
        
        # Valores por defecto
        if not self.instance.pk:
            from django.utils import timezone
            self.fields['fecha_sesion'].initial = timezone.now().date()
            self.fields['asistio'].initial = True
    
    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        
        # Validar que hora fin sea mayor que hora inicio
        if hora_inicio and hora_fin:
            if hora_fin <= hora_inicio:
                raise forms.ValidationError(
                    'La hora de fin debe ser posterior a la hora de inicio'
                )
        
        # Si no asistió, marcar como opcional algunos campos
        asistio = cleaned_data.get('asistio')
        if not asistio:
            # Limpiar campos no obligatorios si no asistió
            cleaned_data['objetivos_trabajados'] = cleaned_data.get('objetivos_trabajados', 'No asistió a la sesión')
            cleaned_data['actividades_realizadas'] = cleaned_data.get('actividades_realizadas', 'No asistió a la sesión')
            cleaned_data['desempeno'] = 'NO_PARTICIPO'
        
        return cleaned_data
