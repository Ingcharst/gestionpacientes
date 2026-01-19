# CREAR: apps/alertas/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AlertaInasistencia, ConfiguracionAlerta
from .utils import GestorAlertas


@login_required
def dashboard_alertas(request):
    """Panel principal de alertas"""
    gestor = GestorAlertas()
    
    alertas_pendientes = gestor.obtener_alertas_pendientes()
    alertas_atendidas = AlertaInasistencia.objects.filter(
        estado='ATENDIDA'
    ).select_related('paciente', 'atendida_por').order_by('-fecha_atencion')[:20]
    
    context = {
        'pendientes': alertas_pendientes,
        'atendidas': alertas_atendidas,
        'total_pendientes': alertas_pendientes.count()
    }
    return render(request, 'alertas/dashboard.html', context)


@login_required
def atender_alerta(request, alerta_id):
    """Marcar alerta como atendida"""
    alerta = get_object_or_404(AlertaInasistencia, pk=alerta_id)
    
    if request.method == 'POST':
        observaciones = request.POST.get('observaciones', '')
        
        gestor = GestorAlertas()
        gestor.marcar_atendida(alerta_id, request.user, observaciones)
        
        messages.success(request, 'Alerta marcada como atendida')
        return redirect('alertas:dashboard_alertas')
    
    context = {'alerta': alerta}
    return render(request, 'alertas/atender_alerta.html', context)


@login_required
def configuracion_alertas(request):
    """Configuración del sistema de alertas"""
    config = ConfiguracionAlerta.get_config()
    
    if request.method == 'POST':
        config.dias_inasistencia_alerta = int(request.POST.get('dias_alerta', 3))
        config.telefono_ips = request.POST.get('telefono_ips', '')
        config.mensaje_sms_template = request.POST.get('mensaje_template', '')
        config.save()
        
        messages.success(request, 'Configuración actualizada')
        return redirect('alertas:configuracion_alertas')
    
    context = {'config': config}
    return render(request, 'alertas/configuracion.html', context)


@login_required
def forzar_verificacion(request):
    """Forzar verificación manual de inasistencias"""
    if request.method == 'POST':
        gestor = GestorAlertas()
        alertas = gestor.verificar_inasistencias()
        
        messages.success(request, f'Verificación completada. {len(alertas)} alertas generadas')
        return redirect('alertas:dashboard_alertas')
    
    return render(request, 'alertas/forzar_verificacion.html')


# URLS: apps/alertas/urls.py

from django.urls import path
from . import views

app_name = 'alertas'

urlpatterns = [
    path('', views.dashboard_alertas, name='dashboard_alertas'),
    path('<int:alerta_id>/atender/', views.atender_alerta, name='atender_alerta'),
    path('configuracion/', views.configuracion_alertas, name='configuracion_alertas'),
    path('verificar/', views.forzar_verificacion, name='forzar_verificacion'),
]
