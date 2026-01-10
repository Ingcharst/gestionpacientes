"""
Formularios Django para procedimientos.
"""
from django import forms
from apps.procedimientos.models import (
    Paciente, Procedimiento, SesionTerapeutica,
    ObjetivoTerapeutico, ValoracionInicial, EvolucionPaciente
)


class PacienteForm(forms.ModelForm):
    """Formulario para crear/editar pacientes."""
    
    class Meta:
        model = Paciente
        fields = [
            'nombres', 'apellidos', 'tipo_documento', 'numero_documento',
            'fecha_nacimiento', 'genero', 'foto',
            'telefono', 'email', 'direccion', 'ciudad',
            'nombre_responsable', 'parentesco_responsable',
            'telefono_responsable', 'email_responsable',
            'diagnostico_principal', 'alergias', 'medicamentos', 'eps',
            'numero_historia_clinica','numero_admision',
            'fecha_ingreso', 'fecha_alta',
            'observaciones', 'necesidades_especiales',
            'motivo_inactividad'
        ]
        exclude = ['creado_por', 'fecha_creacion', 'fecha_actualizacion', 'estado_asignacion']

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





