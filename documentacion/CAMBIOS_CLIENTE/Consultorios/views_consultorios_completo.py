"""
Vistas del frontend para consultorios.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
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
    consultorios = Consultorio.objects.all()
    
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
    
    context = {
        'consultorios': consultorios,
        'form': form,
        'total': consultorios.count(),
    }
    
    return render(request, 'consultorios/consultorio_list.html', context)


@login_required
def consultorio_detail(request, pk):
    """Detalle de un consultorio."""
    consultorio = get_object_or_404(
        Consultorio.objects.prefetch_related('salas', 'asignaciones'),
        pk=pk
    )
    
    # Asignaciones activas
    asignaciones_activas = consultorio.asignaciones.filter(activo=True)
    
    context = {
        'consultorio': consultorio,
        'asignaciones_activas': asignaciones_activas,
    }
    
    return render(request, 'consultorios/consultorio_detail.html', context)


@login_required
def consultorio_create(request):
    """Crear nuevo consultorio."""
    if not (request.user.es_admin or request.user.es_coordinador):
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
    
    if not (request.user.es_admin or request.user.es_coordinador):
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
def consultorio_cambiar_estado(request, pk):
    """Cambiar estado de consultorio."""
    consultorio = get_object_or_404(Consultorio, pk=pk)
    
    if not (request.user.es_admin or request.user.es_coordinador):
        messages.error(request, 'No tienes permiso para cambiar el estado.')
        return redirect('consultorios:consultorio_detail', pk=pk)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Consultorio.EstadoConsultorio.choices):
            consultorio.estado = nuevo_estado
            consultorio.save()
            messages.success(request, f'Estado cambiado a {consultorio.get_estado_display()}')
        else:
            messages.error(request, 'Estado no válido.')
    
    return redirect('consultorios:consultorio_detail', pk=pk)


# ========================================
# VISTAS DE SALAS
# ========================================

@login_required
def sala_create(request, consultorio_pk):
    """Crear sala en un consultorio."""
    consultorio = get_object_or_404(Consultorio, pk=consultorio_pk)
    
    if not (request.user.es_admin or request.user.es_coordinador):
        messages.error(request, 'No tienes permiso para crear salas.')
        return redirect('consultorios:consultorio_detail', pk=consultorio_pk)
    
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            sala = form.save()
            messages.success(request, f'Sala {sala.nombre} creada exitosamente.')
            return redirect('consultorios:consultorio_detail', pk=consultorio.pk)
    else:
        # Pre-seleccionar consultorio
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
    
    if not (request.user.es_admin or request.user.es_coordinador):
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
        'action': 'Actualizar'
    })


# ========================================
# VISTAS DE ASIGNACIONES
# ========================================

@login_required
def asignacion_list(request):
    """Lista de asignaciones de consultorios."""
    asignaciones = AsignacionConsultorio.objects.select_related(
        'consultorio', 'terapeuta', 'terapia'  # ✅ INCLUIR TERAPIA
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
    """Detalle de asignación."""
    asignacion = get_object_or_404(
        AsignacionConsultorio.objects.select_related(
            'consultorio', 'terapeuta', 'terapia'
        ),
        pk=pk
    )
    
    return render(request, 'consultorios/asignacion_detail.html', {
        'asignacion': asignacion
    })


@login_required
def asignacion_create(request):
    """Crear nueva asignación."""
    if not (request.user.es_admin or request.user.es_coordinador):
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
    
    if not (request.user.es_admin or request.user.es_coordinador):
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
    """Consultorios asignados al terapeuta actual."""
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
    """Lista de disponibilidad de consultorios."""
    disponibilidades = DisponibilidadConsultorio.objects.select_related(
        'consultorio', 'terapeuta'
    ).all()
    
    # Filtros
    consultorio_id = request.GET.get('consultorio')
    if consultorio_id:
        disponibilidades = disponibilidades.filter(consultorio_id=consultorio_id)
    
    fecha = request.GET.get('fecha')
    if fecha:
        disponibilidades = disponibilidades.filter(fecha=fecha)
    
    estado = request.GET.get('estado')
    if estado:
        disponibilidades = disponibilidades.filter(estado=estado)
    
    context = {
        'disponibilidades': disponibilidades,
        'total': disponibilidades.count(),
        'consultorios': Consultorio.objects.filter(activo=True),
    }
    
    return render(request, 'consultorios/disponibilidad_list.html', context)


@login_required
def disponibilidad_create(request):
    """Crear disponibilidad."""
    if not (request.user.es_admin or request.user.es_coordinador):
        messages.error(request, 'No tienes permiso para gestionar disponibilidad.')
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
    
    if not (request.user.es_admin or request.user.es_coordinador):
        messages.error(request, 'No tienes permiso para gestionar disponibilidad.')
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
    """Vista de calendario de disponibilidad."""
    hoy = timezone.now().date()
    
    # Disponibilidad de hoy
    disponibilidades_hoy = DisponibilidadConsultorio.objects.filter(
        fecha=hoy
    ).select_related('consultorio', 'terapeuta')
    
    context = {
        'disponibilidades_hoy': disponibilidades_hoy,
        'fecha': hoy,
    }
    
    return render(request, 'consultorios/calendario_disponibilidad.html', context)


@login_required
def estadisticas_consultorios(request):
    """Estadísticas de uso de consultorios."""
    if not (request.user.es_admin or request.user.es_coordinador):
        messages.error(request, 'No tienes permiso para ver estadísticas.')
        return redirect('consultorios:consultorio_list')
    
    # Estadísticas generales
    total_consultorios = Consultorio.objects.count()
    consultorios_disponibles = Consultorio.objects.filter(
        estado='DISPONIBLE', activo=True
    ).count()
    consultorios_ocupados = Consultorio.objects.filter(
        estado='OCUPADO'
    ).count()
    consultorios_mantenimiento = Consultorio.objects.filter(
        estado='MANTENIMIENTO'
    ).count()
    
    # Asignaciones activas
    asignaciones_activas = AsignacionConsultorio.objects.filter(
        activo=True
    ).count()
    
    # Por tipo
    por_tipo = Consultorio.objects.values('tipo').annotate(
        total=Count('id')
    ).order_by('-total')
    
    context = {
        'total_consultorios': total_consultorios,
        'consultorios_disponibles': consultorios_disponibles,
        'consultorios_ocupados': consultorios_ocupados,
        'consultorios_mantenimiento': consultorios_mantenimiento,
        'asignaciones_activas': asignaciones_activas,
        'por_tipo': por_tipo,
    }
    
    return render(request, 'consultorios/estadisticas.html', context)
