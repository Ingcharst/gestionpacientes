# CREAR: apps/grupos/views_asistencia.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from apps.procedimientos.models import AsistenciaSesion, AdmisionTerapia
from .models import GrupoTerapeutico, AsignacionGrupo


@login_required
def control_asistencia_grupo(request, grupo_id):
    """Control de asistencia diaria por grupo"""
    grupo = get_object_or_404(GrupoTerapeutico, pk=grupo_id)
    hoy = timezone.now().date()
    
    # Pacientes activos del grupo con admisiones vigentes
    asignaciones = AsignacionGrupo.objects.filter(
        grupo=grupo,
        estado='ACTIVA',
        admision_terapia__estado='VIGENTE',
        admision_terapia__fecha_fin__gte=hoy
    ).select_related('paciente', 'admision_terapia')
    
    # Asistencias ya registradas hoy
    asistencias_hoy = AsistenciaSesion.objects.filter(
        grupo=grupo,
        fecha=hoy
    ).values_list('paciente_id', flat=True)
    
    if request.method == 'POST':
        with transaction.atomic():
            hora_inicio = request.POST.get('hora_inicio')
            hora_fin = request.POST.get('hora_fin')
            
            for asignacion in asignaciones:
                # Verificar si ya tiene registro hoy
                if asignacion.paciente.id in asistencias_hoy:
                    continue
                
                asistio = request.POST.get(f'asistio_{asignacion.paciente.id}') == 'on'
                justificada = request.POST.get(f'justificada_{asignacion.paciente.id}') == 'on'
                observaciones = request.POST.get(f'obs_{asignacion.paciente.id}', '')
                
                AsistenciaSesion.objects.create(
                    grupo=grupo,
                    paciente=asignacion.paciente,
                    admision=asignacion.admision_terapia,
                    fecha=hoy,
                    hora_inicio=hora_inicio or None,
                    hora_fin=hora_fin or None,
                    asistio=asistio,
                    justificada=justificada,
                    observaciones=observaciones,
                    registrado_por=request.user
                )
                
                # Actualizar contador de inasistencias
                if not asistio:
                    asignacion.dias_inasistencias_consecutivas += 1
                else:
                    asignacion.dias_inasistencias_consecutivas = 0
                    asignacion.fecha_ultima_asistencia = hoy
                
                asignacion.save()
            
            messages.success(request, 'Asistencia registrada')
            return redirect('grupos:control_asistencia_grupo', grupo_id=grupo_id)
    
    context = {
        'grupo': grupo,
        'asignaciones': asignaciones,
        'asistencias_registradas': asignacion.paciente.id in asistencias_hoy,
        'fecha': hoy,
    }
    return render(request, 'grupos/control_asistencia.html', context)


@login_required
def historial_asistencia_paciente(request, paciente_id):
    """Historial de asistencias de un paciente"""
    from apps.procedimientos.models import Paciente
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    asistencias = AsistenciaSesion.objects.filter(
        paciente=paciente
    ).select_related('grupo', 'admision').order_by('-fecha')[:30]
    
    # Estadísticas
    total = asistencias.count()
    asistencias_count = asistencias.filter(asistio=True).count()
    inasistencias = total - asistencias_count
    porcentaje = (asistencias_count / total * 100) if total > 0 else 0
    
    context = {
        'paciente': paciente,
        'asistencias': asistencias,
        'stats': {
            'total': total,
            'asistencias': asistencias_count,
            'inasistencias': inasistencias,
            'porcentaje': round(porcentaje, 1)
        }
    }
    return render(request, 'grupos/historial_asistencia.html', context)


@login_required
def cambiar_cupo_grupo(request, grupo_id):
    """Cambiar capacidad máxima del grupo"""
    grupo = get_object_or_404(GrupoTerapeutico, pk=grupo_id)
    
    if request.method == 'POST':
        from .forms import CambioCupoGrupoForm
        form = CambioCupoGrupoForm(request.POST)
        
        if form.is_valid():
            nueva_capacidad = form.cleaned_data['capacidad_maxima']
            capacidad_anterior = grupo.capacidad_maxima
            
            # Contar pacientes activos actuales
            activos = AsignacionGrupo.objects.filter(
                grupo=grupo,
                estado='ACTIVA',
                admision_terapia__estado='VIGENTE'
            ).count()
            
            grupo.capacidad_maxima = nueva_capacidad
            grupo.save()
            
            # Generar alerta si hay sobrecupo
            if activos > nueva_capacidad:
                from .models import AlertaCupo
                alerta = AlertaCupo.objects.create(
                    grupo=grupo,
                    capacidad_anterior=capacidad_anterior,
                    capacidad_nueva=nueva_capacidad,
                    pacientes_excedentes=activos - nueva_capacidad,
                    generada_por=request.user,
                    observaciones=form.cleaned_data.get('observaciones', '')
                )
                messages.warning(
                    request,
                    f'Cupo actualizado. ALERTA: {alerta.pacientes_excedentes} pacientes deben reasignarse'
                )
                return redirect('grupos:reasignar_pacientes', alerta_id=alerta.id)
            
            messages.success(request, 'Cupo actualizado correctamente')
            return redirect('grupos:detalle_grupo', pk=grupo_id)
    else:
        from .forms import CambioCupoGrupoForm
        form = CambioCupoGrupoForm(initial={'capacidad_maxima': grupo.capacidad_maxima})
    
    # Contar activos
    activos = AsignacionGrupo.objects.filter(
        grupo=grupo,
        estado='ACTIVA',
        admision_terapia__estado='VIGENTE'
    ).count()
    
    context = {
        'grupo': grupo,
        'form': form,
        'pacientes_activos': activos
    }
    return render(request, 'grupos/cambiar_cupo.html', context)


@login_required
def reasignar_pacientes(request, alerta_id):
    """Reasignar pacientes por sobrecupo"""
    from .models import AlertaCupo
    alerta = get_object_or_404(AlertaCupo, pk=alerta_id)
    
    if alerta.estado == 'RESUELTA':
        messages.info(request, 'Esta alerta ya fue resuelta')
        return redirect('grupos:detalle_grupo', pk=alerta.grupo.id)
    
    # Pacientes que deben reasignarse (últimos asignados)
    pacientes_afectados = alerta.pacientes_afectados()
    
    if request.method == 'POST':
        # Procesar reasignaciones
        for asignacion in pacientes_afectados:
            nuevo_grupo_id = request.POST.get(f'grupo_{asignacion.id}')
            if nuevo_grupo_id:
                nuevo_grupo = GrupoTerapeutico.objects.get(pk=nuevo_grupo_id)
                asignacion.grupo = nuevo_grupo
                asignacion.save()
        
        # Marcar alerta como resuelta
        alerta.estado = 'RESUELTA'
        alerta.fecha_resolucion = timezone.now()
        alerta.resuelta_por = request.user
        alerta.save()
        
        messages.success(request, 'Pacientes reasignados correctamente')
        return redirect('grupos:detalle_grupo', pk=alerta.grupo.id)
    
    # Grupos disponibles con cupo
    grupos_disponibles = GrupoTerapeutico.objects.filter(
        activo=True,
        terapia=alerta.grupo.terapia
    ).exclude(id=alerta.grupo.id)
    
    context = {
        'alerta': alerta,
        'pacientes_afectados': pacientes_afectados,
        'grupos_disponibles': grupos_disponibles
    }
    return render(request, 'grupos/reasignar_pacientes.html', context)
