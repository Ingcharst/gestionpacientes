from django import forms
from apps.procedimientos.models import (
    Paciente, Procedimiento, SesionTerapeutica,
    ObjetivoTerapeutico, ValoracionInicial, EvolucionPaciente, 
    Paciente, ValoracionProfesional, AdmisionTerapia, CodigoCIE10
)
from apps.terapias.models import Terapia
from django.utils import timezone
from datetime import timedelta

class PacienteForm(forms.ModelForm):
    """Formulario para crear/editar pacientes."""

    diagnostico_cie10_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar código CIE-10 (ej: F84.0 o Autismo)',
            'autocomplete': 'off'
        }),
        label='Buscar Diagnóstico CIE-10'
    )

    class Meta:
        model = Paciente
        fields = [
            'nombres', 'apellidos', 'tipo_documento', 'numero_documento',
            'fecha_nacimiento', 'genero', 'foto',
            'telefono', 'email', 'direccion', 'ciudad',
            'nombre_responsable', 'parentesco_responsable',
            'telefono_responsable', 'email_responsable',
            'codigo_enfermedad','diagnostico_principal', 'alergias', 'medicamentos', 'eps', 
            'fecha_ingreso', 'fecha_alta',
            'observaciones', 'necesidades_especiales',
            'motivo_inactividad'
        ]
        exclude = ['creado_por', 'fecha_creacion', 'fecha_actualizacion', 'estado_asignacion','numero_historia_clinica','numero_admision']

        widgets = {
            'codigo_enfermedad': forms.HiddenInput(),  # Campo oculto, se llena con JS
            'diagnostico_principal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Solo si no está en catálogo (ej: Z99.9)'
            }),         'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
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
        
        # Configurar valores iniciales para nuevos pacientes
        if not self.instance.pk:
            from django.utils import timezone
            self.fields['fecha_ingreso'].initial = timezone.now().date()
            # IMPORTANTE: Agregar valor inicial para estado_asignacion
            if 'estado_asignacion' in self.fields:
                self.fields['estado_asignacion'].initial = 'SIN_ASIGNAR'  # o el valor por defecto que uses


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
            'numero_admision': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0001'
            }),            
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
            
            sugerido = f"{siguiente_num:04d}"
            self.fields['numero_admision'].initial = sugerido
            self.fields['numero_admision'].help_text = f'Sugerido: {sugerido}'
        
        # Hacer numero_historia_clinica opcional (se genera automáticamente)
        if 'numero_historia_clinica' in self.fields:
            self.fields['numero_historia_clinica'].required = False
    
    def clean_numero_admision(self):
        """Validar formato del número de admisión."""
        numero = self.cleaned_data.get('numero_admision')
        
        # Validar formato ADM-YYYYMMDD-####
        # import re
        # if not re.match(r'^ADM-\d{8}-\d{4}$', numero):
        #     raise forms.ValidationError(
        #         'El formato debe ser: ADM-YYYYMMDD-#### (Ej: ADM-20251124-0001)'
        #     )
        
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


class ValoracionInicialForm(forms.ModelForm):
    """
    Formulario para registro de valoración inicial del paciente.
    """
    diagnostico_cie10_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar código CIE-10 (ej: F84.0 o Autismo)',
            'autocomplete': 'off'
        }),
        label='Buscar Diagnóstico CIE-10'
    )
        
    class Meta:
        model = ValoracionInicial
        fields = [
            'fecha_valoracion',
            'hora_inicio',
            'hora_fin',
            'motivo_consulta',
            'antecedentes_personales',
            'antecedentes_familiares',
            'desarrollo_evolutivo',
            'evaluacion_lenguaje',
            'evaluacion_motora',
            'evaluacion_cognitiva',
            'evaluacion_conductual',
            'evaluacion_social',
            'observaciones_generales',
            'nivel_funcionalidad',
            'diagnostico_profesional',
            'diagnostico_cie10',  # FK a CodigoCIE10
            'diagnostico_cie10_texto',  # TextField manual
            'terapias_recomendadas',
            'numero_sesiones_recomendado',
            'frecuencia_recomendada',
            'duracion_estimada_tratamiento',
            'observaciones_recomendaciones',
            'requiere_interconsulta',
            'especialidades_interconsulta',
            'completada',
        ]
         
        widgets = {
            'diagnostico_cie10': forms.HiddenInput(),  # Campo oculto, se llena con JS
            'diagnostico_cie10_texto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Solo si no está en catálogo (ej: Z99.9)'
            }),
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

        # Reordenar campos para mostrar búsqueda primero
        field_order = list(self.fields.keys())
        if 'diagnostico_cie10_search' in field_order:
            field_order.remove('diagnostico_cie10_search')
            # Insertar después de diagnostico_profesional
            idx = field_order.index('diagnostico_profesional') + 1
            field_order.insert(idx, 'diagnostico_cie10_search')
            self.order_fields(field_order)

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


class PacienteRegistroForm(forms.ModelForm):
    """
    Formulario de registro de paciente completo
    Incluye TODOS los campos del template
    """
    
    # ✅ Campo extra para búsqueda CIE-10
    diagnostico_cie10_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar código CIE-10 (ej: F84.0 o Autismo)',
            'autocomplete': 'off'
        }),
        label='Buscar Diagnóstico CIE-10'
    )
    
    class Meta:
        model = Paciente
        fields = [
            # Información Personal
            'tipo_documento',
            'numero_documento',
            'nombres',
            'apellidos',
            'fecha_nacimiento',
            'genero',
            'foto',
            # Información de Contacto
            'telefono',
            'email',
            'direccion',
            'ciudad',  # ✅ AGREGADO
            # Acudiente/Responsable
            'nombre_responsable',
            'telefono_responsable',
            'parentesco_responsable',
            'email_responsable',
            # Información Médica
            'codigo_enfermedad',
            'diagnostico_principal',  # ✅ AGREGADO
            'alergias',  # ✅ AGREGADO
            'medicamentos',  # ✅ AGREGADO
            'eps',  # ✅ AGREGADO
            # Fechas
            'fecha_ingreso',  # ✅ AGREGADO
            'fecha_alta',  # ✅ AGREGADO
            'motivo_inactividad',  # ✅ AGREGADO
            # Observaciones
            'observaciones',  # ✅ AGREGADO
            'necesidades_especiales',  # ✅ AGREGADO
        ]
        
        widgets = {
            # Información Personal
            'tipo_documento': forms.Select(attrs={
                'class': 'form-control'
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de documento'
            }),
            'nombres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombres del paciente'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos del paciente'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'genero': forms.Select(attrs={
                'class': 'form-control'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            
            # Información de Contacto
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Dirección de residencia'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad'
            }),
            
            # Acudiente/Responsable
            'nombre_responsable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del acudiente'
            }),
            'telefono_responsable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono del acudiente'
            }),
            'parentesco_responsable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Padre, Madre, Tutor, etc.'
            }),
            'email_responsable': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email del acudiente'
            }),
            
            # ✅ Información Médica
            'codigo_enfermedad': forms.HiddenInput(),  # Campo oculto para ID CIE-10
            'diagnostico_principal': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Solo si no está en el catálogo CIE-10'
            }),
            'alergias': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Alergias conocidas'
            }),
            'medicamentos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Medicamentos actuales'
            }),
            'eps': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'EPS del paciente'
            }),
            
            # ✅ Fechas
            'fecha_ingreso': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'fecha_alta': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'motivo_inactividad': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Solo si está inactivo'
            }),
            
            # ✅ Observaciones
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones generales'
            }),
            'necesidades_especiales': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Necesidades especiales o consideraciones'
            }),
        }
        
        labels = {
            'tipo_documento': 'Tipo de Documento',
            'numero_documento': 'Número de Documento',
            'nombres': 'Nombres',
            'apellidos': 'Apellidos',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'genero': 'Género',
            'foto': 'Fotografía',
            'telefono': 'Teléfono',
            'email': 'Correo Electrónico',
            'direccion': 'Dirección',
            'ciudad': 'Ciudad',
            'nombre_responsable': 'Nombre del Acudiente',
            'telefono_responsable': 'Teléfono del Acudiente',
            'parentesco_responsable': 'Parentesco',
            'email_responsable': 'Email del Acudiente',
            'codigo_enfermedad': 'Código CIE-10',
            'diagnostico_principal': 'Diagnóstico Principal',
            'alergias': 'Alergias',
            'medicamentos': 'Medicamentos Actuales',
            'eps': 'EPS',
            'fecha_ingreso': 'Fecha de Ingreso',
            'fecha_alta': 'Fecha de Alta',
            'motivo_inactividad': 'Motivo de Inactividad',
            'observaciones': 'Observaciones Generales',
            'necesidades_especiales': 'Necesidades Especiales',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # ✅ Configurar queryset para código CIE-10
        self.fields['codigo_enfermedad'].queryset = CodigoCIE10.objects.filter(
            activo=True
        ).order_by('codigo')
        
        # ✅ Campos opcionales
        self.fields['codigo_enfermedad'].required = False
        self.fields['diagnostico_principal'].required = False
        self.fields['alergias'].required = False
        self.fields['medicamentos'].required = False
        self.fields['eps'].required = False
        self.fields['fecha_alta'].required = False
        self.fields['motivo_inactividad'].required = False
        self.fields['observaciones'].required = False
        self.fields['necesidades_especiales'].required = False
        self.fields['email'].required = False
        self.fields['email_responsable'].required = False
        self.fields['foto'].required = False
        self.fields['ciudad'].required = False
        
        # ✅ Valor inicial fecha ingreso
        if not self.instance.pk:
            self.fields['fecha_ingreso'].initial = timezone.now().date()
    
    def clean_numero_documento(self):
        """Validar que el documento no exista"""
        numero = self.cleaned_data.get('numero_documento')
        if numero:
            if self.instance.pk:
                existe = Paciente.objects.filter(
                    numero_documento=numero
                ).exclude(pk=self.instance.pk).exists()
            else:
                existe = Paciente.objects.filter(
                    numero_documento=numero
                ).exists()
            
            if existe:
                raise forms.ValidationError(
                    'Ya existe un paciente con este número de documento.'
                )
        return numero


class ValoracionProfesionalForm(forms.ModelForm):
    """
    Formulario de valoración profesional
    ACTUALIZADO: Incluye código CIE-10
    """
    
    class Meta:
        model = ValoracionProfesional
        fields = [
            'terapia',
            'codigo_cie10',  # ✅ Campo CIE-10
            'estado_salud_general',
            'observaciones',
            'recomendaciones',
            'objetivos_terapeuticos',
        ]
        
        widgets = {
            'terapia': forms.Select(attrs={
                'class': 'form-control'
            }),
            # ✅ WIDGET PARA CIE-10
            'codigo_cie10': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Seleccione código CIE-10'
            }),
            'estado_salud_general': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describa el estado de salud general del paciente...'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observaciones relevantes de la valoración...'
            }),
            'recomendaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Recomendaciones terapéuticas...'
            }),
            'objetivos_terapeuticos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Objetivos específicos para esta terapia...'
            }),
        }
        
        labels = {
            'terapia': 'Tipo de Terapia',
            'codigo_cie10': 'Código CIE-10 (Diagnóstico)',
            'estado_salud_general': 'Estado de Salud General',
            'observaciones': 'Observaciones',
            'recomendaciones': 'Recomendaciones',
            'objetivos_terapeuticos': 'Objetivos Terapéuticos',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # ✅ Configurar queryset para código CIE-10
        self.fields['codigo_cie10'].queryset = CodigoCIE10.objects.filter(
            activo=True
        ).order_by('codigo')
        
        # ✅ Código CIE-10 opcional (puede no tener diagnóstico definitivo)
        self.fields['codigo_cie10'].required = False
        
        # Objetivos opcionales
        self.fields['objetivos_terapeuticos'].required = False




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






