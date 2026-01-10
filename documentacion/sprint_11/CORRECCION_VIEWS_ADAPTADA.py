# CORRECCIONES ADAPTADAS AL VIEWS.PY EXISTENTE
# Archivo: apps/grupos/views.py

# ============================================================================
# 1. CORREGIR FUNCIÓN EXISTENTE asignar_paciente_grupo (línea ~101)
# ============================================================================

# BUSCAR esta sección:
            if exito:
                messages.success(request, mensaje)
                return redirect('grupos:grupo_detail', pk=grupo.pk)
            else:
                messages.error(request, mensaje)

# AGREGAR DESPUÉS de "if exito:" y ANTES de "messages.success":

            # ✅ CAMBIAR ESTADO DEL PACIENTE A ACTIVO
            if paciente.estado in ['ADMITIDO', 'PENDIENTE_VALORACION', 'PENDIENTE_ASIGNACION']:
                paciente.estado = Paciente.Estado.ACTIVO
                paciente.save(update_fields=['estado'])

# Resultado final debe ser:
            if exito:
                # ✅ CAMBIAR ESTADO DEL PACIENTE A ACTIVO
                if paciente.estado in ['ADMITIDO', 'PENDIENTE_VALORACION', 'PENDIENTE_ASIGNACION']:
                    paciente.estado = Paciente.Estado.ACTIVO
                    paciente.save(update_fields=['estado'])
                
                messages.success(request, mensaje)
                return redirect('grupos:grupo_detail', pk=grupo.pk)
            else:
                messages.error(request, mensaje)


# ============================================================================
# 2. AGREGAR NUEVAS FUNCIONES AL FINAL DEL ARCHIVO
# ============================================================================

@login_required
def paciente_grupos(request, paciente_id):
    """Ver y gestionar los grupos asignados a un paciente."""
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Asignaciones actuales
    asignaciones = AsignacionGrupo.objects.filter(
        paciente=paciente,
        estado='ACTIVA'
    ).select_related('grupo', 'asignado_por').order_by('-fecha_inicio_asignacion')
    
    # Grupos disponibles (no asignados aún)
    grupos_asignados_ids = asignaciones.values_list('grupo_id', flat=True)
    grupos_disponibles = GrupoTerapeutico.objects.exclude(
        id__in=grupos_asignados_ids
    ).filter(activo=True, cupos_disponibles__gt=0)
    
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
