# ✅ VISTA CORREGIDA: asignar_desde_recomendacion
# Archivo: apps/grupos/views.py

# REEMPLAZAR tu función actual con esta:

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from datetime import date

from apps.grupos.models import GrupoTerapeutico, AsignacionGrupo
from apps.procedimientos.models import Paciente, AdmisionTerapia


@login_required
def asignar_desde_recomendacion(request, paciente_id, grupo_id):
    """
    Asigna un paciente a un grupo desde la página de recomendaciones
    
    ✅ CORREGIDO: Redirige correctamente después de asignar
    """
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    grupo = get_object_or_404(GrupoTerapeutico, pk=grupo_id)
    fecha_hoy = date.today()
    
    try:
        with transaction.atomic():
            # ✅ PASO 1: Verificar que el paciente tenga admisión vigente para esta terapia
            admision = AdmisionTerapia.objects.filter(
                paciente=paciente,
                terapia=grupo.terapia,
                estado='VIGENTE',
                fecha_inicio__lte=fecha_hoy,
                fecha_fin__gte=fecha_hoy
            ).first()
            
            if not admision:
                messages.error(
                    request,
                    f'❌ {paciente.nombre_completo} no tiene una admisión vigente '
                    f'para {grupo.terapia.nombre}. '
                    f'Debe crear una admisión antes de asignar al grupo.'
                )
                return redirect('grupos:recomendar_grupos', paciente_id=paciente_id)
            
            # ✅ PASO 2: Verificar que el grupo tenga cupo disponible
            asignaciones_activas = AsignacionGrupo.objects.filter(
                grupo=grupo,
                estado='ACTIVA'
            ).count()
            
            if asignaciones_activas >= grupo.capacidad_maxima:
                messages.warning(
                    request,
                    f'⚠️ El grupo {grupo.nombre} está lleno. '
                    f'Capacidad: {asignaciones_activas}/{grupo.capacidad_maxima}'
                )
                return redirect('grupos:recomendar_grupos', paciente_id=paciente_id)
            
            # ✅ PASO 3: Verificar que no esté ya asignado a este grupo
            asignacion_existente = AsignacionGrupo.objects.filter(
                paciente=paciente,
                grupo=grupo,
                estado='ACTIVA'
            ).exists()
            
            if asignacion_existente:
                messages.info(
                    request,
                    f'ℹ️ {paciente.nombre_completo} ya está asignado a {grupo.nombre}'
                )
                return redirect('grupos:detalle_grupo', pk=grupo_id)
            
            # ✅ PASO 4: Crear la asignación
            asignacion = AsignacionGrupo.objects.create(
                paciente=paciente,
                grupo=grupo,
                admision_terapia=admision,
                dias_asistencia=grupo.dias_disponibles,  # Asigna todos los días del grupo
                numero_terapias_semanales=len(grupo.dias_disponibles),  # Una terapia por día
                estado='ACTIVA',
                fecha_inicio_asignacion=fecha_hoy
            )
            
            # ✅ PASO 5: Mensaje de éxito
            messages.success(
                request,
                f'✅ {paciente.nombre_completo} asignado exitosamente a {grupo.nombre}. '
                f'Días: {", ".join(grupo.dias_disponibles)}'
            )
            
            # ✅ PASO 6: Redirigir al detalle del grupo (CORRECCIÓN DEL ERROR)
            return redirect('grupos:detalle_grupo', pk=grupo_id)
            
    except Exception as e:
        messages.error(
            request,
            f'❌ Error al asignar el paciente: {str(e)}'
        )
        return redirect('grupos:recomendar_grupos', paciente_id=paciente_id)


# ================================================================
# ALTERNATIVA: Si prefieres quedarte en recomendaciones
# ================================================================

@login_required
def asignar_desde_recomendacion_v2(request, paciente_id, grupo_id):
    """
    Versión alternativa: regresa a recomendaciones después de asignar
    """
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    grupo = get_object_or_404(GrupoTerapeutico, pk=grupo_id)
    fecha_hoy = date.today()
    
    try:
        with transaction.atomic():
            # Verificar admisión
            admision = AdmisionTerapia.objects.filter(
                paciente=paciente,
                terapia=grupo.terapia,
                estado='VIGENTE',
                fecha_inicio__lte=fecha_hoy,
                fecha_fin__gte=fecha_hoy
            ).first()
            
            if not admision:
                messages.error(
                    request,
                    f'No tiene admisión vigente para {grupo.terapia.nombre}'
                )
                return redirect('grupos:recomendar_grupos', paciente_id=paciente_id)
            
            # Verificar cupo
            asignaciones_activas = AsignacionGrupo.objects.filter(
                grupo=grupo,
                estado='ACTIVA'
            ).count()
            
            if asignaciones_activas >= grupo.capacidad_maxima:
                messages.warning(request, f'El grupo está lleno')
                return redirect('grupos:recomendar_grupos', paciente_id=paciente_id)
            
            # Verificar duplicado
            if AsignacionGrupo.objects.filter(
                paciente=paciente,
                grupo=grupo,
                estado='ACTIVA'
            ).exists():
                messages.info(request, 'Ya está asignado a este grupo')
                return redirect('grupos:recomendar_grupos', paciente_id=paciente_id)
            
            # Crear asignación
            AsignacionGrupo.objects.create(
                paciente=paciente,
                grupo=grupo,
                admision_terapia=admision,
                dias_asistencia=grupo.dias_disponibles,
                numero_terapias_semanales=len(grupo.dias_disponibles),
                estado='ACTIVA',
                fecha_inicio_asignacion=fecha_hoy
            )
            
            messages.success(
                request,
                f'✅ Asignado a {grupo.nombre}'
            )
            
            # ✅ REDIRIGIR A RECOMENDACIONES (para seguir asignando)
            return redirect('grupos:recomendar_grupos', paciente_id=paciente_id)
            
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('grupos:recomendar_grupos', paciente_id=paciente_id)
