# ✅ REEMPLAZAR EN: apps/procedimientos/forms.py

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
