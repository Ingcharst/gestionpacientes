# AGREGAR A: apps/procedimientos/urls.py

from django.urls import path
from . import views_fase2

app_name = 'procedimientos'

urlpatterns = [
    # ... URLs existentes ...
    
    # NUEVAS URLs Fase 2
    path('pacientes/registrar/', views_fase2.registrar_paciente, name='registrar_paciente'),
    path('pacientes/<int:pk>/valoraciones/', views_fase2.valoraciones_paciente, name='valoraciones_paciente'),
    path('pacientes/<int:paciente_id>/valoracion/<int:terapia_id>/crear/', 
         views_fase2.crear_valoracion, name='crear_valoracion'),
    
    path('pacientes/<int:pk>/admisiones/', views_fase2.admisiones_paciente, name='admisiones_paciente'),
    path('pacientes/<int:paciente_id>/admisiones/crear/', views_fase2.crear_admision, name='crear_admision'),
    path('admisiones/dashboard/', views_fase2.dashboard_admisiones, name='dashboard_admisiones'),
]


# ============================================
# AGREGAR A: apps/grupos/urls.py

from django.urls import path
from . import views_asistencia

app_name = 'grupos'

urlpatterns = [
    # ... URLs existentes ...
    
    # NUEVAS URLs asistencia
    path('grupos/<int:grupo_id>/asistencia/', 
         views_asistencia.control_asistencia_grupo, name='control_asistencia_grupo'),
    path('pacientes/<int:paciente_id>/historial-asistencia/', 
         views_asistencia.historial_asistencia_paciente, name='historial_asistencia_paciente'),
    
    # Gestión de cupos
    path('grupos/<int:grupo_id>/cambiar-cupo/', 
         views_asistencia.cambiar_cupo_grupo, name='cambiar_cupo_grupo'),
    path('alertas/<int:alerta_id>/reasignar/', 
         views_asistencia.reasignar_pacientes, name='reasignar_pacientes'),
]
