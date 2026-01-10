# MODIFICAR FORMULARIO DE VALORACIÓN
# Archivo: apps/procedimientos/forms.py

# BUSCAR la clase ValoracionInicialForm
# AGREGAR estos campos:

class ValoracionInicialForm(forms.ModelForm):
    # Campo de búsqueda (no se guarda en BD)
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
            # ... resto de widgets existentes ...
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
