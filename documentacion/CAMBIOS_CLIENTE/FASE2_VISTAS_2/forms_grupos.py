# AGREGAR A: apps/grupos/forms.py

from django import forms
from .models import GrupoTerapeutico


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
