# ✅ VISTA PARA COMPLETAR VALORACIONES
# Agregar al archivo: apps/procedimientos/views.py

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

@login_required
def completar_todas_valoraciones(request, paciente_id):
    """
    Marca todas las valoraciones del paciente como completadas
    y cambia su estado a PENDIENTE_ASIGNACION
    
    Esta función se llama cuando un asesor verifica que todas
    las valoraciones profesionales están completadas.
    """
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Verificar que el usuario tenga permisos (asesor o admin)
    if not request.user.is_staff:
        messages.error(request, 'No tiene permisos para realizar esta acción.')
        return redirect('procedimientos:pacientes_pendientes_valoracion')
    
    try:
        with transaction.atomic():
            # Contar valoraciones profesionales del paciente
            valoraciones = ValoracionProfesional.objects.filter(
                paciente=paciente
            )
            
            total_valoraciones = valoraciones.count()
            
            # Verificar que tiene al menos una valoración
            if total_valoraciones == 0:
                messages.warning(
                    request, 
                    f'El paciente {paciente.nombre_completo} no tiene ninguna valoración registrada.'
                )
                return redirect('procedimientos:pacientes_pendientes_valoracion')
            
            # Cambiar estado del paciente
            paciente.estado = 'PENDIENTE_ASIGNACION'
            paciente.save()
            
            messages.success(
                request,
                f'✅ Valoraciones completadas. {paciente.nombre_completo} está listo para asignación de grupos. '
                f'Total de valoraciones: {total_valoraciones}'
            )
            
    except Exception as e:
        messages.error(request, f'Error al completar valoraciones: {str(e)}')
    
    return redirect('procedimientos:pacientes_pendientes_valoracion')


@login_required
def verificar_estado_valoraciones(request, paciente_id):
    """
    API para verificar el estado de las valoraciones de un paciente
    Retorna información sobre cuántas valoraciones tiene completadas
    """
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Obtener todas las valoraciones profesionales
    valoraciones = ValoracionProfesional.objects.filter(
        paciente=paciente
    ).select_related('terapia', 'terapeuta')
    
    # Preparar respuesta
    valoraciones_data = []
    for val in valoraciones:
        valoraciones_data.append({
            'terapia': val.terapia.nombre,
            'terapeuta': val.terapeuta.get_full_name() if val.terapeuta else 'No asignado',
            'fecha': val.fecha_valoracion.strftime('%d/%m/%Y'),
            'estado_salud': val.estado_salud_general[:50] + '...' if len(val.estado_salud_general) > 50 else val.estado_salud_general
        })
    
    return JsonResponse({
        'paciente': paciente.nombre_completo,
        'total_valoraciones': len(valoraciones_data),
        'valoraciones': valoraciones_data,
        'puede_completar': len(valoraciones_data) > 0,
        'estado_actual': paciente.get_estado_display()
    })


@login_required
def cambiar_estado_paciente(request, paciente_id):
    """
    Vista general para cambiar el estado de un paciente
    Permite cambiar entre diferentes estados según el flujo
    """
    if request.method != 'POST':
        messages.error(request, 'Método no permitido.')
        return redirect('procedimientos:pacientes_pendientes_valoracion')
    
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    nuevo_estado = request.POST.get('nuevo_estado')
    
    # Validar estados permitidos
    estados_validos = ['ADMITIDO', 'PENDIENTE_VALORACION', 'PENDIENTE_ASIGNACION', 'ACTIVO']
    
    if nuevo_estado not in estados_validos:
        messages.error(request, f'Estado inválido: {nuevo_estado}')
        return redirect('procedimientos:pacientes_pendientes_valoracion')
    
    try:
        estado_anterior = paciente.get_estado_display()
        paciente.estado = nuevo_estado
        paciente.save()
        
        messages.success(
            request,
            f'✅ Estado del paciente {paciente.nombre_completo} cambiado de '
            f'"{estado_anterior}" a "{paciente.get_estado_display()}"'
        )
        
    except Exception as e:
        messages.error(request, f'Error al cambiar estado: {str(e)}')
    
    return redirect('procedimientos:pacientes_pendientes_valoracion')
