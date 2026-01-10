# CORRECCIÓN: AdmisionPacienteForm
# Archivo: apps/procedimientos/forms.py

class AdmisionPacienteForm(forms.ModelForm):
    firma_acudiente_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    
    class Meta:
        model = Paciente
        fields = [
            'nombres', 'apellidos', 'tipo_documento', 'numero_documento',
            'fecha_nacimiento', 'genero', 'foto',
            'telefono', 'email', 'direccion', 'ciudad',
            'nombre_responsable', 'parentesco_responsable',
            'telefono_responsable', 'email_responsable',
            'diagnostico_principal', 'alergias', 'medicamentos', 'eps',
            'numero_admision',  # ← CRÍTICO: DEBE ESTAR AQUÍ
            'observaciones', 'necesidades_especiales',
        ]
        
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'numero_admision': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ADM-20251130-0001'
            }),
            # ... resto de widgets
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            elif not isinstance(field.widget, (forms.CheckboxInput, forms.HiddenInput)):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'
        
        # Sugerir número de admisión
        if not self.instance.pk:
            from django.utils import timezone
            fecha_str = timezone.now().strftime('%Y%m%d')
            ultimo = Paciente.objects.filter(
                numero_admision__startswith=f'ADM-{fecha_str}'
            ).order_by('-numero_admision').first()
            
            if ultimo:
                try:
                    num = int(ultimo.numero_admision.split('-')[-1])
                    siguiente = num + 1
                except:
                    siguiente = 1
            else:
                siguiente = 1
            
            sugerido = f"ADM-{fecha_str}-{siguiente:04d}"
            self.fields['numero_admision'].initial = sugerido
