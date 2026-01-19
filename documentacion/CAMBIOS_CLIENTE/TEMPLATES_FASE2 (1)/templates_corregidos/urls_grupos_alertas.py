# ============================================
# AGREGAR A: apps/grupos/urls.py
# ============================================

from django.urls import path
from . import views

app_name = 'grupos'

urlpatterns = [
    # ... URLs existentes ...
    
    # NUEVAS URLs asistencia
    path('grupos/<int:grupo_id>/asistencia/', 
         views.control_asistencia_grupo, 
         name='control_asistencia_grupo'),
    
    path('pacientes/<int:paciente_id>/historial-asistencia/', 
         views.historial_asistencia_paciente, 
         name='historial_asistencia_paciente'),
    
    # Gestión de cupos
    path('grupos/<int:grupo_id>/cambiar-cupo/', 
         views.cambiar_cupo_grupo, 
         name='cambiar_cupo_grupo'),
    
    path('alertas/<int:alerta_id>/reasignar/', 
         views.reasignar_pacientes, 
         name='reasignar_pacientes'),
]


# ============================================
# CREAR: apps/alertas/urls.py
# ============================================

from django.urls import path
from . import views

app_name = 'alertas'

urlpatterns = [
    path('', views.dashboard_alertas, name='dashboard_alertas'),
    path('<int:alerta_id>/atender/', views.atender_alerta, name='atender_alerta'),
    path('configuracion/', views.configuracion_alertas, name='configuracion_alertas'),
    path('verificar/', views.forzar_verificacion, name='forzar_verificacion'),
]


# ============================================
# AGREGAR A: config/urls.py (proyecto principal)
# ============================================

urlpatterns = [
    # ... URLs existentes ...
    path('alertas/', include('apps.alertas.urls')),
]
