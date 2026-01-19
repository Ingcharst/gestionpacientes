# ✅ VISTA CORREGIDA - CAMBIO DE ESTADO SIN VALIDACIÓN DE CANTIDAD
# Agregar al archivo: apps/procedimientos/views.py

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

@login_required
def completar_valoraciones_paciente(request, paciente_id):
    """
    Cambia el estado del paciente de PENDIENTE_VALORACION a PENDIENTE_ASIGNACION
    
    NO valida cantidad de valoraciones - el asesor es quien decide si está listo.
    Cada paciente puede tener diferentes órdenes (1, 2, 3 o más terapias).
    """
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Verificar que el usuario tenga permisos (staff o asesor)
    if not request.user.is_staff:
        messages.error(request, 'No tiene permisos para realizar esta acción.')
        return redirect('procedimientos:pacientes_pendientes_valoracion')
    
    try:
        with transaction.atomic():
            # Contar valoraciones (solo para el mensaje)
            total_valoraciones = ValoracionProfesional.objects.filter(
                paciente=paciente
            ).count()
            
            # Cambiar estado - SIN VALIDAR si tiene o no valoraciones
            # El asesor ya verificó que las valoraciones requeridas están completas
            paciente.estado = 'PENDIENTE_ASIGNACION'
            paciente.save()
            
            # Mensaje de éxito
            if total_valoraciones > 0:
                messages.success(
                    request,
                    f'✅ {paciente.nombre_completo} marcado como valorado. '
                    f'Valoraciones registradas: {total_valoraciones}. '
                    f'Ahora puede asignarlo a grupos terapéuticos.'
                )
            else:
                messages.success(
                    request,
                    f'✅ {paciente.nombre_completo} marcado como valorado. '
                    f'Ahora puede asignarlo a grupos terapéuticos.'
                )
            
    except Exception as e:
        messages.error(request, f'Error al cambiar estado: {str(e)}')
    
    return redirect('procedimientos:pacientes_pendientes_valoracion')
