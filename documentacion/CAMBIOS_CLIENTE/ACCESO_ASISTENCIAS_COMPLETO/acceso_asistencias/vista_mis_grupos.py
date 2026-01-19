# ✅ VISTA "MIS GRUPOS" CON ESTADÍSTICAS
# Archivo: apps/grupos/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from datetime import date

from apps.grupos.models import GrupoTerapeutico, AsignacionGrupo


@login_required
def mis_grupos(request):
    """
    Lista de grupos donde el usuario es terapeuta responsable
    Con estadísticas de asistencia del día
    """
    fecha_hoy = date.today()
    
    # Obtener grupos del terapeuta
    grupos_base = GrupoTerapeutico.objects.filter(
        terapeuta_responsable=request.user,
        estado='ACTIVO'
    ).select_related('terapia', 'consultorio')
    
    # Procesar cada grupo
    grupos_procesados = []
    
    for grupo in grupos_base:
        # Obtener asignaciones activas
        asignaciones = AsignacionGrupo.objects.filter(
            grupo=grupo,
            estado='ACTIVA'
        ).select_related('paciente', 'admision_terapia')
        
        # ✅ FILTRAR: Solo pacientes con admisión vigente
        pacientes_vigentes = []
        for asig in asignaciones:
            if asig.admision_terapia:
                admision = asig.admision_terapia
                if (admision.estado == 'VIGENTE' and
                    admision.fecha_inicio <= fecha_hoy <= admision.fecha_fin):
                    pacientes_vigentes.append(asig)
        
        # Verificar si ya se registró asistencia hoy
        # Importar modelo si existe
        try:
            from apps.grupos.models import AsistenciaPaciente
            asistencias_hoy = AsistenciaPaciente.objects.filter(
                grupo=grupo,
                fecha=fecha_hoy
            )
            asistencia_registrada = asistencias_hoy.exists()
            total_asistencias_hoy = asistencias_hoy.count()
        except ImportError:
            asistencia_registrada = False
            total_asistencias_hoy = 0
        
        # Calcular porcentaje de ocupación
        total_vigentes = len(pacientes_vigentes)
        porcentaje_ocupacion = round(
            (total_vigentes / grupo.capacidad_maxima * 100) 
            if grupo.capacidad_maxima > 0 else 0, 
            1
        )
        
        # Agregar datos calculados al grupo
        grupo.total_pacientes_vigentes = total_vigentes
        grupo.asistencia_registrada_hoy = asistencia_registrada
        grupo.total_asistencias_hoy = total_asistencias_hoy
        grupo.porcentaje_ocupacion = porcentaje_ocupacion
        grupo.pacientes_sample = pacientes_vigentes[:3]  # Primeros 3 para preview
        
        grupos_procesados.append(grupo)
    
    # Ordenar por nombre
    grupos_procesados.sort(key=lambda x: x.nombre)
    
    context = {
        'grupos': grupos_procesados,
        'fecha_hoy': fecha_hoy,
        'total_grupos': len(grupos_procesados),
    }
    
    return render(request, 'grupos/mis_grupos.html', context)


# ================================================
# ALTERNATIVA: Vista optimizada con anotaciones
# ================================================

@login_required
def mis_grupos_optimizado(request):
    """
    Versión optimizada con anotaciones de Django ORM
    """
    from django.db.models import Prefetch
    fecha_hoy = date.today()
    
    # Prefetch asignaciones con admisiones vigentes
    asignaciones_vigentes = AsignacionGrupo.objects.filter(
        estado='ACTIVA',
        admision_terapia__estado='VIGENTE',
        admision_terapia__fecha_inicio__lte=fecha_hoy,
        admision_terapia__fecha_fin__gte=fecha_hoy
    ).select_related('paciente', 'admision_terapia')
    
    # Obtener grupos con anotaciones
    grupos = GrupoTerapeutico.objects.filter(
        terapeuta_responsable=request.user,
        estado='ACTIVO'
    ).select_related(
        'terapia', 
        'consultorio'
    ).prefetch_related(
        Prefetch('asignaciones', queryset=asignaciones_vigentes, to_attr='asignaciones_vigentes')
    ).annotate(
        total_asignaciones=Count('asignaciones', filter=Q(asignaciones__estado='ACTIVA'))
    )
    
    # Procesar grupos
    for grupo in grupos:
        # Contar pacientes vigentes
        grupo.total_pacientes_vigentes = len(grupo.asignaciones_vigentes)
        
        # Porcentaje de ocupación
        grupo.porcentaje_ocupacion = round(
            (grupo.total_pacientes_vigentes / grupo.capacidad_maxima * 100) 
            if grupo.capacidad_maxima > 0 else 0, 
            1
        )
        
        # Sample de pacientes
        grupo.pacientes_sample = grupo.asignaciones_vigentes[:3]
        
        # Verificar asistencia del día
        try:
            from apps.grupos.models import AsistenciaPaciente
            asistencias = AsistenciaPaciente.objects.filter(
                grupo=grupo,
                fecha=fecha_hoy
            )
            grupo.asistencia_registrada_hoy = asistencias.exists()
            grupo.total_asistencias_hoy = asistencias.count()
        except ImportError:
            grupo.asistencia_registrada_hoy = False
            grupo.total_asistencias_hoy = 0
    
    context = {
        'grupos': grupos,
        'fecha_hoy': fecha_hoy,
        'total_grupos': grupos.count(),
    }
    
    return render(request, 'grupos/mis_grupos.html', context)
