"""
Vistas para gestión de grupos terapéuticos.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import GrupoTerapeutico, AsignacionGrupo, PacientePendiente
from apps.procedimientos.models import Paciente, ValoracionInicial
from django.utils import timezone
from apps.ml_models.predictor import GrupoRecomendador

from .forms import (
    GrupoTerapeuticoForm,
    AsignacionGrupoForm,
    PacientePendienteForm,
    BuscarGrupoForm
)

from .utils import (
    asignar_paciente_a_grupo,
    marcar_paciente_pendiente,
    liberar_cupo_paciente,
    obtener_estadisticas_grupos,
    obtener_pacientes_sin_grupo
)


@login_required
def grupo_lista(request):
    """Lista de grupos terapéuticos"""
    grupos = GrupoTerapeutico.objects.filter(activo=True).order_by('hora_inicio')
    
    # Filtros
    buscar = request.GET.get('buscar', '')
    if buscar:
        grupos = grupos.filter(
            Q(nombre__icontains=buscar) |
            Q(descripcion__icontains=buscar)
        )
    
    context = {
        'grupos': grupos,
        'estadisticas': obtener_estadisticas_grupos(),
    }
    return render(request, 'grupos/grupo_list.html', context)


@login_required
def grupo_detalle(request, pk):
    """Detalle de un grupo terapéutico"""
    grupo = get_object_or_404(GrupoTerapeutico, pk=pk)
    asignaciones = grupo.asignaciones.filter(estado='ACTIVA').order_by('paciente__apellidos')
    
    context = {
        'grupo': grupo,
        'asignaciones': asignaciones,
    }
    return render(request, 'grupos/grupo_detail.html', context)


@login_required
def grupo_crear(request):
    """Crear nuevo grupo terapéutico"""
    if request.method == 'POST':
        form = GrupoTerapeuticoForm(request.POST)
        if form.is_valid():
            grupo = form.save()
            messages.success(request, f'Grupo "{grupo.nombre}" creado exitosamente.')
            return redirect('grupos:grupo_detail', pk=grupo.pk)
    else:
        form = GrupoTerapeuticoForm()
    
    context = {'form': form, 'titulo': 'Crear Grupo Terapéutico'}
    return render(request, 'grupos/grupo_form.html', context)


@login_required
def grupo_editar(request, pk):
    """Editar grupo terapéutico"""
    grupo = get_object_or_404(GrupoTerapeutico, pk=pk)
    
    if request.method == 'POST':
        form = GrupoTerapeuticoForm(request.POST, instance=grupo)
        if form.is_valid():
            form.save()
            messages.success(request, f'Grupo "{grupo.nombre}" actualizado.')
            return redirect('grupos:grupo_detail', pk=grupo.pk)
    else:
        form = GrupoTerapeuticoForm(instance=grupo)
    
    context = {
        'form': form,
        'grupo': grupo,
        'titulo': f'Editar {grupo.nombre}'
    }
    return render(request, 'grupos/grupo_form.html', context)


@login_required
def asignar_paciente_grupo(request, paciente_pk=None, grupo_id=None):
    """Asignar paciente a un grupo"""
    if request.method == 'POST':
        form = AsignacionGrupoForm(request.POST)
        if form.is_valid():
            paciente = form.cleaned_data['paciente']
            grupo = form.cleaned_data['grupo']
            dias = form.cleaned_data['dias_asistencia']
            num_terapias = form.cleaned_data['numero_terapias_semanales']
            notas = form.cleaned_data.get('notas', '')
            
            asignacion, exito, mensaje = asignar_paciente_a_grupo(
                paciente=paciente,
                grupo=grupo,
                dias_asistencia=dias,
                numero_terapias=num_terapias,
                notas=notas
            )
            
            if exito:
                if paciente.estado in ['ADMITIDO', 'PENDIENTE_VALORACION', 'PENDIENTE_ASIGNACION']:
                    paciente.estado = Paciente.Estado.ACTIVO
                    paciente.save(update_fields=['estado'])

                messages.success(request, mensaje)
                return redirect('grupos:grupo_detail', pk=grupo.pk)
            else:
                messages.error(request, mensaje)
    else:
        initial = {}
        if paciente_pk:
            initial['paciente'] = paciente_pk
        if grupo_id:
            initial['grupo'] = grupo_id
        form = AsignacionGrupoForm(initial=initial)
    
    context = {
        'form': form,
        'titulo': 'Asignar Paciente a Grupo'
    }
    return render(request, 'grupos/asignacion_form.html', context)


@login_required
def pacientes_pendientes_lista(request):
    """Lista de pacientes pendientes de asignación"""
    pendientes = PacientePendiente.objects.filter(
        estado__in=['PENDIENTE','ADMITIDO', 'PENDIENTE_ASIGNACION', 'ACTIVO']
    ).order_by('-prioridad', 'fecha_solicitud')
    
    # Filtros
    prioridad = request.GET.get('prioridad', '')
    if prioridad:
        pendientes = pendientes.filter(prioridad=prioridad)
    
    context = {
        'pendientes': pendientes,
        'total_pendientes': pendientes.count(),
    }
    return render(request, 'grupos/pacientes_pendientes.html', context)


@login_required
def dashboard_grupos(request):
    """Dashboard de grupos con estadísticas"""
    estadisticas = obtener_estadisticas_grupos()
    grupos_recientes = GrupoTerapeutico.objects.filter(activo=True)[:5]
    pacientes_sin_grupo = obtener_pacientes_sin_grupo()[:10]
    pendientes = PacientePendiente.objects.filter(estado='PENDIENTE')[:10]
    
    context = {
        'estadisticas': estadisticas,
        'grupos_recientes': grupos_recientes,
        'pacientes_sin_grupo': pacientes_sin_grupo,
        'pendientes': pendientes,
    }
    return render(request, 'grupos/dashboard.html', context)


@login_required
def liberar_paciente(request, asignacion_pk):
    """Liberar cupo de un paciente"""
    asignacion = get_object_or_404(AsignacionGrupo, pk=asignacion_pk)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', 'Liberación manual')
        asignacion.finalizar(motivo=motivo)
        messages.success(
            request,
            f'Cupo liberado para {asignacion.paciente.nombres} {asignacion.paciente.apellidos}'
        )
        return redirect('grupos:grupo_detail', pk=asignacion.grupo.pk)
    
    context = {'asignacion': asignacion}
    return render(request, 'grupos/liberar_confirm.html', context)


# apps/grupos/views.py

@login_required
def asignar_paciente_grupos(request, paciente_id):
    """
    Permite asignar un paciente a múltiples grupos.
    Solo para pacientes en estado PENDIENTE_ASIGNACION.
    """
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Verificar que tenga valoración
    if not hasattr(paciente, 'valoracion_inicial'):
        messages.error(request, 'El paciente debe tener una valoración inicial.')
        return redirect('procedimientos:paciente_detail', pk=paciente_id)
    
    if paciente.estado != Paciente.Estado.PENDIENTE_ASIGNACION:
        messages.warning(request, 'El paciente no está en estado pendiente de asignación.')
    
    if request.method == 'POST':
        # Procesar múltiples asignaciones
        grupos_ids = request.POST.getlist('grupos')
        terapias_nums = request.POST.getlist('numero_terapias')
        
        for grupo_id, num_terapias in zip(grupos_ids, terapias_nums):
            AsignacionGrupo.objects.create(
                paciente=paciente,
                grupo_id=grupo_id,
                numero_terapias_asignadas=int(num_terapias),
                fecha_inicio_asignacion=timezone.now().date(),
                asignado_por=request.user
            )
        
        # Cambiar estado a ACTIVO
        paciente.estado = Paciente.Estado.ACTIVO
        paciente.save(update_fields=['estado'])
        
        messages.success(request, f'Paciente asignado a {len(grupos_ids)} grupo(s)')
        return redirect('procedimientos:paciente_detail', pk=paciente_id)
    
    # Obtener grupos disponibles y valoración
    grupos_disponibles = GrupoTerapeutico.objects.filter(activo=True, cupos_disponibles__gt=0)
    valoracion = paciente.valoracion_inicial
    
    context = {
        'paciente': paciente,
        'valoracion': valoracion,
        'grupos_disponibles': grupos_disponibles
    }
    
    return render(request, 'grupos/asignar_multiples_grupos.html', context)


@login_required
def paciente_grupos(request, paciente_id):
    """Ver y gestionar los grupos asignados a un paciente."""
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Asignaciones actuales
    asignaciones = AsignacionGrupo.objects.filter(
        paciente=paciente,
        estado='ACTIVA'
    ).select_related('grupo').order_by('-fecha_inicio_asignacion')
    
    # Grupos disponibles (no asignados aún)
    grupos_asignados_ids = asignaciones.values_list('grupo_id', flat=True)
    grupos_disponibles = GrupoTerapeutico.objects.exclude(
        id__in=grupos_asignados_ids
    ).filter(activo=True)

    # Filtrar en Python los que tienen cupos (si es propiedad calculada)
    grupos_disponibles = [g for g in grupos_disponibles if g.cupos_disponibles > 0]
    
    context = {
        'paciente': paciente,
        'asignaciones': asignaciones,
        'grupos_disponibles': grupos_disponibles,
        'total_terapias': sum(a.numero_terapias_asignadas for a in asignaciones),
    }
    return render(request, 'grupos/paciente_grupos.html', context)


@login_required
def agregar_grupo_paciente(request, paciente_id):
    """Agregar un grupo adicional al paciente."""
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    if request.method == 'POST':
        grupo_id = request.POST.get('grupo')
        grupo = get_object_or_404(GrupoTerapeutico, pk=grupo_id)
        
        # Verificar que no esté ya asignado
        if AsignacionGrupo.objects.filter(
            paciente=paciente, 
            grupo=grupo, 
            estado='ACTIVA'
        ).exists():
            messages.warning(request, 'El paciente ya está asignado a este grupo')
            return redirect('grupos:paciente_grupos', paciente_id=paciente_id)
        
        # Crear asignación usando la función de utilidad
        dias = request.POST.getlist('dias_asistencia')
        num_terapias = int(request.POST.get('numero_terapias_asignadas', 10))
        
        asignacion, exito, mensaje = asignar_paciente_a_grupo(
            paciente=paciente,
            grupo=grupo,
            dias_asistencia=dias,
            numero_terapias=num_terapias,
            notas=''
        )
        
        if exito:
            # Asegurar que esté ACTIVO
            if paciente.estado != 'ACTIVO':
                paciente.estado = Paciente.Estado.ACTIVO
                paciente.save(update_fields=['estado'])
            
            messages.success(request, f'Grupo {grupo.nombre} agregado exitosamente')
        else:
            messages.error(request, mensaje)
        
        return redirect('grupos:paciente_grupos', paciente_id=paciente_id)
    
    return redirect('grupos:paciente_grupos', paciente_id=paciente_id)


@login_required
def eliminar_asignacion_grupo(request, asignacion_id):
    """Eliminar una asignación de grupo."""
    asignacion = get_object_or_404(AsignacionGrupo, pk=asignacion_id)
    paciente = asignacion.paciente
    
    if request.method == 'POST':
        # Finalizar asignación (método existente del modelo)
        motivo = request.POST.get('motivo', 'Eliminación manual')
        asignacion.finalizar(motivo=motivo)
        
        # Si no quedan asignaciones activas, cambiar estado
        asignaciones_activas = AsignacionGrupo.objects.filter(
            paciente=paciente, 
            estado='ACTIVA'
        ).count()
        
        if asignaciones_activas == 0:
            paciente.estado = Paciente.Estado.PENDIENTE_ASIGNACION
            paciente.save(update_fields=['estado'])
            messages.info(request, 'Asignación eliminada. Paciente vuelve a Pendiente Asignación')
        else:
            messages.success(request, 'Asignación eliminada exitosamente')
        
        return redirect('grupos:paciente_grupos', paciente_id=paciente.id)
    
    return redirect('grupos:paciente_grupos', paciente_id=paciente.id)


@login_required
def cambiar_grupo_paciente(request, asignacion_id):
    """Cambiar un paciente de un grupo a otro."""
    asignacion = get_object_or_404(AsignacionGrupo, pk=asignacion_id)
    paciente = asignacion.paciente
    
    if request.method == 'POST':
        nuevo_grupo_id = request.POST.get('nuevo_grupo')
        nuevo_grupo = get_object_or_404(GrupoTerapeutico, pk=nuevo_grupo_id)
        
        # Verificar que no esté ya en ese grupo
        if AsignacionGrupo.objects.filter(
            paciente=paciente, 
            grupo=nuevo_grupo, 
            estado='ACTIVA'
        ).exists():
            messages.warning(request, 'El paciente ya está en ese grupo')
            return redirect('grupos:paciente_grupos', paciente_id=paciente.id)
        
        # Finalizar asignación actual
        grupo_anterior = asignacion.grupo
        asignacion.finalizar(motivo=f'Cambio a {nuevo_grupo.nombre}')
        
        # Crear nueva asignación
        asignar_paciente_a_grupo(
            paciente=paciente,
            grupo=nuevo_grupo,
            dias_asistencia=asignacion.dias_asistencia,
            numero_terapias=asignacion.numero_terapias_asignadas,
            notas=f'Cambiado desde {grupo_anterior.nombre}'
        )
        
        messages.success(request, f'Paciente cambiado de {grupo_anterior.nombre} a {nuevo_grupo.nombre}')
        return redirect('grupos:paciente_grupos', paciente_id=paciente.id)
    
    return redirect('grupos:paciente_grupos', paciente_id=paciente.id)


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
    valoracion = ValoracionInicial.objects.filter(
        paciente=paciente
    ).order_by('-fecha_valoracion').first()
    
    # Si no hay valoración, redirigir con warning
    if not valoracion:
        messages.warning(
            request, 
            f'El paciente {paciente.nombre_completo} no tiene valoración inicial. '
            'Por favor complete la valoración antes de solicitar recomendaciones.'
        )
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
    
    valoracion = ValoracionInicial.objects.filter(
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
            return redirect(
                            'grupos:agregar_lista_espera', 
                            paciente_id=paciente_id, 
                            grupo_id=grupo_id
                        )
    
    # Redirigir a la vista de asignación normal
    return redirect(
                    'grupos:asignar_paciente_especifico', 
                    paciente_pk=paciente_id, 
                    grupo_id=grupo_id
                )


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
    valoracion = ValoracionInicial.objects.filter(
        paciente=paciente
    ).order_by('-fecha_valoracion').first()
    
    if not valoracion:
        messages.error(request, 'No hay valoración disponible')
        return redirect('procedimientos:paciente_detail', paciente_id=paciente_id)
    
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
    p.drawString(50, y, f"Edad: {paciente.edad_actual} años")
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




