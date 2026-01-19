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
            'codigo_enfermedad', 'diagnostico_principal', 'alergias', 'medicamentos', 'eps', 
            'fecha_ingreso', 'fecha_alta',
            'observaciones', 'necesidades_especiales',
            'motivo_inactividad'
        ]
        exclude = ['creado_por', 'fecha_creacion', 'fecha_actualizacion', 'estado_asignacion', 'numero_historia_clinica', 'numero_admision']

        widgets = {
            # Información Personal
            'nombres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombres del paciente'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos del paciente'
            }),
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de documento'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'genero': forms.Select(attrs={
                'class': 'form-select'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            
            # Contacto
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
                'placeholder': 'Dirección completa'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad'
            }),
            
            # Responsable
            'nombre_responsable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del responsable'
            }),
            'parentesco_responsable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Madre, Padre, Tutor'
            }),
            'telefono_responsable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono del responsable'
            }),
            'email_responsable': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            
            # Información Médica
            'codigo_enfermedad': forms.HiddenInput(),  # Campo oculto, se llena con JS
            'diagnostico_principal': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Solo si no está en catálogo CIE-10'
            }),
            'alergias': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Alergias conocidas del paciente'
            }),
            'medicamentos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Medicamentos que toma actualmente'
            }),
            'eps': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'EPS o aseguradora'
            }),
            
            # Fechas
            'fecha_ingreso': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'fecha_alta': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            
            # Observaciones
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones generales del paciente'
            }),
            'necesidades_especiales': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Necesidades especiales o consideraciones'
            }),
            'motivo_inactividad': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Solo llenar si está inactivo o dado de alta'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar valores iniciales para nuevos pacientes
        if not self.instance.pk:
            from django.utils import timezone
            self.fields['fecha_ingreso'].initial = timezone.now().date()
