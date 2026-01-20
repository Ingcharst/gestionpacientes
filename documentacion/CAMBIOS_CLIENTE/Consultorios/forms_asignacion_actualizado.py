class AsignacionConsultorioForm(forms.ModelForm):
    """Formulario para crear y editar asignaciones."""
    
    class Meta:
        model = AsignacionConsultorio
        fields = [
            'consultorio', 'terapeuta', 'terapia',  # ✅ AGREGADO TERAPIA
            'tipo_asignacion',
            'fecha_inicio', 'fecha_fin', 'horario',
            'dias_semana', 'prioridad', 'notas', 'activo'
        ]
        widgets = {
            'consultorio': forms.Select(attrs={'class': 'form-select'}),
            'terapeuta': forms.Select(attrs={'class': 'form-select'}),
            'terapia': forms.Select(attrs={'class': 'form-select'}),  # ✅ WIDGET TERAPIA
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
        
        # ✅ FILTRAR SOLO TERAPIAS ACTIVAS
        from apps.terapias.models import Terapia
        self.fields['terapia'].queryset = Terapia.objects.filter(activo=True)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            Row(
                Column('consultorio', css_class='col-md-6'),
                Column('terapeuta', css_class='col-md-6'),
            ),
            Row(
                Column('terapia', css_class='col-md-6'),  # ✅ CAMPO TERAPIA
                Column('tipo_asignacion', css_class='col-md-6'),
            ),
            Row(
                Column('fecha_inicio', css_class='col-md-6'),
                Column('fecha_fin', css_class='col-md-6'),
            ),
            Row(
                Column('prioridad', css_class='col-md-6'),
                Column(Field('activo', css_class='form-check-input'), css_class='col-md-6'),
            ),
            'dias_semana',
            'horario',
            'notas',
            Div(
                Submit('submit', 'Guardar', css_class='btn btn-primary'),
                HTML('<a href="{% url "consultorios:asignacion_list" %}" class="btn btn-secondary ms-2">Cancelar</a>'),
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
