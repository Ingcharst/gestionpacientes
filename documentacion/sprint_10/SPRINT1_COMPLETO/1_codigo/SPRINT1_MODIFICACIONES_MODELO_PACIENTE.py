# ============================================================================
# SPRINT 1 - MODIFICACIONES AL MODELO PACIENTE
# apps/procedimientos/models.py
# ============================================================================

"""
INSTRUCCIONES:
1. Buscar la clase Paciente en apps/procedimientos/models.py (línea ~13)
2. Reemplazar la clase Estado con la nueva versión
3. Agregar los nuevos campos después de numero_historia_clinica
"""

# ============================================================================
# PASO 1: REEMPLAZAR LA CLASE Estado (línea ~26)
# ============================================================================

class Estado(models.TextChoices):
    # NUEVOS ESTADOS PARA EL FLUJO
    ADMITIDO = 'ADMITIDO', _('Admitido - Sin Valorar')
    PENDIENTE_VALORACION = 'PENDIENTE_VALORACION', _('Pendiente Valoración')
    PENDIENTE_ASIGNACION = 'PENDIENTE_ASIGNACION', _('Pendiente Asignación Terapias')
    
    # ESTADOS EXISTENTES
    ACTIVO = 'ACTIVO', _('Activo en Tratamiento')
    INACTIVO = 'INACTIVO', _('Inactivo')
    SUSPENDIDO = 'SUSPENDIDO', _('Suspendido')
    DADO_ALTA = 'DADO_ALTA', _('Dado de Alta')


# ============================================================================
# PASO 2: AGREGAR NUEVOS CAMPOS AL MODELO PACIENTE
# Agregar DESPUÉS del campo numero_historia_clinica (línea ~166)
# ============================================================================

# ✅ NUEVO: Número de admisión (reemplaza HC como identificador principal)
numero_admision = models.CharField(
    max_length=50,
    unique=True,
    verbose_name='Número de Admisión',
    help_text='Número de admisión del paciente (ingresado manualmente)'
)

# ✅ MODIFICADO: Historia clínica ahora es opcional y se genera automáticamente
# El campo numero_historia_clinica ya existe, solo cambiar sus atributos:
# blank=True (ya existe en línea 162)
# editable=True (ya existe en línea 163)

# ✅ NUEVO: Firma digital del acudiente en admisión
firma_acudiente = models.TextField(
    blank=True,
    verbose_name='Firma Digital Acudiente',
    help_text='Firma del acudiente en formato base64 capturada con periférico'
)

fecha_firma_acudiente = models.DateTimeField(
    null=True,
    blank=True,
    verbose_name='Fecha y Hora de Firma'
)

ip_firma = models.GenericIPAddressField(
    null=True,
    blank=True,
    verbose_name='IP donde se firmó'
)


# ============================================================================
# PASO 3: MODIFICAR EL VALOR POR DEFECTO DEL ESTADO (línea ~184)
# ============================================================================

# CAMBIAR DE:
estado = models.CharField(
    max_length=20,
    choices=Estado.choices,
    default=Estado.ACTIVO,  # ❌ CAMBIAR ESTO
    verbose_name='Estado'
)

# A:
estado = models.CharField(
    max_length=30,  # ✅ Aumentar tamaño por nuevos estados
    choices=Estado.choices,
    default=Estado.ADMITIDO,  # ✅ NUEVO VALOR POR DEFECTO
    verbose_name='Estado'
)


# ============================================================================
# PASO 4: MODIFICAR EL MÉTODO generar_numero_historia_clinica (línea ~250 aprox)
# ============================================================================

# BUSCAR el método:
def generar_numero_historia_clinica(self):
    """
    Genera número de historia clínica automático.
    Formato: HC-{documento}-{año}
    """
    anio = timezone.now().year
    return f"HC-{self.numero_documento}-{anio}"

# REEMPLAZAR CON:
def generar_numero_historia_clinica(self):
    """
    Genera número de historia clínica automático.
    Formato: HC-{numero_admision}-{año}
    """
    anio = timezone.now().year
    # Usar número de admisión si está disponible, sino documento
    identificador = self.numero_admision if hasattr(self, 'numero_admision') and self.numero_admision else self.numero_documento
    return f"HC-{identificador}-{anio}"


# ============================================================================
# RESUMEN DE CAMBIOS:
# ============================================================================
# 1. ✅ Nuevos estados: ADMITIDO, PENDIENTE_VALORACION, PENDIENTE_ASIGNACION
# 2. ✅ Campo numero_admision (obligatorio, único)
# 3. ✅ Campo firma_acudiente (firma digital base64)
# 4. ✅ Campo fecha_firma_acudiente
# 5. ✅ Campo ip_firma
# 6. ✅ Estado por defecto cambiado a ADMITIDO
# 7. ✅ Método generar_numero_historia_clinica modificado
