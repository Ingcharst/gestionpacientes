"""
Formularios para gestión de grupos terapéuticos.
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import GrupoTerapeutico, AsignacionGrupo, PacientePendiente
from apps.procedimientos.models import Paciente


class GrupoTerapeuticoForm(forms.ModelForm):
    """Formulario para crear/editar grupos terapéuticos"""
    
    # Días de la semana como checkboxes
    dias_disponibles = forms.MultipleChoiceField(
        choices=GrupoTerapeutico.DIAS_SEMANA,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Días Disponibles'
    )
    
    class Meta:
        model = GrupoTerapeutico
        fields = [
            'nombre',
            'descripcion',
            'hora_inicio',
            'hora_fin',
            'dias_disponibles',
            'capacidad_maxima',
            'activo',
            'notas',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Grupo 9:00 a.m.'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del grupo'
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'capacidad_maxima': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 50
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }


class AsignacionGrupoForm(forms.ModelForm):
    """Formulario para asignar paciente a grupo"""
    
    fields = ['paciente', 'grupo', 'numero_terapias_asignadas', 'dias_asistencia']
    
    paciente = forms.ModelChoiceField(
        # queryset=Paciente.objects.filter(estado__in=['ACTIVO','ADMITIDO', 'PENDIENTE_ASIGNACION'], tiene_grupo_asignado=False),
        queryset=Paciente.objects.filter(estado__in=['ACTIVO','ADMITIDO', 'PENDIENTE_ASIGNACION']),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Paciente'
    )
    
    grupo = forms.ModelChoiceField(
        queryset=GrupoTerapeutico.objects.filter(activo=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Grupo Terapéutico'
    )
    
    dias_asistencia = forms.MultipleChoiceField(
        choices=GrupoTerapeutico.DIAS_SEMANA,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Días de Asistencia'
    )
    
    class Meta:
        model = AsignacionGrupo
        fields = [
            'paciente',
            'grupo',
            'dias_asistencia',
            'numero_terapias_semanales',
            'numero_terapias_asignadas',
            'fecha_inicio_asignacion',
            'notas',
        ]
        widgets = {
            'numero_terapias_semanales': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 7
            }),
            'fecha_inicio_asignacion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        grupo = cleaned_data.get('grupo')
        dias_asistencia = cleaned_data.get('dias_asistencia')
        
        if grupo and dias_asistencia:
            # Verificar que los días estén disponibles en el grupo
            if not grupo.puede_asignar_dias(dias_asistencia):
                raise ValidationError({
                    'dias_asistencia': f'Los días seleccionados no están disponibles en el grupo. Días del grupo: {grupo.dias_disponibles}'
                })
            
            # Verificar cupo
            if not grupo.tiene_cupo:
                raise ValidationError({
                    'grupo': f'El grupo está lleno (capacidad: {grupo.capacidad_maxima})'
                })
        
        return cleaned_data


class PacientePendienteForm(forms.ModelForm):
    """Formulario para marcar paciente como pendiente"""
    
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.filter(
            estado='ACTIVO',
            tiene_grupo_asignado=False
        ),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Paciente'
    )
    
    dias_preferidos = forms.MultipleChoiceField(
        choices=GrupoTerapeutico.DIAS_SEMANA,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Días Preferidos'
    )
    
    class Meta:
        model = PacientePendiente
        fields = [
            'paciente',
            'preferencia_horario',
            'dias_preferidos',
            'prioridad',
            'observaciones',
        ]
        widgets = {
            'preferencia_horario': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }


class BuscarGrupoForm(forms.Form):
    """Formulario para buscar grupos disponibles"""
    
    dias_requeridos = forms.MultipleChoiceField(
        choices=GrupoTerapeutico.DIAS_SEMANA,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Días Requeridos'
    )
    
    hora_preferida = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        }),
        label='Hora Preferida (opcional)'
    )
    
    capacidad_minima = forms.IntegerField(
        initial=1,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1
        }),
        label='Cupos Mínimos Requeridos'
    )

class CambioCupoGrupoForm(forms.Form):
    """Formulario para cambiar cupo máximo"""
    capacidad_maxima = forms.IntegerField(
        label='Nueva Capacidad Máxima',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 10'
        })
    )
    observaciones = forms.CharField(
        label='Observaciones',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Motivo del cambio (opcional)'
        })
    )




