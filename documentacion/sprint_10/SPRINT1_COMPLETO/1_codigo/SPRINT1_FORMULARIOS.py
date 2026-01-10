# ============================================================================
# SPRINT 1 - FORMULARIOS
# apps/procedimientos/forms.py
# ============================================================================

"""
INSTRUCCIONES:
Agregar estos formularios al final de apps/procedimientos/forms.py
"""

from django import forms
from apps.procedimientos.models import Paciente, ValoracionInicial


# ============================================================================
# FORMULARIO DE ADMISIÓN DE PACIENTE
# ============================================================================

class AdmisionPacienteForm(forms.ModelForm):
    """
    Formulario para admisión de nuevos pacientes.
    Incluye captura de firma digital del acudiente.
    """
    
    # Campo oculto para la firma digital (se captura con JavaScript)
    firma_acudiente_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        label='Firma Digital'
    )
    
    class Meta:
        model = Paciente
        fields = [
            # Información Personal
            'nombres', 'apellidos', 'tipo_documento', 'numero_documento',
            'fecha_nacimiento', 'genero', 'foto',
            
            # Contacto
            'telefono', 'email', 'direccion', 'ciudad',
            
            # Responsable/Acudiente
            'nombre_responsable', 'parentesco_responsable',
            'telefono_responsable', 'email_responsable',
            
            # Información Médica Básica
            'diagnostico_principal', 'alergias', 'medicamentos', 'eps',
            
            # NUEVO: Número de Admisión
            'numero_admision',
            
            # Observaciones
            'observaciones', 'necesidades_especiales',
        ]
        
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'necesidades_especiales': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'diagnostico_principal': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'alergias': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'medicamentos': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Agregar clases CSS a todos los campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs['class'] = 'form-select'
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control'
            elif not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.HiddenInput)):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'
        
        # Configurar valores iniciales
        if not self.instance.pk:
            from django.utils import timezone
            self.fields['fecha_nacimiento'].initial = None
            
            # Generar sugerencia de número de admisión
            # Formato: ADM-YYYYMMDD-#### (automático)
            fecha_str = timezone.now().strftime('%Y%m%d')
            ultimo_paciente = Paciente.objects.filter(
                numero_admision__startswith=f'ADM-{fecha_str}'
            ).order_by('-numero_admision').first()
            
            if ultimo_paciente:
                # Extraer último número y sumar 1
                try:
                    ultimo_num = int(ultimo_paciente.numero_admision.split('-')[-1])
                    siguiente_num = ultimo_num + 1
                except:
                    siguiente_num = 1
            else:
                siguiente_num = 1
            
            sugerido = f"ADM-{fecha_str}-{siguiente_num:04d}"
            self.fields['numero_admision'].initial = sugerido
            self.fields['numero_admision'].help_text = f'Sugerido: {sugerido}'
        
        # Hacer numero_historia_clinica opcional (se genera automáticamente)
        if 'numero_historia_clinica' in self.fields:
            self.fields['numero_historia_clinica'].required = False
    
    def clean_numero_admision(self):
        """Validar formato del número de admisión."""
        numero = self.cleaned_data.get('numero_admision')
        
        # Validar formato ADM-YYYYMMDD-####
        import re
        if not re.match(r'^ADM-\d{8}-\d{4}$', numero):
            raise forms.ValidationError(
                'El formato debe ser: ADM-YYYYMMDD-#### (Ej: ADM-20251124-0001)'
            )
        
        return numero
    
    def save(self, commit=True):
        """Guardar paciente con firma digital."""
        paciente = super().save(commit=False)
        
        # Establecer estado inicial
        paciente.estado = Paciente.Estado.ADMITIDO
        
        # Guardar firma si existe
        firma_data = self.cleaned_data.get('firma_acudiente_data')
        if firma_data:
            from django.utils import timezone
            paciente.firma_acudiente = firma_data
            paciente.fecha_firma_acudiente = timezone.now()
            
            # Capturar IP si está disponible en el request (se debe pasar desde la vista)
            if hasattr(self, 'request'):
                x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    paciente.ip_firma = x_forwarded_for.split(',')[0]
                else:
                    paciente.ip_firma = self.request.META.get('REMOTE_ADDR')
        
        if commit:
            paciente.save()
            self.save_m2m()
        
        return paciente


# ============================================================================
# FORMULARIO DE VALORACIÓN INICIAL
# ============================================================================

class ValoracionInicialForm(forms.ModelForm):
    """
    Formulario para registro de valoración inicial del paciente.
    """
    
    class Meta:
        model = ValoracionInicial
        fields = [
            # Información General
            'fecha_valoracion', 'hora_inicio', 'hora_fin',
            
            # Motivo y Antecedentes
            'motivo_consulta', 'antecedentes_personales', 
            'antecedentes_familiares', 'desarrollo_evolutivo',
            
            # Evaluación
            'observaciones_generales',
            
            # Evaluaciones por Área
            'evaluacion_lenguaje', 'evaluacion_motora', 
            'evaluacion_cognitiva', 'evaluacion_conductual', 
            'evaluacion_social',
            
            # Nivel de funcionalidad
            'nivel_funcionalidad',
            
            # Diagnóstico
            'diagnostico_profesional', 'diagnostico_cie10',
            
            # Recomendaciones
            'terapias_recomendadas', 'numero_sesiones_recomendado',
            'frecuencia_recomendada', 'duracion_estimada_tratamiento',
            'observaciones_recomendaciones',
            
            # Interconsulta
            'requiere_interconsulta', 'especialidades_interconsulta',
            
            # Estado
            'completada',
        ]
        
        widgets = {
            'fecha_valoracion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            
            'motivo_consulta': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'antecedentes_personales': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'antecedentes_familiares': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'desarrollo_evolutivo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            
            'observaciones_generales': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            
            'evaluacion_lenguaje': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'evaluacion_motora': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'evaluacion_cognitiva': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'evaluacion_conductual': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'evaluacion_social': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            
            'diagnostico_profesional': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'observaciones_recomendaciones': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'especialidades_interconsulta': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            
            'terapias_recomendadas': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Agregar clases CSS
        for field_name, field in self.fields.items():
            if field_name == 'terapias_recomendadas':
                continue  # Checkbox múltiple maneja su propio estilo
            
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs['class'] = 'form-select'
            elif not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'
        
        # Valores iniciales
        if not self.instance.pk:
            from django.utils import timezone
            self.fields['fecha_valoracion'].initial = timezone.now().date()
            self.fields['completada'].initial = False


# ============================================================================
# FORMULARIO PARA AGREGAR PROBLEMAS DETECTADOS (Dinámico con JavaScript)
# ============================================================================

class ProblemaDetectadoForm(forms.Form):
    """
    Formulario para agregar problemas detectados durante la valoración.
    Se usa de forma dinámica con JavaScript.
    """
    
    SEVERIDAD_CHOICES = [
        ('LEVE', 'Leve'),
        ('MODERADA', 'Moderada'),
        ('SEVERA', 'Severa'),
    ]
    
    tipo = forms.ChoiceField(
        choices=ValoracionInicial.TipoProblema.choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo de Problema'
    )
    
    descripcion = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        label='Descripción del Problema'
    )
    
    severidad = forms.ChoiceField(
        choices=SEVERIDAD_CHOICES,
        initial='MODERADA',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Severidad'
    )
    
    observaciones = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        label='Observaciones Adicionales'
    )


# ============================================================================
# FIN DE FORMULARIOS SPRINT 1
# ============================================================================
