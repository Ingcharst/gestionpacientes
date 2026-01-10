# VISTAS: EVOLUCIONES DE PACIENTES
# Archivo: apps/procedimientos/views.py
# AGREGAR estas vistas

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg
from .models import EvolucionPaciente, Paciente
from .forms import EvolucionPacienteForm

@login_required
def crear_evolucion(request, paciente_id=None, grupo_id=None):
    """Crear nueva evolución de paciente"""
    
    if request.method == 'POST':
        form = EvolucionPacienteForm(
            request.POST,
            profesional=request.user,
            paciente_id=paciente_id,
            grupo_id=grupo_id
        )
        
        if form.is_valid():
            evolucion = form.save(commit=False)
            evolucion.profesional = request.user
            evolucion.save()
            
            messages.success(
                request,
                f'Evolución de {evolucion.paciente.nombre_completo} registrada exitosamente.'
            )
            
            # Redirigir según origen
            if grupo_id:
                return redirect('grupos:detalle_grupo', grupo_id=grupo_id)
            else:
                return redirect('procedimientos:evoluciones_paciente', paciente_id=paciente_id)
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = EvolucionPacienteForm(
            profesional=request.user,
            paciente_id=paciente_id,
            grupo_id=grupo_id
        )
    
    # Obtener contexto adicional
    paciente = None
    if paciente_id:
        paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    context = {
        'form': form,
        'paciente': paciente,
        'grupo_id': grupo_id,
    }
    
    return render(request, 'procedimientos/crear_evolucion.html', context)


@login_required
def editar_evolucion(request, evolucion_id):
    """Editar evolución existente (solo si no está firmada)"""
    evolucion = get_object_or_404(EvolucionPaciente, pk=evolucion_id)
    
    # Verificar permisos
    if evolucion.firmado:
        messages.error(request, 'No se puede editar una evolución firmada.')
        return redirect('procedimientos:detalle_evolucion', evolucion_id=evolucion_id)
    
    if evolucion.profesional != request.user and not request.user.is_superuser:
        messages.error(request, 'No tiene permisos para editar esta evolución.')
        return redirect('procedimientos:detalle_evolucion', evolucion_id=evolucion_id)
    
    if request.method == 'POST':
        form = EvolucionPacienteForm(request.POST, instance=evolucion)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Evolución actualizada exitosamente.')
            return redirect('procedimientos:detalle_evolucion', evolucion_id=evolucion_id)
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = EvolucionPacienteForm(instance=evolucion)
    
    context = {
        'form': form,
        'evolucion': evolucion,
        'editando': True,
    }
    
    return render(request, 'procedimientos/crear_evolucion.html', context)


@login_required
def detalle_evolucion(request, evolucion_id):
    """Ver detalle de una evolución"""
    evolucion = get_object_or_404(EvolucionPaciente, pk=evolucion_id)
    
    context = {
        'evolucion': evolucion,
    }
    
    return render(request, 'procedimientos/detalle_evolucion.html', context)


@login_required
def evoluciones_paciente(request, paciente_id):
    """Listar todas las evoluciones de un paciente"""
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Filtros
    terapia_id = request.GET.get('terapia')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    evoluciones = EvolucionPaciente.objects.filter(
        paciente=paciente
    ).select_related('profesional', 'terapia', 'grupo')
    
    if terapia_id:
        evoluciones = evoluciones.filter(terapia_id=terapia_id)
    
    if fecha_desde:
        evoluciones = evoluciones.filter(fecha_sesion__gte=fecha_desde)
    
    if fecha_hasta:
        evoluciones = evoluciones.filter(fecha_sesion__lte=fecha_hasta)
    
    # Estadísticas
    estadisticas = evoluciones.aggregate(
        total_sesiones=Count('id'),
        sesiones_asistidas=Count('id', filter=Q(asistio=True)),
        promedio_atencion=Avg('nivel_atencion'),
        promedio_participacion=Avg('nivel_participacion'),
        promedio_colaboracion=Avg('nivel_colaboracion'),
        promedio_comprension=Avg('nivel_comprension'),
    )
    
    # Calcular porcentaje de asistencia
    if estadisticas['total_sesiones'] > 0:
        estadisticas['porcentaje_asistencia'] = round(
            (estadisticas['sesiones_asistidas'] / estadisticas['total_sesiones']) * 100, 1
        )
    else:
        estadisticas['porcentaje_asistencia'] = 0
    
    # Terapias disponibles para filtro
    from .models import Terapia
    terapias = Terapia.objects.filter(
        evoluciones__paciente=paciente
    ).distinct()
    
    context = {
        'paciente': paciente,
        'evoluciones': evoluciones,
        'estadisticas': estadisticas,
        'terapias': terapias,
    }
    
    return render(request, 'procedimientos/evoluciones_paciente.html', context)


@login_required
def mis_evoluciones(request):
    """Listar evoluciones registradas por el profesional actual"""
    
    # Filtros
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    paciente_id = request.GET.get('paciente')
    terapia_id = request.GET.get('terapia')
    
    evoluciones = EvolucionPaciente.objects.filter(
        profesional=request.user
    ).select_related('paciente', 'terapia', 'grupo')
    
    if fecha_desde:
        evoluciones = evoluciones.filter(fecha_sesion__gte=fecha_desde)
    
    if fecha_hasta:
        evoluciones = evoluciones.filter(fecha_sesion__lte=fecha_hasta)
    
    if paciente_id:
        evoluciones = evoluciones.filter(paciente_id=paciente_id)
    
    if terapia_id:
        evoluciones = evoluciones.filter(terapia_id=terapia_id)
    
    # Estadísticas
    estadisticas = evoluciones.aggregate(
        total_registradas=Count('id'),
        total_firmadas=Count('id', filter=Q(firmado=True)),
        total_pendientes=Count('id', filter=Q(firmado=False)),
    )
    
    context = {
        'evoluciones': evoluciones,
        'estadisticas': estadisticas,
    }
    
    return render(request, 'procedimientos/mis_evoluciones.html', context)


@login_required
def firmar_evolucion(request, evolucion_id):
    """Firmar y finalizar una evolución"""
    evolucion = get_object_or_404(EvolucionPaciente, pk=evolucion_id)
    
    # Verificar permisos
    if evolucion.profesional != request.user and not request.user.is_superuser:
        messages.error(request, 'No tiene permisos para firmar esta evolución.')
        return redirect('procedimientos:detalle_evolucion', evolucion_id=evolucion_id)
    
    if evolucion.firmado:
        messages.warning(request, 'Esta evolución ya está firmada.')
        return redirect('procedimientos:detalle_evolucion', evolucion_id=evolucion_id)
    
    if request.method == 'POST':
        evolucion.firmado = True
        evolucion.save()
        messages.success(
            request,
            'Evolución firmada exitosamente. Ya no se podrá modificar.'
        )
        return redirect('procedimientos:detalle_evolucion', evolucion_id=evolucion_id)
    
    context = {
        'evolucion': evolucion,
    }
    
    return render(request, 'procedimientos/confirmar_firma.html', context)


@login_required
def eliminar_evolucion(request, evolucion_id):
    """Eliminar evolución (solo si no está firmada)"""
    evolucion = get_object_or_404(EvolucionPaciente, pk=evolucion_id)
    
    # Verificar permisos
    if evolucion.firmado:
        messages.error(request, 'No se puede eliminar una evolución firmada.')
        return redirect('procedimientos:detalle_evolucion', evolucion_id=evolucion_id)
    
    if evolucion.profesional != request.user and not request.user.is_superuser:
        messages.error(request, 'No tiene permisos para eliminar esta evolución.')
        return redirect('procedimientos:detalle_evolucion', evolucion_id=evolucion_id)
    
    if request.method == 'POST':
        paciente_id = evolucion.paciente_id
        evolucion.delete()
        messages.success(request, 'Evolución eliminada exitosamente.')
        return redirect('procedimientos:evoluciones_paciente', paciente_id=paciente_id)
    
    context = {
        'evolucion': evolucion,
    }
    
    return render(request, 'procedimientos/confirmar_eliminar_evolucion.html', context)
