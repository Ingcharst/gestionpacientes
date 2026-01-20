"""
Vistas del frontend para consultorios.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import date, timedelta
from django.utils import timezone

from .models import Consultorio, Sala, AsignacionConsultorio, DisponibilidadConsultorio
from .forms import (
    ConsultorioForm, SalaForm, AsignacionConsultorioForm,
    DisponibilidadConsultorioForm, FiltroConsultorioForm
)


# ========================================
# VISTAS DE CONSULTORIOS
# ========================================

@login_required
def consultorio_list(request):
    """Lista de consultorios con filtros."""
    consultorios = Consultorio.objects.prefetch_related('salas', 'asignaciones').all()
    
    # Aplicar filtros
    form = FiltroConsultorioForm(request.GET)
    
    if form.is_valid():
        tipo = form.cleaned_data.get('tipo')
        estado = form.cleaned_data.get('estado')
        piso = form.cleaned_data.get('piso')
        activo = form.cleaned_data.get('activo')
        search = form.cleaned_data.get('search')
        
        if tipo:
            consultorios = consultorios.filter(tipo=tipo)
        
        if estado:
            consultorios = consultorios.filter(estado=estado)
        
        if piso is not None:
            consultorios = consultorios.filter(piso=piso)
        
        if activo:
            consultorios = consultorios.filter(activo=(activo == 'true'))
        
        if search:
            consultorios = consultorios.filter(
                Q(nombre__icontains=search) |
                Q(codigo__icontains=search) |
                Q(numero__icontains=search) |
                Q(caracteristicas__icontains=search)
            )
    
    # Estadísticas
    total = consultorios.count()
    disponibles = consultorios.filter(
        estado=Consultorio.EstadoConsultorio.DISPONIBLE
    ).count()
    ocupados = consultorios.filter(
        estado=Consultorio.EstadoConsultorio.OCUPADO
    ).count()
    
    context = {
        'consultorios': consultorios,
        'form': form,
        'total': total,
        'disponibles': disponibles,
        'ocupados': ocupados,
    }
    
    # Si es petición HTMX, solo renderizar la tabla
    if request.headers.get('HX-Request'):
        return render(request, 'consultorios/partials/consultorio_table.html', context)
    
    return render(request, 'consultorios/consultorio_list.html', context)


@login_required
def consultorio_detail(request, pk):
    """Detalle de un consultorio."""
    consultorio = get_object_or_404(
        Consultorio.objects.prefetch_related('salas', 'asignaciones__terapeuta'),
        pk=pk
    )
    
    # Obtener asignaciones activas
    asignaciones = consultorio.asignaciones.filter(activo=True)
    
    # Obtener salas
    salas = consultorio.salas.filter(activo=True)
    
    context = {
        'consultorio': consultorio,
        'asignaciones': asignaciones,
        'salas': salas,
    }
    
    return render(request, 'consultorios/consultorio_detail.html', context)


@login_required
def consultorio_create(request):
    """Crear nuevo consultorio."""
    if not (request.user.es_admin or request.user.puede_gestionar_terapias):
        messages.error(request, 'No tienes permiso para crear consultorios.')
        return redirect('consultorios:consultorio_list')
    
    if request.method == 'POST':
        form = ConsultorioForm(request.POST, request.FILES)
        if form.is_valid():
            consultorio = form.save()
            messages.success(request, f'Consultorio {consultorio.nombre} creado exitosamente.')
            return redirect('consultorios:consultorio_detail', pk=consultorio.pk)
    else:
        form = ConsultorioForm()
    
    return render(request, 'consultorios/consultorio_form.html', {
        'form': form,
        'action': 'Crear'
    })


@login_required
def consultorio_update(request, pk):
    """Actualizar consultorio."""
    consultorio = get_object_or_404(Consultorio, pk=pk)
    
    if not (request.user.es_admin or request.user.puede_gestionar_terapias):
        messages.error(request, 'No tienes permiso para editar consultorios.')
        return redirect('consultorios:consultorio_detail', pk=pk)
    
    if request.method == 'POST':
        form = ConsultorioForm(request.POST, request.FILES, instance=consultorio)
        if form.is_valid():
            consultorio = form.save()
            messages.success(request, 'Consultorio actualizado exitosamente.')
            return redirect('consultorios:consultorio_detail', pk=consultorio.pk)
    else:
        form = ConsultorioForm(instance=consultorio)
    
    return render(request, 'consultorios/consultorio_form.html', {
        'form': form,
        'consultorio': consultorio,
        'action': 'Actualizar'
    })


@login_required
@require_http_methods(["POST"])
def consultorio_cambiar_estado(request, pk):
    """Cambiar estado del consultorio (HTMX)."""
    if not (request.user.es_admin or request.user.puede_gestionar_terapias):
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    consultorio = get_object_or_404(Consultorio, pk=pk)
    nuevo_estado = request.POST.get('estado')
    
    if nuevo_estado in dict(Consultorio.EstadoConsultorio.choices):
        consultorio.estado = nuevo_estado
        consultorio.save()
        
        if request.headers.get('HX-Request'):
            return render(request, 'consultorios/partials/consultorio_estado_badge.html', {
                'consultorio': consultorio
            })
        
        return JsonResponse({
            'mensaje': f'Estado cambiado a {consultorio.get_estado_display()}'
        })
    
    return JsonResponse({'error': 'Estado no válido'}, status=400)


# ========================================
# VISTAS DE SALAS
# ========================================

@login_required
def sala_create(request, consultorio_pk):
    """Crear nueva sala en un consultorio."""
    consultorio = get_object_or_404(Consultorio, pk=consultorio_pk)
    
    if not (request.user.es_admin or request.user.puede_gestionar_terapias):
        messages.error(request, 'No tienes permiso para crear salas.')
        return redirect('consultorios:consultorio_detail', pk=consultorio_pk)
    
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            sala = form.save()
            messages.success(request, f'Sala {sala.nombre} creada exitosamente.')
            return redirect('consultorios:consultorio_detail', pk=consultorio.pk)
    else:
        form = SalaForm(initial={'consultorio': consultorio})
    
    return render(request, 'consultorios/sala_form.html', {
        'form': form,
        'consultorio': consultorio,
        'action': 'Crear'
    })


@login_required
def sala_update(request, pk):
    """Actualizar sala."""
    sala = get_object_or_404(Sala, pk=pk)
    
    if not (request.user.es_admin or request.user.puede_gestionar_terapias):
        messages.error(request, 'No tienes permiso para editar salas.')
        return redirect('consultorios:consultorio_detail', pk=sala.consultorio.pk)
    
    if request.method == 'POST':
        form = SalaForm(request.POST, instance=sala)
        if form.is_valid():
            sala = form.save()
            messages.success(request, 'Sala actualizada exitosamente.')
            return redirect('consultorios:consultorio_detail', pk=sala.consultorio.pk)
    else:
        form = SalaForm(instance=sala)
    
    return render(request, 'consultorios/sala_form.html', {
        'form': form,
        'sala': sala,
        'consultorio': sala.consultorio,
        'action': 'Actualizar'
    })


# ========================================
# VISTAS DE ASIGNACIONES
# ========================================

@login_required
def asignacion_list(request):
    """Lista de asignaciones de consultorios."""
    asignaciones = AsignacionConsultorio.objects.select_related(
        'consultorio', 'terapeuta', 'terapia'
    ).all()
    
    # Filtros
    activo = request.GET.get('activo')
    if activo == 'true':
        asignaciones = asignaciones.filter(activo=True)
    elif activo == 'false':
        asignaciones = asignaciones.filter(activo=False)
    
    consultorio_id = request.GET.get('consultorio')
    if consultorio_id:
        asignaciones = asignaciones.filter(consultorio_id=consultorio_id)
    
    terapeuta_id = request.GET.get('terapeuta')
    if terapeuta_id:
        asignaciones = asignaciones.filter(terapeuta_id=terapeuta_id)
    
    # ✅ FILTRO POR TERAPIA
    terapia_id = request.GET.get('terapia')
    if terapia_id:
        asignaciones = asignaciones.filter(terapia_id=terapia_id)
    
    context = {
        'asignaciones': asignaciones,
        'total': asignaciones.count(),
        'consultorios': Consultorio.objects.filter(activo=True),
    }
    
    return render(request, 'consultorios/asignacion_list.html', context)


@login_required
def asignacion_detail(request, pk):
    """Detalle de una asignación."""
    asignacion = get_object_or_404(
        AsignacionConsultorio.objects.select_related('consultorio', 'terapeuta'),
        pk=pk
    )
    
    return render(request, 'consultorios/asignacion_detail.html', {
        'asignacion': asignacion
    })


@login_required
def asignacion_create(request):
    """Crear nueva asignación."""
    if not (request.user.es_admin or request.user.puede_gestionar_terapias):
        messages.error(request, 'No tienes permiso para crear asignaciones.')
        return redirect('consultorios:asignacion_list')
    
    if request.method == 'POST':
        form = AsignacionConsultorioForm(request.POST)
        if form.is_valid():
            asignacion = form.save()
            messages.success(request, 'Asignación creada exitosamente.')
            return redirect('consultorios:asignacion_detail', pk=asignacion.pk)
    else:
        form = AsignacionConsultorioForm()
    
    return render(request, 'consultorios/asignacion_form.html', {
        'form': form,
        'action': 'Crear'
    })


@login_required
def asignacion_update(request, pk):
    """Actualizar asignación."""
    asignacion = get_object_or_404(AsignacionConsultorio, pk=pk)
    
    if not (request.user.es_admin or request.user.puede_gestionar_terapias):
        messages.error(request, 'No tienes permiso para editar asignaciones.')
        return redirect('consultorios:asignacion_detail', pk=pk)
    
    if request.method == 'POST':
        form = AsignacionConsultorioForm(request.POST, instance=asignacion)
        if form.is_valid():
            asignacion = form.save()
            messages.success(request, 'Asignación actualizada exitosamente.')
            return redirect('consultorios:asignacion_detail', pk=asignacion.pk)
    else:
        form = AsignacionConsultorioForm(instance=asignacion)
    
    return render(request, 'consultorios/asignacion_form.html', {
        'form': form,
        'asignacion': asignacion,
        'action': 'Actualizar'
    })


@login_required
def mis_consultorios(request):
    """Lista de consultorios asignados al terapeuta autenticado."""
    if not request.user.es_terapeuta:
        messages.error(request, 'Esta vista es solo para terapeutas.')
        return redirect('consultorios:consultorio_list')
    
    asignaciones = AsignacionConsultorio.objects.filter(
        terapeuta=request.user,
        activo=True
    ).select_related('consultorio', 'terapia')
    
    return render(request, 'consultorios/mis_consultorios.html', {
        'asignaciones': asignaciones
    })


# ========================================
# VISTAS DE DISPONIBILIDAD
# ========================================

@login_required
def disponibilidad_list(request):
    """Lista de disponibilidades de consultorios."""
    disponibilidades = DisponibilidadConsultorio.objects.select_related(
        'consultorio', 'terapeuta'
    ).all()
    
    # Filtros
    consultorio_id = request.GET.get('consultorio')
    fecha = request.GET.get('fecha')
    estado = request.GET.get('estado')
    
    if consultorio_id:
        disponibilidades = disponibilidades.filter(consultorio_id=consultorio_id)
    
    if fecha:
        disponibilidades = disponibilidades.filter(fecha=fecha)
    
    if estado:
        disponibilidades = disponibilidades.filter(estado=estado)
    
    context = {
        'disponibilidades': disponibilidades,
        'consultorios': Consultorio.objects.filter(activo=True),
    }
    
    return render(request, 'consultorios/disponibilidad_list.html', context)


@login_required
def disponibilidad_create(request):
    """Crear nueva disponibilidad."""
    if not (request.user.es_admin or request.user.puede_gestionar_terapias):
        messages.error(request, 'No tienes permiso para gestionar disponibilidades.')
        return redirect('consultorios:disponibilidad_list')
    
    if request.method == 'POST':
        form = DisponibilidadConsultorioForm(request.POST)
        if form.is_valid():
            disponibilidad = form.save()
            messages.success(request, 'Disponibilidad creada exitosamente.')
            return redirect('consultorios:disponibilidad_list')
    else:
        form = DisponibilidadConsultorioForm()
    
    return render(request, 'consultorios/disponibilidad_form.html', {
        'form': form,
        'action': 'Crear'
    })


@login_required
def disponibilidad_update(request, pk):
    """Actualizar disponibilidad."""
    disponibilidad = get_object_or_404(DisponibilidadConsultorio, pk=pk)
    
    if not (request.user.es_admin or request.user.puede_gestionar_terapias):
        messages.error(request, 'No tienes permiso para editar disponibilidades.')
        return redirect('consultorios:disponibilidad_list')
    
    if request.method == 'POST':
        form = DisponibilidadConsultorioForm(request.POST, instance=disponibilidad)
        if form.is_valid():
            disponibilidad = form.save()
            messages.success(request, 'Disponibilidad actualizada exitosamente.')
            return redirect('consultorios:disponibilidad_list')
    else:
        form = DisponibilidadConsultorioForm(instance=disponibilidad)
    
    return render(request, 'consultorios/disponibilidad_form.html', {
        'form': form,
        'disponibilidad': disponibilidad,
        'action': 'Actualizar'
    })


@login_required
def calendario_disponibilidad(request):
    """Vista de calendario de disponibilidad de consultorios."""
    # Fecha actual
    hoy = date.today()
    
    # Rango de una semana
    fecha_inicio = request.GET.get('fecha_inicio', hoy)
    if isinstance(fecha_inicio, str):
        from datetime import datetime
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    
    fecha_fin = fecha_inicio + timedelta(days=6)
    
    # Consultorios activos
    consultorios = Consultorio.objects.filter(activo=True).order_by('piso', 'numero')
    
    # Disponibilidades del rango
    disponibilidades = DisponibilidadConsultorio.objects.filter(
        fecha__gte=fecha_inicio,
        fecha__lte=fecha_fin
    ).select_related('consultorio', 'terapeuta')
    
    # Organizar por consultorio y fecha
    calendario = {}
    for consultorio in consultorios:
        calendario[consultorio] = {}
        fecha = fecha_inicio
        while fecha <= fecha_fin:
            disps = disponibilidades.filter(
                consultorio=consultorio,
                fecha=fecha
            )
            calendario[consultorio][fecha] = list(disps)
            fecha += timedelta(days=1)
    
    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'consultorios': consultorios,
        'calendario': calendario,
    }
    
    return render(request, 'consultorios/calendario_disponibilidad.html', context)


# ========================================
# VISTAS DE ESTADÍSTICAS
# ========================================

@login_required
def estadisticas_consultorios(request):
    """Dashboard de estadísticas de consultorios."""
    # Estadísticas generales
    total = Consultorio.objects.filter(activo=True).count()
    disponibles = Consultorio.objects.filter(
        estado=Consultorio.EstadoConsultorio.DISPONIBLE,
        activo=True
    ).count()
    ocupados = Consultorio.objects.filter(
        estado=Consultorio.EstadoConsultorio.OCUPADO,
        activo=True
    ).count()
    mantenimiento = Consultorio.objects.filter(
        estado=Consultorio.EstadoConsultorio.MANTENIMIENTO,
        activo=True
    ).count()
    
    # Por tipo
    por_tipo = {}
    for choice in Consultorio.TipoConsultorio.choices:
        tipo_key = choice[0]
        tipo_label = choice[1]
        count = Consultorio.objects.filter(tipo=tipo_key, activo=True).count()
        por_tipo[tipo_label] = count
    
    # Por piso
    pisos = Consultorio.objects.filter(activo=True).values_list('piso', flat=True).distinct()
    por_piso = {}
    for piso in pisos:
        count = Consultorio.objects.filter(piso=piso, activo=True).count()
        por_piso[f'Piso {piso}'] = count
    
    # Tasa de ocupación
    tasa_ocupacion = (ocupados / total * 100) if total > 0 else 0
    
    # Asignaciones activas
    asignaciones_activas = AsignacionConsultorio.objects.filter(activo=True).count()
    
    context = {
        'total': total,
        'disponibles': disponibles,
        'ocupados': ocupados,
        'mantenimiento': mantenimiento,
        'por_tipo': por_tipo,
        'por_piso': por_piso,
        'tasa_ocupacion': round(tasa_ocupacion, 2),
        'asignaciones_activas': asignaciones_activas,
    }
    
    return render(request, 'consultorios/estadisticas.html', context)
