# AGREGAR A: apps/procedimientos/urls.py

from django.urls import path
from . import views

app_name = 'procedimientos'

urlpatterns = [
    # ... URLs existentes ...
    
    # NUEVAS URLs Fase 2
    path('pacientes/registrar/', views.registrar_paciente, name='registrar_paciente'),
    
    # Vistas de listado
    path('pacientes/pendientes-valoracion/', 
         views.pacientes_pendientes_valoracion, 
         name='pacientes_pendientes_valoracion'),
    
    path('pacientes/pendientes-asignacion/', 
         views.pacientes_pendientes_asignacion, 
         name='pacientes_pendientes_asignacion'),
    
    # Valoraciones
    path('pacientes/<int:pk>/valoraciones/', 
         views.valoraciones_paciente, 
         name='valoraciones_paciente'),
    
    path('pacientes/<int:paciente_id>/valoracion/<int:terapia_id>/crear/', 
         views.crear_valoracion, 
         name='crear_valoracion'),
    
    # Admisiones
    path('pacientes/<int:pk>/admisiones/', 
         views.admisiones_paciente, 
         name='admisiones_paciente'),
    
    path('pacientes/<int:paciente_id>/admisiones/crear/', 
         views.crear_admision, 
         name='crear_admision'),
    
    path('admisiones/dashboard/', 
         views.dashboard_admisiones, 
         name='dashboard_admisiones'),
]


# ============================================
# VISTAS FALTANTES (si no existen)
# ============================================

# AGREGAR A: apps/procedimientos/views.py

@login_required
def pacientes_pendientes_valoracion(request):
    """Lista de pacientes que no tienen valoraciones"""
    from apps.procedimientos.models import Paciente, ValoracionProfesional
    
    # Pacientes sin ninguna valoración
    pacientes_con_valoracion = ValoracionProfesional.objects.values_list('paciente_id', flat=True).distinct()
    pacientes = Paciente.objects.exclude(id__in=pacientes_con_valoracion).order_by('-fecha_creacion')
    
    context = {
        'pacientes': pacientes,
        'titulo': 'Pacientes Pendientes de Valoración'
    }
    return render(request, 'procedimientos/pacientes_pendientes_valoracion.html', context)


@login_required
def pacientes_pendientes_asignacion(request):
    """Lista de pacientes con valoraciones pero sin grupo asignado"""
    from apps.procedimientos.models import Paciente
    from apps.grupos.models import AsignacionGrupo
    
    # Pacientes con valoraciones pero sin asignación activa
    pacientes_asignados = AsignacionGrupo.objects.filter(
        estado='ACTIVA'
    ).values_list('paciente_id', flat=True).distinct()
    
    pacientes = Paciente.objects.filter(
        valoraciones_profesionales__isnull=False
    ).exclude(
        id__in=pacientes_asignados
    ).distinct().order_by('-fecha_creacion')
    
    context = {
        'pacientes': pacientes,
        'titulo': 'Pacientes Pendientes de Asignación'
    }
    return render(request, 'procedimientos/pacientes_pendientes_asignacion.html', context)
