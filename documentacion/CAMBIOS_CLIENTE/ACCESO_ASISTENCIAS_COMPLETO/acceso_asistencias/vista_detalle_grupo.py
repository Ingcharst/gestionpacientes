# ✅ VISTA DETALLE GRUPO CON FILTRO DE ADMISIONES
# Archivo: apps/grupos/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import date

from apps.grupos.models import GrupoTerapeutico, AsignacionGrupo


@login_required
def grupo_detalle(request, pk):
    """
    Vista detallada del grupo con listado de pacientes
    Separa pacientes con admisión vigente de los que no la tienen
    """
    grupo = get_object_or_404(GrupoTerapeutico, pk=pk)
    fecha_hoy = date.today()
    
    # Obtener todas las asignaciones activas del grupo
    asignaciones = AsignacionGrupo.objects.filter(
        grupo=grupo,
        estado='ACTIVA'
    ).select_related(
        'paciente',
        'admision_terapia',
        'admision_terapia__terapia'
    ).order_by('paciente__apellidos', 'paciente__nombres')
    
    # ✅ SEPARAR: Pacientes con admisión vigente vs sin admisión
    pacientes_con_admision = []
    pacientes_sin_admision = []
    
    for asig in asignaciones:
        if asig.admision_terapia:
            # Verificar que la admisión esté vigente
            admision = asig.admision_terapia
            
            if (admision.estado == 'VIGENTE' and
                admision.fecha_inicio <= fecha_hoy <= admision.fecha_fin):
                # ✅ Admisión VIGENTE
                pacientes_con_admision.append(asig)
            else:
                # ❌ Admisión vencida o inactiva
                pacientes_sin_admision.append(asig)
        else:
            # ❌ Sin admisión
            pacientes_sin_admision.append(asig)
    
    # Contar pacientes activos totales
    pacientes_activos = len(pacientes_con_admision)
    
    context = {
        'grupo': grupo,
        'pacientes_con_admision': pacientes_con_admision,
        'pacientes_sin_admision': pacientes_sin_admision,
        'pacientes_activos': pacientes_activos,
        'fecha_hoy': fecha_hoy,
    }
    
    return render(request, 'grupos/detalle_grupo.html', context)


# ================================================
# VISTA ALTERNATIVA: Si ya tienes grupo_detalle
# ================================================

@login_required
def grupo_detalle_mejorado(request, pk):
    """
    Versión mejorada de la vista de detalle del grupo
    Incluye más información y estadísticas
    """
    from django.db.models import Count, Q
    
    grupo = get_object_or_404(
        GrupoTerapeutico.objects.annotate(
            total_asignaciones=Count('asignaciones', filter=Q(asignaciones__estado='ACTIVA'))
        ),
        pk=pk
    )
    
    fecha_hoy = date.today()
    
    # Obtener asignaciones con información completa
    asignaciones = AsignacionGrupo.objects.filter(
        grupo=grupo,
        estado='ACTIVA'
    ).select_related(
        'paciente',
        'admision_terapia',
        'admision_terapia__terapia'
    ).prefetch_related(
        'paciente__asignaciones_grupo'
    ).order_by('paciente__apellidos')
    
    # Filtrar por vigencia de admisión
    pacientes_con_admision = []
    pacientes_sin_admision = []
    
    for asig in asignaciones:
        tiene_admision_vigente = False
        
        if asig.admision_terapia:
            admision = asig.admision_terapia
            
            # Verificar vigencia
            if (admision.estado == 'VIGENTE' and
                admision.fecha_inicio <= fecha_hoy <= admision.fecha_fin):
                tiene_admision_vigente = True
        
        if tiene_admision_vigente:
            pacientes_con_admision.append(asig)
        else:
            pacientes_sin_admision.append(asig)
    
    # Estadísticas adicionales
    if pacientes_con_admision:
        progreso_promedio = sum(
            asig.admision_terapia.progreso_porcentaje 
            for asig in pacientes_con_admision 
            if asig.admision_terapia
        ) / len(pacientes_con_admision)
    else:
        progreso_promedio = 0
    
    context = {
        'grupo': grupo,
        'pacientes_con_admision': pacientes_con_admision,
        'pacientes_sin_admision': pacientes_sin_admision,
        'pacientes_activos': len(pacientes_con_admision),
        'fecha_hoy': fecha_hoy,
        'progreso_promedio': round(progreso_promedio, 1),
        'total_asignaciones': grupo.total_asignaciones,
    }
    
    return render(request, 'grupos/detalle_grupo.html', context)
