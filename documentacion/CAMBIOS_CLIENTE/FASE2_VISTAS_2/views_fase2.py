# CREAR: apps/procedimientos/views_fase2.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from .models import Paciente, ValoracionProfesional, AdmisionTerapia
from .forms import PacienteRegistroForm, ValoracionProfesionalForm, AdmisionTerapiaForm


@login_required
def registrar_paciente(request):
    """Registro simple sin admisión ni historia"""
    if request.method == 'POST':
        form = PacienteRegistroForm(request.POST)
        if form.is_valid():
            paciente = form.save()
            messages.success(request, f'Paciente {paciente.nombre_completo} registrado. ID: {paciente.id}')
            return redirect('procedimientos:valoraciones_paciente', pk=paciente.id)
    else:
        form = PacienteRegistroForm()
    
    return render(request, 'procedimientos/registrar_paciente.html', {
        'form': form,
        'titulo': 'Registro de Paciente'
    })


@login_required
def valoraciones_paciente(request, pk):
    """Lista de valoraciones pendientes y completadas por terapeuta"""
    paciente = get_object_or_404(Paciente, pk=pk)
    
    # Valoraciones por terapeuta
    valoraciones = ValoracionProfesional.objects.filter(
        paciente=paciente
    ).select_related('terapeuta', 'terapia').order_by('-fecha_valoracion')
    
    # Terapias disponibles
    from apps.grupos.models import Terapia
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
    from apps.grupos.models import Terapia
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
