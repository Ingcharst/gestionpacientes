# ✅ ACTUALIZACIÓN: Función de validación para asignaciones
# Archivo: apps/grupos/views.py
# REEMPLAZAR la función validar_paciente_para_asignacion

from datetime import date
from apps.procedimientos.models import AdmisionTerapia, ValoracionProfesional


def validar_paciente_para_asignacion(paciente, grupo):
    """
    Valida que un paciente cumpla los requisitos para asignarse a un grupo.
    
    ✅ ACTUALIZADO: Usa ValoracionProfesional (múltiples valoraciones)
    
    Requisitos:
    1. Tiene valoración completada para la terapia del grupo
    2. Tiene admisión vigente para la terapia del grupo
    3. No está ya asignado al mismo grupo
    
    Args:
        paciente: Objeto Paciente
        grupo: Objeto GrupoTerapeutico
    
    Returns:
        tuple: (es_valido: bool, mensaje_error: str, admision: AdmisionTerapia|None)
    """
    
    # =========================================================================
    # 1. VERIFICAR VALORACIÓN PARA LA TERAPIA DEL GRUPO
    # =========================================================================
    
    valoracion = ValoracionProfesional.objects.filter(
        paciente=paciente,
        terapia=grupo.terapia,
        estado='COMPLETADA'
    ).first()
    
    if not valoracion:
        return (
            False,
            f'El paciente no tiene valoración completada para {grupo.terapia.nombre}',
            None
        )
    
    # =========================================================================
    # 2. VERIFICAR ADMISIÓN VIGENTE PARA LA TERAPIA
    # =========================================================================
    
    fecha_hoy = date.today()
    admision = AdmisionTerapia.objects.filter(
        paciente=paciente,
        terapia=grupo.terapia,
        estado='VIGENTE',
        fecha_inicio__lte=fecha_hoy,
        fecha_fin__gte=fecha_hoy
    ).first()
    
    if not admision:
        return (
            False,
            f'El paciente no tiene admisión vigente para {grupo.terapia.nombre}',
            None
        )
    
    # =========================================================================
    # 3. VERIFICAR QUE NO ESTÉ YA ASIGNADO AL MISMO GRUPO
    # =========================================================================
    
    from apps.grupos.models import AsignacionGrupo
    
    if AsignacionGrupo.objects.filter(
        paciente=paciente,
        grupo=grupo,
        estado='ACTIVA'
    ).exists():
        return (
            False,
            f'El paciente ya está asignado a {grupo.nombre}',
            None
        )
    
    # ✅ TODO OK
    return True, '', admision


# =============================================================================
# USO EN LAS VISTAS DE ASIGNACIÓN
# =============================================================================

"""
USAR EN:
1. asignar_paciente_grupo
2. agregar_grupo_paciente
3. asignar_desde_recomendacion

EJEMPLO:

@login_required
def asignar_paciente_grupo(request, paciente_id=None, grupo_id=None):
    if request.method == 'POST':
        form = AsignacionGrupoForm(request.POST)
        if form.is_valid():
            paciente = form.cleaned_data['paciente']
            grupo = form.cleaned_data['grupo']
            
            # ✅ VALIDAR PRERREQUISITOS
            es_valido, mensaje_error, admision = validar_paciente_para_asignacion(
                paciente, grupo
            )
            
            if not es_valido:
                messages.error(request, f'❌ {mensaje_error}')
                return render(request, 'grupos/asignacion_form.html', {'form': form})
            
            try:
                # Crear asignación con admisión vinculada
                asignacion = AsignacionGrupo.objects.create(
                    paciente=paciente,
                    grupo=grupo,
                    admision_terapia=admision,  # ✅ Vinculada
                    # ... resto de campos
                )
                # ...
"""


# =============================================================================
# CAMBIOS EN EL FLUJO DE ESTADOS
# =============================================================================

"""
FLUJO ACTUALIZADO:

1. REGISTRO DE PACIENTE
   → Estado: ADMITIDO
   
2. VALORACIONES PROFESIONALES
   → Cada terapeuta crea su ValoracionProfesional
   → Estado de valoración: COMPLETADA
   
3. CAMBIO DE ESTADO DEL PACIENTE
   → Cuando tiene al menos 1 valoración completada
   → Estado: PENDIENTE_ASIGNACION
   
4. ADMISIONES DE TERAPIA
   → Se crean AdmisionTerapia para cada terapia recomendada
   → Estado: VIGENTE
   
5. ASIGNACIÓN A GRUPOS
   → Requiere valoración + admisión para esa terapia
   → Estado paciente: ACTIVO

IMPORTANTE:
- Un paciente puede estar en PENDIENTE_ASIGNACION con algunas valoraciones
- Para asignar a grupo específico, necesita:
  * Valoración completada de ESA terapia
  * Admisión vigente de ESA terapia
"""


# =============================================================================
# ACTUALIZAR CAMBIO DE ESTADO EN ValoracionProfesional
# =============================================================================

"""
En models.py, clase ValoracionProfesional, agregar método save():

def save(self, *args, **kwargs):
    # Detectar cambio a COMPLETADA
    cambio_completada = False
    
    if self.pk:
        try:
            anterior = ValoracionProfesional.objects.get(pk=self.pk)
            cambio_completada = anterior.estado != 'COMPLETADA' and self.estado == 'COMPLETADA'
        except ValoracionProfesional.DoesNotExist:
            cambio_completada = self.estado == 'COMPLETADA'
    else:
        cambio_completada = self.estado == 'COMPLETADA'
    
    # Auto-copiar firma
    if not self.firma_terapeuta and self.terapeuta.firma:
        self.firma_terapeuta = self.terapeuta.firma
    
    super().save(*args, **kwargs)
    
    # Cambiar estado del paciente si es la primera valoración completada
    if cambio_completada:
        from apps.grupos.models import AsignacionGrupo
        
        # Contar valoraciones completadas
        total_completadas = ValoracionProfesional.objects.filter(
            paciente=self.paciente,
            estado='COMPLETADA'
        ).count()
        
        # Si es la primera y no tiene grupo activo
        if total_completadas >= 1:
            tiene_grupo = AsignacionGrupo.objects.filter(
                paciente=self.paciente,
                estado='ACTIVA'
            ).exists()
            
            if not tiene_grupo and self.paciente.estado != 'ACTIVO':
                self.paciente.estado = 'PENDIENTE_ASIGNACION'
                self.paciente.save(update_fields=['estado'])
"""
