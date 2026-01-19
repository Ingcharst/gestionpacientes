# ✅ VISTA PARA TOMAR ASISTENCIA
# Archivo: apps/grupos/views.py (agregar estas vistas)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import date

from apps.grupos.models import GrupoTerapeutico, AsignacionGrupo
from apps.procedimientos.models import AdmisionTerapia


@login_required
def control_asistencia_grupo(request, grupo_id):
    """
    Vista para tomar asistencia diaria del grupo
    Solo muestra pacientes con admisiones vigentes
    """
    grupo = get_object_or_404(GrupoTerapeutico, pk=grupo_id)
    fecha_hoy = date.today()
    
    # Obtener asignaciones activas del grupo
    asignaciones = AsignacionGrupo.objects.filter(
        grupo=grupo,
        estado='ACTIVA'
    ).select_related('paciente', 'admision_terapia')
    
    # ✅ FILTRAR: Solo pacientes con admisión vigente
    asignaciones_vigentes = []
    for asig in asignaciones:
        if asig.admision_terapia:
            # Verificar que la admisión esté vigente
            if (asig.admision_terapia.estado == 'VIGENTE' and
                asig.admision_terapia.fecha_inicio <= fecha_hoy <= asig.admision_terapia.fecha_fin):
                asignaciones_vigentes.append(asig)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                hora_inicio = request.POST.get('hora_inicio')
                hora_fin = request.POST.get('hora_fin')
                
                asistencias_registradas = 0
                
                for asig in asignaciones_vigentes:
                    paciente_id = asig.paciente.id
                    asistio = request.POST.get(f'asistio_{paciente_id}') == 'on'
                    justificada = request.POST.get(f'justificada_{paciente_id}') == 'on'
                    observaciones = request.POST.get(f'obs_{paciente_id}', '').strip()
                    
                    # Crear registro de asistencia
                    # NOTA: Necesitas crear el modelo AsistenciaPaciente si no existe
                    # o usar el que ya tengas
                    from apps.grupos.models import AsistenciaPaciente
                    
                    AsistenciaPaciente.objects.create(
                        paciente=asig.paciente,
                        grupo=grupo,
                        asignacion=asig,
                        fecha=fecha_hoy,
                        asistio=asistio,
                        justificada=justificada if not asistio else False,
                        observaciones=observaciones,
                        hora_inicio=hora_inicio or None,
                        hora_fin=hora_fin or None,
                        registrado_por=request.user
                    )
                    
                    # ✅ Actualizar contador en admisión si asistió
                    if asistio and asig.admision_terapia:
                        asig.admision_terapia.cantidad_realizada += 1
                        asig.admision_terapia.save()
                    
                    asistencias_registradas += 1
                
                messages.success(
                    request,
                    f'✅ Asistencia registrada: {asistencias_registradas} pacientes'
                )
                return redirect('grupos:detalle_grupo', pk=grupo.id)
                
        except Exception as e:
            messages.error(request, f'Error al registrar asistencia: {str(e)}')
    
    # Ver si ya hay asistencias registradas hoy
    from apps.grupos.models import AsistenciaPaciente
    asistencias_hoy = AsistenciaPaciente.objects.filter(
        grupo=grupo,
        fecha=fecha_hoy
    ).values_list('paciente_id', flat=True)
    
    context = {
        'grupo': grupo,
        'asignaciones': asignaciones_vigentes,
        'fecha': fecha_hoy,
        'asistencias_registradas': list(asistencias_hoy),
        'total_pacientes': len(asignaciones_vigentes)
    }
    
    return render(request, 'grupos/control_asistencia.html', context)


@login_required
def lista_grupos_terapeuta(request):
    """
    Lista de grupos donde el terapeuta es responsable
    Para acceso rápido a tomar asistencia
    """
    # Filtrar grupos donde el usuario es el terapeuta responsable
    grupos = GrupoTerapeutico.objects.filter(
        terapeuta_responsable=request.user,
        estado='ACTIVO'
    ).annotate(
        total_pacientes=models.Count('asignaciones', filter=models.Q(asignaciones__estado='ACTIVA'))
    )
    
    context = {
        'grupos': grupos,
        'fecha_hoy': date.today()
    }
    
    return render(request, 'grupos/mis_grupos.html', context)


@login_required
def historial_asistencia_paciente(request, paciente_id):
    """
    Historial completo de asistencias de un paciente
    """
    from apps.procedimientos.models import Paciente
    from apps.grupos.models import AsistenciaPaciente
    
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    asistencias = AsistenciaPaciente.objects.filter(
        paciente=paciente
    ).select_related('grupo').order_by('-fecha')
    
    # Estadísticas
    total = asistencias.count()
    asistencias_count = asistencias.filter(asistio=True).count()
    inasistencias_count = asistencias.filter(asistio=False).count()
    porcentaje = round((asistencias_count / total * 100) if total > 0 else 0, 1)
    
    stats = {
        'total': total,
        'asistencias': asistencias_count,
        'inasistencias': inasistencias_count,
        'porcentaje': porcentaje
    }
    
    context = {
        'paciente': paciente,
        'asistencias': asistencias[:50],  # Últimas 50
        'stats': stats
    }
    
    return render(request, 'grupos/historial_asistencia.html', context)
