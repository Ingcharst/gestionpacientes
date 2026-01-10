# NUEVAS VISTAS: Gestión de múltiples grupos por paciente
# Archivo: apps/grupos/views.py (AGREGAR AL FINAL)

from django.db.models import Count, Q

@login_required
def paciente_grupos(request, paciente_id):
    """Ver y gestionar los grupos asignados a un paciente."""
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Asignaciones actuales
    asignaciones = AsignacionGrupo.objects.filter(
        paciente=paciente
    ).select_related('grupo', 'asignado_por').order_by('-fecha_inicio_asignacion')
    
    # Grupos disponibles (no asignados aún)
    grupos_asignados_ids = asignaciones.values_list('grupo_id', flat=True)
    grupos_disponibles = GrupoTerapeutico.objects.exclude(
        id__in=grupos_asignados_ids
    ).filter(activo=True)
    
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
        if AsignacionGrupo.objects.filter(paciente=paciente, grupo=grupo).exists():
            messages.warning(request, 'El paciente ya está asignado a este grupo')
            return redirect('grupos:paciente_grupos', paciente_id=paciente_id)
        
        # Crear asignación
        AsignacionGrupo.objects.create(
            paciente=paciente,
            grupo=grupo,
            numero_terapias_asignadas=request.POST.get('numero_terapias_asignadas', 10),
            fecha_inicio_asignacion=timezone.now().date(),
            asignado_por=request.user,
            dias_asistencia=request.POST.getlist('dias_asistencia')
        )
        
        # Asegurar que esté ACTIVO
        if paciente.estado != 'ACTIVO':
            paciente.estado = Paciente.Estado.ACTIVO
            paciente.save(update_fields=['estado'])
        
        messages.success(request, f'Grupo {grupo.nombre} agregado exitosamente')
        return redirect('grupos:paciente_grupos', paciente_id=paciente_id)
    
    return redirect('grupos:paciente_grupos', paciente_id=paciente_id)


@login_required
def eliminar_asignacion(request, asignacion_id):
    """Eliminar una asignación de grupo."""
    asignacion = get_object_or_404(AsignacionGrupo, pk=asignacion_id)
    paciente = asignacion.paciente
    
    if request.method == 'POST':
        asignacion.delete()
        
        # Si no quedan asignaciones, cambiar estado
        if not AsignacionGrupo.objects.filter(paciente=paciente).exists():
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
        if AsignacionGrupo.objects.filter(paciente=paciente, grupo=nuevo_grupo).exists():
            messages.warning(request, 'El paciente ya está en ese grupo')
            return redirect('grupos:paciente_grupos', paciente_id=paciente.id)
        
        # Actualizar asignación
        grupo_anterior = asignacion.grupo
        asignacion.grupo = nuevo_grupo
        asignacion.fecha_inicio_asignacion = timezone.now().date()
        asignacion.save()
        
        messages.success(request, f'Paciente cambiado de {grupo_anterior.nombre} a {nuevo_grupo.nombre}')
        return redirect('grupos:paciente_grupos', paciente_id=paciente.id)
    
    return redirect('grupos:paciente_grupos', paciente_id=paciente.id)
