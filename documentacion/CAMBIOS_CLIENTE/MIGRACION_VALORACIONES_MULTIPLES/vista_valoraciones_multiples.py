# ✅ VISTA CORREGIDA: pacientes_pendientes_asignacion
# Archivo: apps/procedimientos/views.py
# Reemplazar función completa (línea ~574)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Exists, OuterRef
from datetime import date

from .models import Paciente, ValoracionProfesional, AdmisionTerapia
from apps.grupos.models import AsignacionGrupo


@login_required
def pacientes_pendientes_asignacion(request):
    """
    Lista de pacientes que han sido valorados por profesionales
    y están pendientes de asignación a grupos terapéuticos.
    
    ✅ ACTUALIZADO: Usa ValoracionProfesional (múltiples valoraciones)
    """
    
    # =========================================================================
    # 1. BUSCAR PACIENTES CON VALORACIONES COMPLETADAS
    # =========================================================================
    
    # Subquery para verificar si tiene valoraciones completadas
    tiene_valoraciones = ValoracionProfesional.objects.filter(
        paciente=OuterRef('pk'),
        estado='COMPLETADA'
    )
    
    # Pacientes con al menos una valoración completada
    pacientes_con_valoraciones = Paciente.objects.annotate(
        tiene_valoraciones_completadas=Exists(tiene_valoraciones),
        total_valoraciones=Count(
            'valoraciones_profesionales',
            filter=Q(valoraciones_profesionales__estado='COMPLETADA')
        )
    ).filter(
        tiene_valoraciones_completadas=True
    )
    
    # =========================================================================
    # 2. FILTRAR POR ESTADO Y SIN ASIGNACIÓN ACTIVA
    # =========================================================================
    
    # Opción A: Filtrar por estado PENDIENTE_ASIGNACION
    pacientes = pacientes_con_valoraciones.filter(
        estado=Paciente.Estado.PENDIENTE_ASIGNACION
    )
    
    # Opción B (alternativa): Todos con valoración pero sin grupo activo
    # pacientes = pacientes_con_valoraciones.exclude(
    #     id__in=AsignacionGrupo.objects.filter(
    #         estado='ACTIVA'
    #     ).values_list('paciente_id', flat=True)
    # )
    
    pacientes = pacientes.select_related(
        'codigo_enfermedad'
    ).prefetch_related(
        'valoraciones_profesionales__terapia',
        'valoraciones_profesionales__terapeuta',
        'admisiones'
    ).order_by('-fecha_ingreso')
    
    # =========================================================================
    # 3. CONSTRUIR DATOS PARA CADA PACIENTE
    # =========================================================================
    
    pacientes_data = []
    
    for paciente in pacientes:
        # Obtener valoraciones completadas
        valoraciones = paciente.valoraciones_profesionales.filter(
            estado='COMPLETADA'
        )
        
        # Obtener terapias recomendadas (únicas)
        terapias_recomendadas = set()
        for val in valoraciones:
            terapias_recomendadas.add(val.terapia)
        
        # Obtener admisiones vigentes
        admisiones_vigentes = paciente.admisiones.filter(
            estado='VIGENTE',
            fecha_inicio__lte=date.today(),
            fecha_fin__gte=date.today()
        )
        
        # Verificar si tiene admisiones para todas las terapias valoradas
        terapias_valoradas = {val.terapia for val in valoraciones}
        terapias_con_admision = {adm.terapia for adm in admisiones_vigentes}
        
        falta_admision = terapias_valoradas - terapias_con_admision
        
        pacientes_data.append({
            'paciente': paciente,
            'valoraciones': valoraciones,
            'total_valoraciones': valoraciones.count(),
            'terapias_recomendadas': list(terapias_recomendadas),
            'admisiones_vigentes': admisiones_vigentes,
            'falta_admision': list(falta_admision),
            'tiene_todas_admisiones': len(falta_admision) == 0,
        })
    
    # =========================================================================
    # 4. MENSAJES INFORMATIVOS
    # =========================================================================
    
    if pacientes_data:
        # Contar cuántos están listos para asignar
        listos = sum(1 for p in pacientes_data if p['tiene_todas_admisiones'])
        pendientes = len(pacientes_data) - listos
        
        if listos > 0:
            messages.success(
                request,
                f'✅ {listos} paciente(s) listo(s) para asignación a grupos'
            )
        
        if pendientes > 0:
            messages.warning(
                request,
                f'⚠️ {pendientes} paciente(s) valorado(s) pero sin todas las admisiones de terapia'
            )
    else:
        messages.info(
            request,
            'No hay pacientes pendientes de asignación a grupos'
        )
    
    # =========================================================================
    # 5. RENDERIZAR
    # =========================================================================
    
    context = {
        'pacientes_data': pacientes_data,
        'titulo': 'Pacientes Pendientes de Asignación a Terapias',
    }
    
    return render(request, 'procedimientos/pacientes_pendientes_asignacion.html', context)


# =============================================================================
# FUNCIÓN AUXILIAR: Verificar si paciente puede asignarse
# =============================================================================

def puede_asignar_paciente_a_grupo(paciente, grupo):
    """
    Verifica si un paciente puede asignarse a un grupo.
    
    Requisitos:
    1. Tiene valoración completada para la terapia del grupo
    2. Tiene admisión vigente para la terapia del grupo
    
    Returns:
        tuple: (puede: bool, mensaje: str, admision: AdmisionTerapia|None)
    """
    
    # 1. Verificar valoración para la terapia
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
    
    # 2. Verificar admisión vigente
    admision = AdmisionTerapia.objects.filter(
        paciente=paciente,
        terapia=grupo.terapia,
        estado='VIGENTE',
        fecha_inicio__lte=date.today(),
        fecha_fin__gte=date.today()
    ).first()
    
    if not admision:
        return (
            False,
            f'El paciente no tiene admisión vigente para {grupo.terapia.nombre}',
            None
        )
    
    # 3. Verificar que no esté ya asignado
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
    
    return True, '', admision


# =============================================================================
# EXPLICACIÓN DE CAMBIOS
# =============================================================================

"""
ANTES (con ValoracionInicial):
- hasattr(paciente, 'valoracion_inicial')
- paciente.valoracion_inicial.completada
- Relación OneToOne → una sola valoración

AHORA (con ValoracionProfesional):
- paciente.valoraciones_profesionales.filter(estado='COMPLETADA')
- Relación ForeignKey → múltiples valoraciones
- Una valoración por cada terapeuta/terapia

FLUJO CORRECTO:
1. Paciente ingresa → Estado ADMITIDO
2. Terapeutas hacen valoraciones → ValoracionProfesional (completadas)
3. Se crean AdmisionTerapia por cada terapia
4. Paciente pasa a PENDIENTE_ASIGNACION
5. Se puede asignar a grupos (si tiene admisión para esa terapia)

VALIDACIONES:
- Debe tener al menos 1 valoración completada
- Para asignar a grupo, debe tener:
  * Valoración completada para esa terapia
  * Admisión vigente para esa terapia
"""
