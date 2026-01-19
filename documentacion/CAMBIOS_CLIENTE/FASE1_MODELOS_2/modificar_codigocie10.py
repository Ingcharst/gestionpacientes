# MODIFICAR modelo CodigoCIE10 existente en apps/procedimientos/models.py

# Si el modelo NO tiene campo 'nombre', agregar:
"""
    nombre = models.CharField(
        max_length=200,
        blank=True,
        help_text='Nombre descriptivo de la enfermedad'
    )
"""

# Modelo Paciente - agregar FK:
"""
    codigo_enfermedad = models.ForeignKey(
        'CodigoCIE10',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pacientes',
        verbose_name='Código CIE-10'
    )
    
    # Deprecar (agregar null=True, blank=True):
    numero_historia_clinica = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text='[DEPRECADO]'
    )
"""
