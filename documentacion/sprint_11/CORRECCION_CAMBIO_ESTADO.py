# CORRECCIÓN: Cambio de estado al asignar grupo
# Archivo: apps/grupos/views.py

# BUSCAR la vista de asignación y MODIFICAR:

@login_required
def asignar_paciente_grupo(request, grupo_id):
    grupo = get_object_or_404(GrupoTerapeutico, pk=grupo_id)
    
    if request.method == 'POST':
        paciente_id = request.POST.get('paciente')
        paciente = get_object_or_404(Paciente, pk=paciente_id)
        
        # Crear asignación
        asignacion = AsignacionGrupo.objects.create(
            paciente=paciente,
            grupo=grupo,
            numero_terapias_asignadas=request.POST.get('numero_terapias_asignadas', 10),
            fecha_inicio_asignacion=timezone.now().date(),
            asignado_por=request.user
        )
        
        # Guardar días de asistencia
        dias = request.POST.getlist('dias_asistencia')
        if dias:
            asignacion.dias_asistencia = dias
            asignacion.save(update_fields=['dias_asistencia'])
        
        # ✅ CAMBIAR ESTADO DEL PACIENTE A ACTIVO
        if paciente.estado in ['ADMITIDO', 'PENDIENTE_VALORACION', 'PENDIENTE_ASIGNACION']:
            paciente.estado = Paciente.Estado.ACTIVO
            paciente.save(update_fields=['estado'])
        
        messages.success(request, f'Paciente {paciente.nombre_completo} asignado exitosamente')
        return redirect('grupos:grupo_detail', pk=grupo_id)
    
    # Filtrar pacientes disponibles
    pacientes = Paciente.objects.filter(
        estado__in=['ADMITIDO', 'PENDIENTE_ASIGNACION', 'ACTIVO']
    ).order_by('nombres', 'apellidos')
    
    context = {
        'grupo': grupo,
        'pacientes': pacientes
    }
    return render(request, 'grupos/asignar_paciente.html', context)
