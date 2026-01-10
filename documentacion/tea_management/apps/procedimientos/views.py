"""
Vistas para procedimientos (frontend).
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone

from apps.procedimientos.models import (
    Paciente, Procedimiento, SesionTerapeutica,
    ObjetivoTerapeutico, EvolucionPaciente
)
from apps.procedimientos.forms import (
    PacienteForm, ProcedimientoForm, SesionTerapeuticaForm,
    ObjetivoTerapeuticoForm, EvolucionPacienteForm
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
            Q(numero_historia_clinica__icontains=query)
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
    evoluciones = paciente.evoluciones.all()[:10]
    
    context = {
        'paciente': paciente,
        'procedimientos': procedimientos,
        'sesiones': sesiones,
        'objetivos': objetivos,
        'evoluciones': evoluciones,
    }
    
    return render(request, 'procedimientos/paciente_detalle.html', context)


@login_required
def paciente_crear(request):
    """Crear un nuevo paciente."""
    if request.method == 'POST':
        form = PacienteForm(request.POST, request.FILES)
        if form.is_valid():
            paciente = form.save(commit=False)
            paciente.creado_por = request.user
            paciente.save()
            messages.success(request, f'Paciente {paciente.nombre_completo} creado exitosamente.')
            return redirect('procedimientos:paciente_detalle', pk=paciente.pk)
    else:
        form = PacienteForm()
    
    context = {'form': form, 'titulo': 'Crear Paciente'}
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
            return redirect('procedimientos:paciente_detalle', pk=paciente.pk)
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
            sesion = form.save(commit=False)
            sesion.creado_por = request.user
            sesion.save()
            messages.success(request, f'Sesión {sesion.numero_sesion} creada exitosamente.')
            return redirect('procedimientos:sesion_detalle', pk=sesion.pk)
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
            procedimiento = form.save(commit=False)
            procedimiento.creado_por = request.user
            procedimiento.save()
            messages.success(request, 'Procedimiento creado exitosamente.')
            return redirect('procedimientos:procedimiento_list')
    else:
        form = ProcedimientoForm()
    
    context = {'form': form, 'titulo': 'Crear Procedimiento'}
    return render(request, 'procedimientos/form.html', context)

