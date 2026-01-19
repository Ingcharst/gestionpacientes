"""
Vistas para procedimientos (frontend).
"""
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg, Exists, OuterRef
from django.utils import timezone
from django.db import transaction
from datetime import date, timedelta

from apps.terapias.models import Terapia
from apps.grupos.models import AsignacionGrupo
from .models import (
    Paciente, Procedimiento, SesionTerapeutica,
    ObjetivoTerapeutico, EvolucionPaciente, ValoracionInicial, CodigoCIE10,
    ValoracionProfesional, AdmisionTerapia
)
from .forms import (
    AdmisionPacienteForm, PacienteForm, ProblemaDetectadoForm, ProcedimientoForm, SesionTerapeuticaForm,
    ObjetivoTerapeuticoForm, EvolucionPacienteForm, ValoracionInicialForm,
    PacienteRegistroForm, ValoracionProfesionalForm, AdmisionTerapiaForm
)


@login_required
def paciente_lista(request):
    """Lista de pacientes."""
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    
    pacientes = Paciente.objects.all()
    
    if query:
        pacientes = pacientes.filter(
            Q(nombres__icontains=query) |
            Q(apellidos__icontains=query) |
            Q(numero_documento__icontains=query) |
            Q(numero_historia_clinica__icontains=query) |
            Q(numero_admision__icontains=query)
        )
    
    if estado:
        pacientes = pacientes.filter(estado=estado)
    
    pacientes = pacientes.order_by('-fecha_ingreso')
    
    context = {
        'pacientes': pacientes,
        'query': query,
        'estado_seleccionado': estado,
        'estados': Paciente.Estado.choices,
    }
    
    return render(request, 'procedimientos/paciente_lista.html', context)


@login_required
def paciente_detalle(request, pk):
    """Detalle de un paciente."""
    paciente = get_object_or_404(Paciente, pk=pk)
    
    # Obtener información relacionada
    procedimientos = paciente.procedimientos.all()[:10]
    sesiones = paciente.sesiones.all()[:10]
    objetivos = paciente.objetivos_terapeuticos.all()
    evoluciones = EvolucionPaciente.objects.filter(
        paciente=paciente
    ).select_related('profesional', 'terapia', 'grupo').order_by('-fecha_sesion')[:10]
    
    admisiones_vigentes = AdmisionTerapia.objects.filter(
        paciente=paciente,
        estado='VIGENTE'
    ).count()    
    
    context = {
        'paciente': paciente,
        'procedimientos': procedimientos,
        'sesiones': sesiones,
        'objetivos': objetivos,
        'evoluciones': evoluciones,
        'admisiones_vigentes': admisiones_vigentes,
    }
    
    return render(request, 'procedimientos/paciente_detalle.html', context)



@login_required
def paciente_crear(request):
    """Crear un nuevo paciente."""
    if request.method == 'POST':
        form = PacienteForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                paciente = form.save()
                messages.success(request, f'Paciente {paciente.nombre_completo} creado exitosamente.')
                return redirect('procedimientos:paciente_detail', pk=paciente.pk)
            except Exception as e:
                messages.error(request, f'Error al guardar el paciente: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
            messages.error(request, form.errors.as_json())
    else:
        form = PacienteForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Paciente',
        'object': None  # Importante: para el template
    }
    return render(request, 'procedimientos/paciente_form.html', context)



@login_required
def paciente_editar(request, pk):
    """Editar un paciente."""
    paciente = get_object_or_404(Paciente, pk=pk)
    
    if request.method == 'POST':
        form = PacienteForm(request.POST, request.FILES, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, f'Paciente {paciente.nombre_completo} actualizado exitosamente.')
            return redirect('procedimientos:paciente_detail', pk=paciente.pk)
    else:
        form = PacienteForm(instance=paciente)
    
    context = {
        'form': form,
        'paciente': paciente,
        'titulo': f'Editar Paciente: {paciente.nombre_completo}'
    }
    return render(request, 'procedimientos/paciente_form.html', context)


@login_required
def sesion_lista(request):
    """Lista de sesiones terapéuticas."""
    fecha = request.GET.get('fecha', '')
    estado = request.GET.get('estado', '')
    paciente_id = request.GET.get('paciente', '')
    
    sesiones = SesionTerapeutica.objects.select_related('paciente', 'terapeuta', 'terapia')
    
    if fecha:
        sesiones = sesiones.filter(fecha=fecha)
    
    if estado:
        sesiones = sesiones.filter(estado=estado)
    
    if paciente_id:
        sesiones = sesiones.filter(paciente_id=paciente_id)
    
    sesiones = sesiones.order_by('-fecha', '-hora_inicio')
    
    context = {
        'sesiones': sesiones,
        'fecha_seleccionada': fecha,
        'estado_seleccionado': estado,
        'estados': SesionTerapeutica.Estado.choices,
    }
    
    return render(request, 'procedimientos/sesion_lista.html', context)


@login_required
def sesion_detalle(request, pk):
    """Detalle de una sesión."""
    sesion = get_object_or_404(SesionTerapeutica, pk=pk)
    
    context = {'sesion': sesion}
    return render(request, 'procedimientos/sesion_detalle.html', context)


@login_required
def sesion_crear(request):
    """Crear una nueva sesión."""
    if request.method == 'POST':
        form = SesionTerapeuticaForm(request.POST)
        if form.is_valid():
            try:
                sesion = form.save(commit=False)
                sesion.creado_por = request.user
                sesion.save()
                messages.success(request, f'Sesión creada exitosamente.')
                return redirect('procedimientos:sesion_list')
            except Exception as e:
                messages.error(request, f'Error al guardar la sesión: {str(e)}')
        else:
            # Mostrar errores de validación
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = SesionTerapeuticaForm()
    
    context = {'form': form, 'titulo': 'Crear Sesión Terapéutica'}
    return render(request, 'procedimientos/sesion_form.html', context)


@login_required
def sesion_editar(request, pk):
    """Editar una sesión."""
    sesion = get_object_or_404(SesionTerapeutica, pk=pk)
    
    if request.method == 'POST':
        form = SesionTerapeuticaForm(request.POST, instance=sesion)
        if form.is_valid():
            form.save()
            messages.success(request, f'Sesión {sesion.numero_sesion} actualizada exitosamente.')
            return redirect('procedimientos:sesion_detalle', pk=sesion.pk)
    else:
        form = SesionTerapeuticaForm(instance=sesion)
    
    context = {
        'form': form,
        'sesion': sesion,
        'titulo': f'Editar Sesión: {sesion.numero_sesion}'
    }
    return render(request, 'procedimientos/sesion_form.html', context)


@login_required
def dashboard(request):
    """Dashboard principal de procedimientos."""
    # Estadísticas generales
    total_pacientes = Paciente.objects.count()
    pacientes_activos = Paciente.objects.filter(estado='ACTIVO').count()
    
    # Sesiones de hoy
    hoy = timezone.now().date()
    sesiones_hoy = SesionTerapeutica.objects.filter(fecha=hoy).count()
    
    # Procedimientos pendientes
    procedimientos_programados = Procedimiento.objects.filter(estado='PROGRAMADO').count()
    
    # Pacientes pendientes de grupo
    from apps.grupos.models import PacientePendiente
    pacientes_pendientes_grupo = PacientePendiente.objects.filter(
        estado='PENDIENTE'
    ).count()
    
    # Últimas sesiones
    ultimas_sesiones = SesionTerapeutica.objects.select_related(
        'paciente', 'terapeuta', 'terapia'
    ).order_by('-fecha', '-hora_inicio')[:5]
    
    # Pacientes recientes
    pacientes_recientes = Paciente.objects.order_by('-fecha_ingreso')[:5]
    
    context = {
        'total_pacientes': total_pacientes,
        'pacientes_activos': pacientes_activos,
        'sesiones_hoy': sesiones_hoy,
        'procedimientos_programados': procedimientos_programados,
        'pacientes_pendientes_grupo': pacientes_pendientes_grupo,
        'ultimas_sesiones': ultimas_sesiones,
        'pacientes_recientes': pacientes_recientes,
    }
    
    return render(request, 'procedimientos/dashboard.html', context)


@login_required
def procedimiento_lista(request):
    """Lista de procedimientos."""
    procedimientos = Procedimiento.objects.select_related(
        'paciente', 'profesional', 'consultorio'
    ).order_by('-fecha', '-hora_inicio')
    
    context = {'procedimientos': procedimientos}
    return render(request, 'procedimientos/lista.html', context)


@login_required
def procedimiento_crear(request):
    """Crear un nuevo procedimiento."""
    if request.method == 'POST':
        form = ProcedimientoForm(request.POST)
        if form.is_valid():
            try:
                procedimiento = form.save(commit=False)
                procedimiento.creado_por = request.user
                procedimiento.save()
                messages.success(request, 'Procedimiento creado exitosamente.')
                return redirect('procedimientos:procedimiento_list')
            except Exception as e:
                messages.error(request, f'Error al guardar el procedimiento: {str(e)}')
        else:
            # Mostrar errores de validación
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProcedimientoForm()
    
    context = {'form': form, 'titulo': 'Crear Procedimiento'}
    return render(request, 'procedimientos/form.html', context)



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
                    paciente.estado = Paciente.Estado.ADMITIDO 
                    
                    # Guardar paciente
                    paciente.save()
                    form.save_m2m()
                    
                    messages.success(
                        request,
                        f'Paciente {paciente.nombre_completo} admitido exitosamente. '
                        f'Estado: {paciente.get_estado_display()}. '  # ✅ Mostrar estado
                        f'El paciente está pendiente de valoración inicial.'  # ✅ Informar
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


@login_required
def pacientes_pendientes_asignacion(request):
    """
    Lista de pacientes que han sido valorados por profesionales
    y están pendientes de asignación a grupos terapéuticos.
    
    ✅ ACTUALIZADO: Usa ValoracionProfesional (múltiples valoraciones)
    ✅ CORREGIDO: Compara por terapia_id en vez de objetos
    """
    
    # =========================================================================
    # 1. BUSCAR PACIENTES CON VALORACIONES COMPLETADAS
    # =========================================================================
    
    # Subquery para verificar si tiene valoraciones completadas
    tiene_valoraciones = ValoracionProfesional.objects.filter(
        paciente=OuterRef('pk'),
        estado='COMPLETADA'
    )
    
    # Pacientes con al menos una valoración completada
    pacientes_con_valoraciones = Paciente.objects.annotate(
        tiene_valoraciones_completadas=Exists(tiene_valoraciones),
        total_valoraciones=Count(
            'valoraciones_profesionales',
            filter=Q(valoraciones_profesionales__estado='COMPLETADA')
        )
    ).filter(
        tiene_valoraciones_completadas=True
    )
    
    # =========================================================================
    # 2. FILTRAR POR ESTADO Y SIN ASIGNACIÓN ACTIVA
    # =========================================================================
    
    # Filtrar por estado PENDIENTE_ASIGNACION
    pacientes = pacientes_con_valoraciones.filter(
        estado=Paciente.Estado.PENDIENTE_ASIGNACION
    )
    
    pacientes_ok = pacientes.select_related(
        'codigo_enfermedad'
    ).prefetch_related(
        'valoraciones_profesionales__terapia',
        'valoraciones_profesionales__terapeuta',
        'admisiones__terapia'
    ).order_by('-fecha_ingreso')
    
    # =========================================================================
    # 3. CONSTRUIR DATOS PARA CADA PACIENTE
    # =========================================================================
    
    pacientes_data = []
    
    for paciente in pacientes_ok:
        # Obtener valoraciones completadas
        valoraciones = paciente.valoraciones_profesionales.filter(
            estado='COMPLETADA'
        )
        
        # Obtener admisiones vigentes
        admisiones_vigentes = paciente.admisiones.filter(
            estado='VIGENTE',
            fecha_inicio__lte=date.today() + timedelta(days=7),
            fecha_fin__gte=date.today()
        )
        
        # ✅ CORRECCIÓN: Comparar por IDs de terapia
        terapias_valoradas_ids = set(val.terapia_id for val in valoraciones)
        terapias_con_admision_ids = set(adm.terapia_id for adm in admisiones_vigentes)
        
        falta_admision_ids = terapias_valoradas_ids - terapias_con_admision_ids
        
        # Obtener objetos Terapia únicos para mostrar
        from apps.terapias.models import Terapia
        terapias_recomendadas = Terapia.objects.filter(
            id__in=terapias_valoradas_ids
        )
        
        terapias_falta_admision = Terapia.objects.filter(
            id__in=falta_admision_ids
        )
        
        pacientes_data.append({
            'paciente': paciente,
            'valoraciones': valoraciones,
            'total_valoraciones': valoraciones.count(),
            'terapias_recomendadas': list(terapias_recomendadas),
            'admisiones_vigentes': admisiones_vigentes,
            'falta_admision': list(terapias_falta_admision),
            'tiene_todas_admisiones': len(falta_admision_ids) == 0,
        })
    
    # =========================================================================
    # 4. MENSAJES INFORMATIVOS
    # =========================================================================
    
    if pacientes_data:
        # Contar cuántos están listos para asignar
        listos = sum(1 for p in pacientes_data if p['tiene_todas_admisiones'])
        pendientes = len(pacientes_data) - listos
        
        if listos > 0:
            messages.success(
                request,
                f'✅ {listos} paciente(s) listo(s) para asignación a grupos'
            )
        
        if pendientes > 0:
            messages.warning(
                request,
                f'⚠️ {pendientes} paciente(s) valorado(s) pero sin todas las admisiones de terapia'
            )
    else:
        messages.info(
            request,
            'No hay pacientes pendientes de asignación a grupos'
        )
    
    # =========================================================================
    # 5. RENDERIZAR
    # =========================================================================
    
    context = {
        'pacientes_data': pacientes_data,
        'titulo': 'Pacientes Pendientes de Asignación a Terapias',
    }
    
    return render(request, 'procedimientos/pacientes_pendientes_asignacion.html', context)



# ============================================================================
# VISTA: LISTA CIE10 AJAX
# ============================================================================


@login_required
def buscar_cie10(request):
    """
    Búsqueda AJAX de códigos CIE-10.
    Retorna JSON con resultados.
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    # Buscar en código o descripción
    codigos = CodigoCIE10.objects.filter(
        Q(codigo__icontains=query) |
        Q(descripcion__icontains=query) |
        Q(categoria__icontains=query),
        activo=True
    ).order_by('codigo')[:20]  # Limitar a 20 resultados
    
    results = [
        {
            'id': codigo.id,
            'codigo': codigo.codigo,
            'descripcion': codigo.descripcion,
            'categoria': codigo.categoria,
            'texto_completo': f"{codigo.codigo} - {codigo.descripcion}"
        }
        for codigo in codigos
    ]
    
    return JsonResponse({'results': results})


@login_required
def obtener_cie10(request, codigo_id):
    """
    Obtener un código CIE-10 específico por ID.
    """
    try:
        codigo = CodigoCIE10.objects.get(id=codigo_id)
        return JsonResponse({
            'success': True,
            'codigo': {
                'id': codigo.id,
                'codigo': codigo.codigo,
                'descripcion': codigo.descripcion,
                'categoria': codigo.categoria,
                'texto_completo': str(codigo)
            }
        })
    except CodigoCIE10.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Código no encontrado'
        }, status=404)

# ============================================================================
# VISTA: EVOLUCIÓN PACIENTE
# ============================================================================


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
                return redirect('procedimientos:evoluciones_paciente', paciente_id=evolucion.paciente.id)
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
    # from .models import Terapia
    # terapias = Terapia.objects.filter(evoluciones_paciente=paciente).distinct()
    terapias_ids = EvolucionPaciente.objects.filter(
        paciente=paciente
    ).values_list('terapia_id', flat=True).distinct()

    # Obtener objetos Terapia
    terapias = Terapia.objects.filter(id__in=terapias_ids)
    
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


@login_required
def registrar_paciente(request):
    """Registro simple sin admisión ni historia"""
    if request.method == 'POST':
        form = PacienteRegistroForm(request.POST, request.FILES)
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
                        f'Paciente {paciente.nombre_completo} registrado exitosamente. '
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
        form = PacienteRegistroForm()
    
    context = {
        'form': form,
        'titulo': 'Registro de Nuevo Paciente',
        'mostrar_firma': True,  # Flag para mostrar pad de firma
    }

    return render(request, 'procedimientos/registrar_paciente.html', context)


@login_required
def valoraciones_paciente(request, pk):
    """Lista de valoraciones pendientes y completadas por terapeuta"""
    paciente = get_object_or_404(Paciente, pk=pk)
    
    # Valoraciones por terapeuta
    valoraciones = ValoracionProfesional.objects.filter(
        paciente=paciente
    ).select_related('terapeuta', 'terapia').order_by('-fecha_valoracion')
    
    # Terapias disponibles
    terapias = Terapia.objects.filter(activo=True)
    
    # Contar valoraciones por terapia
    terapias_valoradas = valoraciones.values_list('terapia_id', flat=True)
    
    context = {
        'paciente': paciente,
        'valoraciones': valoraciones,
        'terapias': terapias,
        'terapias_valoradas': list(terapias_valoradas),
    }
    return render(request, 'procedimientos/valoraciones_paciente.html', context)



@login_required
def crear_valoracion(request, paciente_id, terapia_id):
    """Crear valoración por terapeuta"""
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    terapia = get_object_or_404(Terapia, pk=terapia_id)
    
    # Verificar si ya existe valoración
    existe = ValoracionProfesional.objects.filter(
        paciente=paciente,
        terapeuta=request.user,
        terapia=terapia
    ).exists()
    
    if existe:
        messages.warning(request, 'Ya realizó valoración para esta terapia')
        return redirect('procedimientos:valoraciones_paciente', pk=paciente_id)
    
    if request.method == 'POST':
        form = ValoracionProfesionalForm(request.POST)
        if form.is_valid():
            valoracion = form.save(commit=False)
            valoracion.paciente = paciente
            valoracion.terapeuta = request.user
            valoracion.save()
            messages.success(request, 'Valoración registrada')
            return redirect('procedimientos:valoraciones_paciente', pk=paciente_id)
    else:
        form = ValoracionProfesionalForm(initial={'terapia': terapia})
    
    return render(request, 'procedimientos/crear_valoracion.html', {
        'form': form,
        'paciente': paciente,
        'terapia': terapia
    })


@login_required
def admisiones_paciente(request, pk):
    """Lista de admisiones del paciente"""
    paciente = get_object_or_404(Paciente, pk=pk)
    admisiones = AdmisionTerapia.objects.filter(
        paciente=paciente
    ).select_related('terapia').order_by('-fecha_inicio')
    
    return render(request, 'procedimientos/admisiones_paciente.html', {
        'paciente': paciente,
        'admisiones': admisiones
    })


@login_required
def crear_admision(request, paciente_id):
    """Crear admisión por terapia"""
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    if request.method == 'POST':
        form = AdmisionTerapiaForm(request.POST)
        if form.is_valid():
            admision = form.save(commit=False)
            admision.paciente = paciente
            admision.creado_por = request.user
            admision.save()
            messages.success(request, f'Admisión {admision.numero_admision} creada')
            return redirect('procedimientos:admisiones_paciente', pk=paciente_id)
    else:
        form = AdmisionTerapiaForm()
    
    return render(request, 'procedimientos/crear_admision.html', {
        'form': form,
        'paciente': paciente
    })


@login_required
def dashboard_admisiones(request):
    """Dashboard de admisiones vigentes y próximas a vencer"""
    hoy = timezone.now().date()
    
    # Vigentes
    vigentes = AdmisionTerapia.objects.filter(
        estado='VIGENTE',
        fecha_fin__gte=hoy
    ).select_related('paciente', 'terapia').order_by('fecha_fin')
    
    # Por vencer (7 días)
    por_vencer = vigentes.filter(fecha_fin__lte=hoy + timezone.timedelta(days=7))
    
    # Vencidas sin completar
    vencidas = AdmisionTerapia.objects.filter(
        estado='VIGENTE',
        fecha_fin__lt=hoy
    ).select_related('paciente', 'terapia')
    
    context = {
        'vigentes': vigentes,
        'por_vencer': por_vencer,
        'vencidas': vencidas,
    }
    return render(request, 'procedimientos/dashboard_admisiones.html', context)


def api_buscar_cie10(request):
    """
    API para búsqueda de códigos CIE-10 en tiempo real
    
    GET /procedimientos/api/buscar-cie10/?q=<busqueda>
    
    Returns:
        JSON con lista de códigos que coinciden
    """
    query = request.GET.get('q', '').strip()
    
    # Mínimo 2 caracteres para buscar
    if len(query) < 2:
        return JsonResponse({
            'resultados': [],
            'mensaje': 'Escriba al menos 2 caracteres'
        })
    
    try:
        # Buscar por código o descripción
        codigos = CodigoCIE10.objects.filter(
            Q(codigo__icontains=query) | 
            Q(descripcion__icontains=query) |
            Q(nombre__icontains=query),
            activo=True
        ).order_by('codigo')[:20]  # Máximo 20 resultados
        
        # Formatear resultados
        resultados = []
        for c in codigos:
            resultados.append({
                'id': c.id,
                'codigo': c.codigo,
                'descripcion': c.descripcion,
                'nombre': c.nombre if c.nombre else c.descripcion
            })
        
        return JsonResponse({
            'resultados': resultados,
            'total': len(resultados)
        })
        
    except Exception as e:
        return JsonResponse({
            'resultados': [],
            'error': str(e)
        }, status=500)



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

