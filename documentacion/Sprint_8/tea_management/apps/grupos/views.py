"""
Vistas para gestión de grupos terapéuticos.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import GrupoTerapeutico, AsignacionGrupo, PacientePendiente
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
def asignar_paciente_grupo(request, paciente_pk=None):
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
                messages.success(request, mensaje)
                return redirect('grupos:grupo_detail', pk=grupo.pk)
            else:
                messages.error(request, mensaje)
    else:
        initial = {}
        if paciente_pk:
            initial['paciente'] = paciente_pk
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
        estado='PENDIENTE'
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
