# ============================================================================
# SPRINT 1 - VISTAS
# apps/procedimientos/views.py
# ============================================================================

"""
INSTRUCCIONES:
Agregar estas vistas al final de apps/procedimientos/views.py
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction

from apps.procedimientos.models import Paciente, ValoracionInicial
from apps.procedimientos.forms import (
    AdmisionPacienteForm, ValoracionInicialForm, ProblemaDetectadoForm
)


# ============================================================================
# VISTA: ADMISIÓN DE PACIENTE
# ============================================================================

@login_required
def admision_paciente(request):
    """
    Vista para admisión de nuevos pacientes.
    Incluye captura de firma digital del acudiente.
    """
    if request.method == 'POST':
        form = AdmisionPacienteForm(request.POST, request.FILES)
        
        # Pasar request al formulario para capturar IP
        form.request = request
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    paciente = form.save(commit=False)
                    
                    # Establecer creado_por
                    paciente.creado_por = request.user
                    
                    # Guardar paciente
                    paciente.save()
                    form.save_m2m()
                    
                    messages.success(
                        request,
                        f'Paciente {paciente.nombre_completo} admitido exitosamente. '
                        f'Número de Admisión: {paciente.numero_admision}'
                    )
                    
                    # Redirigir a detalle del paciente
                    return redirect('procedimientos:paciente_detail', pk=paciente.pk)
                    
            except Exception as e:
                messages.error(request, f'Error al guardar paciente: {str(e)}')
        else:
            # Mostrar errores de validación
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = AdmisionPacienteForm()
    
    context = {
        'form': form,
        'titulo': 'Admisión de Nuevo Paciente',
        'mostrar_firma': True,  # Flag para mostrar pad de firma
    }
    
    return render(request, 'procedimientos/admision_paciente.html', context)


# ============================================================================
# VISTA: LISTA DE PACIENTES ADMITIDOS (Sin Valorar)
# ============================================================================

@login_required
def pacientes_pendientes_valoracion(request):
    """
    Lista de pacientes admitidos que están pendientes de valoración inicial.
    """
    pacientes = Paciente.objects.filter(
        estado=Paciente.Estado.ADMITIDO
    ).order_by('-fecha_ingreso')
    
    context = {
        'pacientes': pacientes,
        'titulo': 'Pacientes Pendientes de Valoración',
        'estado_filtro': 'ADMITIDO',
    }
    
    return render(request, 'procedimientos/pacientes_pendientes_valoracion.html', context)


# ============================================================================
# VISTA: CREAR VALORACIÓN INICIAL
# ============================================================================

@login_required
def crear_valoracion_inicial(request, paciente_id):
    """
    Vista para crear valoración inicial de un paciente.
    Solo se puede valorar pacientes en estado ADMITIDO.
    """
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Verificar que el paciente esté en estado ADMITIDO
    if paciente.estado != Paciente.Estado.ADMITIDO:
        messages.warning(
            request,
            f'El paciente está en estado {paciente.get_estado_display()}. '
            'Solo se pueden valorar pacientes admitidos.'
        )
        return redirect('procedimientos:paciente_detail', pk=paciente_id)
    
    # Verificar que no tenga ya una valoración
    if hasattr(paciente, 'valoracion_inicial'):
        messages.info(request, 'Este paciente ya tiene una valoración inicial.')
        return redirect('procedimientos:ver_valoracion_inicial', paciente_id=paciente_id)
    
    if request.method == 'POST':
        form = ValoracionInicialForm(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    valoracion = form.save(commit=False)
                    valoracion.paciente = paciente
                    valoracion.profesional = request.user
                    
                    # Procesar problemas detectados desde JSON (si vienen por POST)
                    problemas_json = request.POST.get('problemas_detectados_json', '[]')
                    import json
                    try:
                        valoracion.problemas_detectados = json.loads(problemas_json)
                    except:
                        valoracion.problemas_detectados = []
                    
                    valoracion.save()
                    form.save_m2m()  # Guardar terapias recomendadas
                    
                    messages.success(
                        request,
                        f'Valoración inicial creada exitosamente. '
                        f'Código: {valoracion.codigo_valoracion}'
                    )
                    
                    # Si se marcó como completada, el estado del paciente cambia automáticamente
                    if valoracion.completada:
                        messages.info(
                            request,
                            f'El paciente {paciente.nombre_completo} ahora está en estado: '
                            'Pendiente de Asignación a Terapias'
                        )
                    
                    return redirect('procedimientos:ver_valoracion_inicial', paciente_id=paciente_id)
                    
            except Exception as e:
                messages.error(request, f'Error al guardar valoración: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ValoracionInicialForm()
    
    # Formulario para problemas (se usa dinámicamente con JS)
    problema_form = ProblemaDetectadoForm()
    
    context = {
        'form': form,
        'problema_form': problema_form,
        'paciente': paciente,
        'titulo': f'Valoración Inicial - {paciente.nombre_completo}',
    }
    
    return render(request, 'procedimientos/crear_valoracion_inicial.html', context)


# ============================================================================
# VISTA: VER VALORACIÓN INICIAL
# ============================================================================

@login_required
def ver_valoracion_inicial(request, paciente_id):
    """
    Vista para ver la valoración inicial de un paciente.
    """
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    if not hasattr(paciente, 'valoracion_inicial'):
        messages.error(request, 'Este paciente no tiene valoración inicial.')
        return redirect('procedimientos:paciente_detail', pk=paciente_id)
    
    valoracion = paciente.valoracion_inicial
    
    context = {
        'paciente': paciente,
        'valoracion': valoracion,
        'titulo': f'Valoración Inicial - {paciente.nombre_completo}',
    }
    
    return render(request, 'procedimientos/ver_valoracion_inicial.html', context)


# ============================================================================
# VISTA: EDITAR VALORACIÓN INICIAL
# ============================================================================

@login_required
def editar_valoracion_inicial(request, paciente_id):
    """
    Vista para editar valoración inicial de un paciente.
    """
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    if not hasattr(paciente, 'valoracion_inicial'):
        messages.error(request, 'Este paciente no tiene valoración inicial.')
        return redirect('procedimientos:crear_valoracion_inicial', paciente_id=paciente_id)
    
    valoracion = paciente.valoracion_inicial
    
    if request.method == 'POST':
        form = ValoracionInicialForm(request.POST, instance=valoracion)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    valoracion = form.save(commit=False)
                    
                    # Actualizar problemas detectados
                    problemas_json = request.POST.get('problemas_detectados_json', '[]')
                    import json
                    try:
                        valoracion.problemas_detectados = json.loads(problemas_json)
                    except:
                        pass  # Mantener los existentes si hay error
                    
                    valoracion.save()
                    form.save_m2m()
                    
                    messages.success(request, 'Valoración actualizada exitosamente.')
                    
                    return redirect('procedimientos:ver_valoracion_inicial', paciente_id=paciente_id)
                    
            except Exception as e:
                messages.error(request, f'Error al actualizar valoración: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ValoracionInicialForm(instance=valoracion)
    
    problema_form = ProblemaDetectadoForm()
    
    # Pasar problemas existentes como JSON para el JavaScript
    import json
    problemas_json = json.dumps(valoracion.problemas_detectados or [])
    
    context = {
        'form': form,
        'problema_form': problema_form,
        'paciente': paciente,
        'valoracion': valoracion,
        'problemas_json': problemas_json,
        'titulo': f'Editar Valoración - {paciente.nombre_completo}',
    }
    
    return render(request, 'procedimientos/editar_valoracion_inicial.html', context)


# ============================================================================
# VISTA: COMPLETAR VALORACIÓN (AJAX)
# ============================================================================

@login_required
def completar_valoracion(request, valoracion_id):
    """
    Vista AJAX para marcar una valoración como completada.
    Esto cambia automáticamente el estado del paciente a PENDIENTE_ASIGNACION.
    """
    if request.method == 'POST':
        valoracion = get_object_or_404(ValoracionInicial, pk=valoracion_id)
        
        if not valoracion.completada:
            valoracion.completada = True
            valoracion.save()  # El método save() del modelo cambiará el estado del paciente
            
            return JsonResponse({
                'success': True,
                'message': 'Valoración completada. Paciente en estado: Pendiente Asignación',
                'nuevo_estado_paciente': valoracion.paciente.get_estado_display()
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'La valoración ya estaba completada'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


# ============================================================================
# VISTA: LISTA DE PACIENTES PENDIENTES DE ASIGNACIÓN
# ============================================================================

@login_required
def pacientes_pendientes_asignacion(request):
    """
    Lista de pacientes que han sido valorados y están pendientes de 
    asignación a grupos terapéuticos.
    
    Esta vista es para el ASESOR que asigna grupos.
    """
    pacientes = Paciente.objects.filter(
        estado=Paciente.Estado.PENDIENTE_ASIGNACION
    ).select_related('valoracion_inicial').order_by('-fecha_ingreso')
    
    # Agregar información de valoración a cada paciente
    pacientes_data = []
    for paciente in pacientes:
        if hasattr(paciente, 'valoracion_inicial'):
            valoracion = paciente.valoracion_inicial
            pacientes_data.append({
                'paciente': paciente,
                'valoracion': valoracion,
                'terapias_recomendadas': valoracion.terapias_recomendadas.all(),
                'cantidad_problemas': valoracion.cantidad_problemas,
                'areas_afectadas': valoracion.areas_afectadas,
            })
    
    context = {
        'pacientes_data': pacientes_data,
        'titulo': 'Pacientes Pendientes de Asignación a Terapias',
    }
    
    return render(request, 'procedimientos/pacientes_pendientes_asignacion.html', context)


# ============================================================================
# FIN DE VISTAS SPRINT 1
# ============================================================================
