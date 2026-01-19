# ACTUALIZAR EN: apps/procedimientos/forms.py

from django import forms
from .models import Paciente, ValoracionProfesional, CodigoCIE10
from apps.terapias.models import Terapia


class PacienteRegistroForm(forms.ModelForm):
    """
    Formulario de registro de paciente
    ACTUALIZADO: Incluye código CIE-10
    """
    
    class Meta:
        model = Paciente
        fields = [
            'tipo_documento',
            'numero_documento',
            'nombres',
            'apellidos',
            'fecha_nacimiento',
            'genero',
            'foto',
            'telefono',
            'email',
            'direccion',
            'acudiente_nombre',
            'acudiente_telefono',
            'acudiente_parentesco',
            'codigo_enfermedad',  # ✅ Campo CIE-10
        ]
        
        widgets = {
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
            'acudiente_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del acudiente'
            }),
            'acudiente_telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono del acudiente'
            }),
            'acudiente_parentesco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Padre, Madre, Tutor, etc.'
            }),
            # ✅ WIDGET PARA CIE-10
            'codigo_enfermedad': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Seleccione código CIE-10'
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
            'acudiente_nombre': 'Nombre del Acudiente',
            'acudiente_telefono': 'Teléfono del Acudiente',
            'acudiente_parentesco': 'Parentesco',
            'codigo_enfermedad': 'Código CIE-10 (Diagnóstico)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # ✅ Configurar queryset para código CIE-10
        # Mostrar solo códigos activos, ordenados por código
        self.fields['codigo_enfermedad'].queryset = CodigoCIE10.objects.filter(
            activo=True
        ).order_by('codigo')
        
        # ✅ Hacer código CIE-10 opcional
        self.fields['codigo_enfermedad'].required = False
        
        # Email opcional
        self.fields['email'].required = False
        
        # Foto opcional
        self.fields['foto'].required = False
    
    def clean_numero_documento(self):
        """Validar que el documento no exista"""
        numero = self.cleaned_data.get('numero_documento')
        if numero:
            # Si está editando, excluir el paciente actual
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
