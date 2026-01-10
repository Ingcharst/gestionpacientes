"""
Vistas del frontend para terapias.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import CategoriaTerapia, Terapia
from .forms import CategoriaTerapiaForm, TerapiaForm, FiltroTerapiaForm


# ========================================
# VISTAS DE CATEGORÍAS
# ========================================

@login_required
def categoria_list(request):
    """Lista de categorías de terapias."""
    categorias = CategoriaTerapia.objects.all()
    
    # Filtro activo
    activo = request.GET.get('activo')
    if activo:
        categorias = categorias.filter(activo=(activo == 'true'))
    
    return render(request, 'terapias/categoria_list.html', {
        'categorias': categorias
    })


@login_required
def categoria_create(request):
    """Crear nueva categoría."""
    if not (request.user.es_admin or request.user.puede_gestionar_terapias):
        messages.error(request, 'No tienes permiso para crear categorías.')
        return redirect('categoria_list')
    
    if request.method == 'POST':
        form = CategoriaTerapiaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría {categoria.nombre} creada exitosamente.')
            return redirect('categoria_list')
    else:
        form = CategoriaTerapiaForm()
    
    return render(request, 'terapias/categoria_form.html', {
        'form': form,
        'action': 'Crear'
    })


@login_required
def categoria_update(request, pk):
    """Actualizar categoría."""
    categoria = get_object_or_404(CategoriaTerapia, pk=pk)
    
    if not (request.user.es_admin or request.user.puede_gestionar_terapias):
        messages.error(request, 'No tienes permiso para editar categorías.')
        return redirect('categoria_list')
    
    if request.method == 'POST':
        form = CategoriaTerapiaForm(request.POST, instance=categoria)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, 'Categoría actualizada exitosamente.')
            return redirect('categoria_list')
    else:
        form = CategoriaTerapiaForm(instance=categoria)
    
    return render(request, 'terapias/categoria_form.html', {
        'form': form,
        'categoria': categoria,
        'action': 'Actualizar'
    })


# ========================================
# VISTAS DE TERAPIAS
# ========================================

@login_required
def terapia_list(request):
    """Lista de terapias con filtros."""
    terapias = Terapia.objects.select_related('categoria').all()
    
    # Aplicar filtros
    form = FiltroTerapiaForm(request.GET)
    
    if form.is_valid():
        categoria = form.cleaned_data.get('categoria')
        modalidad = form.cleaned_data.get('modalidad')
        especialidad = form.cleaned_data.get('especialidad')
        solo_destacadas = form.cleaned_data.get('solo_destacadas')
        search = form.cleaned_data.get('search')
        
        if categoria:
            terapias = terapias.filter(categoria=categoria)
        
        if modalidad:
            terapias = terapias.filter(modalidad=modalidad)
        
        if especialidad:
            terapias = terapias.filter(especialidad=especialidad)
        
        if solo_destacadas:
            terapias = terapias.filter(destacado=True)
        
        if search:
            terapias = terapias.filter(
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search) |
                Q(descripcion_corta__icontains=search)
            )
    
    context = {
        'terapias': terapias,
        'form': form,
        'total': terapias.count(),
    }
    
    return render(request, 'terapias/terapia_list.html', context)


@login_required
def terapia_detail(request, pk):
    """Detalle de una terapia."""
    terapia = get_object_or_404(
        Terapia.objects.select_related('categoria'),
        pk=pk
    )
    
    return render(request, 'terapias/terapia_detail.html', {
        'terapia': terapia
    })


@login_required
def terapia_create(request):
    """Crear nueva terapia."""
    if not (request.user.es_admin or request.user.puede_gestionar_terapias):
        messages.error(request, 'No tienes permiso para crear terapias.')
        return redirect('terapia_list')
    
    if request.method == 'POST':
        form = TerapiaForm(request.POST, request.FILES)
        if form.is_valid():
            terapia = form.save()
            messages.success(request, f'Terapia {terapia.nombre} creada exitosamente.')
            return redirect('terapia_detail', pk=terapia.pk)
    else:
        form = TerapiaForm()
    
    return render(request, 'terapias/terapia_form.html', {
        'form': form,
        'action': 'Crear'
    })


@login_required
def terapia_update(request, pk):
    """Actualizar terapia."""
    terapia = get_object_or_404(Terapia, pk=pk)
    
    if not (request.user.es_admin or request.user.puede_gestionar_terapias):
        messages.error(request, 'No tienes permiso para editar terapias.')
        return redirect('terapia_detail', pk=pk)
    
    if request.method == 'POST':
        form = TerapiaForm(request.POST, request.FILES, instance=terapia)
        if form.is_valid():
            terapia = form.save()
            messages.success(request, 'Terapia actualizada exitosamente.')
            return redirect('terapia_detail', pk=terapia.pk)
    else:
        form = TerapiaForm(instance=terapia)
    
    return render(request, 'terapias/terapia_form.html', {
        'form': form,
        'terapia': terapia,
        'action': 'Actualizar'
    })


@login_required
def catalogo_terapias(request):
    """Vista del catálogo público de terapias."""
    terapias = Terapia.objects.filter(activo=True).select_related('categoria')
    categorias = CategoriaTerapia.objects.filter(activo=True)
    
    # Filtro por categoría
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        terapias = terapias.filter(categoria_id=categoria_id)
    
    # Destacadas
    destacadas = terapias.filter(destacado=True)[:6]
    
    context = {
        'terapias': terapias,
        'categorias': categorias,
        'destacadas': destacadas,
    }
    
    return render(request, 'terapias/catalogo.html', context)


@login_required
def terapias_por_especialidad(request, especialidad):
    """Lista terapias por especialidad."""
    terapias = Terapia.objects.filter(
        especialidad=especialidad,
        activo=True
    ).select_related('categoria')
    
    especialidad_display = dict(Terapia.Especialidad.choices).get(especialidad, especialidad)
    
    return render(request, 'terapias/terapia_list.html', {
        'terapias': terapias,
        'titulo': f'Terapias de {especialidad_display}',
        'total': terapias.count(),
    })
