"""
Vista Django para Recomendaciones de Grupos
VERSIÓN CORREGIDA - Fix NoReverseMatch
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.procedimientos.models import Paciente, Valoracion
from apps.grupos.models import GrupoTerapeutico
from apps.ml_models.predictor import GrupoRecomendador


@login_required
def recomendar_grupos_paciente(request, paciente_id):
    """
    Vista principal: Muestra recomendaciones de grupos para un paciente
    
    Args:
        request: HttpRequest
        paciente_id: ID del paciente
        
    Returns:
        HttpResponse con template de recomendaciones
    """
    # Obtener paciente
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Obtener última valoración
    valoracion = Valoracion.objects.filter(
        paciente=paciente
    ).order_by('-fecha_valoracion').first()
    
    # Si no hay valoración, redirigir con warning
    if not valoracion:
        messages.warning(
            request, 
            f'El paciente {paciente.nombre_completo} no tiene valoración inicial. '
            'Por favor complete la valoración antes de solicitar recomendaciones.'
        )
        # CORRECCIÓN: Usar 'pk' en lugar de 'paciente_id'
        return redirect('procedimientos:paciente_detail', pk=paciente_id)
    
    # Crear recomendador
    recomendador = GrupoRecomendador()
    
    # Obtener recomendaciones
    resultado = recomendador.recomendar_grupos(
        paciente=paciente,
        valoracion=valoracion,
        top_n=5
    )
    
    # Preparar contexto
    context = {
        'paciente': paciente,
        'valoracion': valoracion,
        'recomendaciones': resultado['recomendaciones'],
        'mensaje': resultado['mensaje'],
        'total_evaluados': resultado.get('total_grupos_evaluados', 0),
        'total_compatibles': resultado.get('grupos_filtrados', 0),
        'mostrar_debug': request.user.is_staff,  # Solo para admins
    }
    
    return render(request, 'grupos/recomendaciones.html', context)


@login_required
def debug_recomendacion(request, paciente_id, grupo_id):
    """
    Vista de debug: Muestra detalles completos de una recomendación
    Solo para staff/admins
    
    Args:
        request: HttpRequest
        paciente_id: ID del paciente
        grupo_id: ID del grupo
        
    Returns:
        JsonResponse con detalles
    """
    from django.http import JsonResponse
    
    # Verificar que sea staff
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    # Obtener objetos
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    grupo = get_object_or_404(GrupoTerapeutico, pk=grupo_id)
    
    valoracion = Valoracion.objects.filter(
        paciente=paciente
    ).order_by('-fecha_valoracion').first()
    
    # Crear recomendador y obtener debug
    recomendador = GrupoRecomendador()
    debug_info = recomendador.debug_recomendacion(paciente, grupo, valoracion)
    
    return JsonResponse(debug_info, safe=False)


@login_required
def asignar_desde_recomendacion(request, paciente_id, grupo_id):
    """
    Asigna un paciente a un grupo desde las recomendaciones
    
    Args:
        request: HttpRequest
        paciente_id: ID del paciente
        grupo_id: ID del grupo
        
    Returns:
        Redirect a la vista de confirmación de asignación
    """
    # Verificar que el grupo tenga cupos
    grupo = get_object_or_404(GrupoTerapeutico, pk=grupo_id)
    
    if grupo.cupos_disponibles <= 0:
        messages.warning(
            request,
            f'El grupo {grupo.nombre} no tiene cupos disponibles actualmente. '
            'Puede agregarlo a la lista de espera.'
        )
        # Redirigir a lista de espera si existe
        if hasattr(grupo, 'lista_espera'):
            return redirect('grupos:agregar_lista_espera', 
                          paciente_id=paciente_id, 
                          grupo_id=grupo_id)
    
    # Redirigir a la vista de asignación normal
    # NOTA: Ajustar según tu URL pattern de asignación
    return redirect('grupos:asignar_paciente_grupo', 
                   paciente_id=paciente_id, 
                   grupo_id=grupo_id)


@login_required
def exportar_recomendaciones(request, paciente_id):
    """
    Exporta las recomendaciones a PDF
    
    Args:
        request: HttpRequest
        paciente_id: ID del paciente
        
    Returns:
        HttpResponse con PDF
    """
    from django.http import HttpResponse
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    import io
    
    # Obtener paciente y recomendaciones
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    valoracion = Valoracion.objects.filter(
        paciente=paciente
    ).order_by('-fecha_valoracion').first()
    
    if not valoracion:
        messages.error(request, 'No hay valoración disponible')
        # CORRECCIÓN: Usar 'pk' en lugar de 'paciente_id'
        return redirect('procedimientos:paciente_detail', pk=paciente_id)
    
    recomendador = GrupoRecomendador()
    resultado = recomendador.recomendar_grupos(
        paciente=paciente,
        valoracion=valoracion,
        top_n=5
    )
    
    # Crear PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Recomendaciones de Grupos - {paciente.nombre_completo}")
    
    # Información del paciente
    p.setFont("Helvetica", 12)
    y = height - 80
    p.drawString(50, y, f"Edad: {paciente.edad} años")
    y -= 20
    p.drawString(50, y, f"Valoración: {valoracion.fecha_valoracion.strftime('%d/%m/%Y')}")
    y -= 40
    
    # Recomendaciones
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Grupos Recomendados:")
    y -= 30
    
    for i, rec in enumerate(resultado['recomendaciones'], 1):
        grupo = rec['grupo']
        score = rec['score']
        
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, f"{i}. {grupo.nombre} - {score}% Match")
        y -= 20
        
        p.setFont("Helvetica", 10)
        p.drawString(70, y, f"Terapia: {grupo.terapia.nombre}")
        y -= 15
        p.drawString(70, y, f"Edad: {grupo.edad_minima}-{grupo.edad_maxima} años")
        y -= 15
        p.drawString(70, y, f"Cupos: {grupo.cupos_disponibles}")
        y -= 25
        
        # Razones
        p.setFont("Helvetica-Oblique", 9)
        for razon in rec['razones'][:3]:  # Solo primeras 3
            if y < 100:  # Nueva página si es necesario
                p.showPage()
                y = height - 50
            p.drawString(70, y, f"• {razon}")
            y -= 12
        
        y -= 20
        
        if y < 150:  # Nueva página
            p.showPage()
            y = height - 50
    
    # Finalizar PDF
    p.showPage()
    p.save()
    
    # Retornar PDF
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recomendaciones_{paciente_id}.pdf"'
    
    return response