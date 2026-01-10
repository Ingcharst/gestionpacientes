# ============================================================================
# SPRINT 1 - URLs
# apps/procedimientos/urls.py
# ============================================================================

"""
INSTRUCCIONES:
Agregar estas rutas a apps/procedimientos/urls.py en la lista urlpatterns
"""

from django.urls import path
from . import views

# Agregar al urlpatterns existente:

# ============================================================================
# SPRINT 1: ADMISIÓN Y VALORACIÓN
# ============================================================================

# Admisión de Pacientes
path('admision/', views.admision_paciente, name='admision_paciente'),

# Valoración Inicial
path('pacientes/pendientes-valoracion/', views.pacientes_pendientes_valoracion, name='pacientes_pendientes_valoracion'),
path('pacientes/<int:paciente_id>/valoracion/crear/', views.crear_valoracion_inicial, name='crear_valoracion_inicial'),
path('pacientes/<int:paciente_id>/valoracion/', views.ver_valoracion_inicial, name='ver_valoracion_inicial'),
path('pacientes/<int:paciente_id>/valoracion/editar/', views.editar_valoracion_inicial, name='editar_valoracion_inicial'),
path('valoracion/<int:valoracion_id>/completar/', views.completar_valoracion, name='completar_valoracion'),

# Lista para Asignación de Grupos
path('pacientes/pendientes-asignacion/', views.pacientes_pendientes_asignacion, name='pacientes_pendientes_asignacion'),


# ============================================================================
# EJEMPLO DE CÓMO QUEDARÍAN LAS URLs COMPLETAS:
# ============================================================================

"""
app_name = 'procedimientos'

urlpatterns = [
    # ... URLs existentes ...
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Pacientes
    path('pacientes/', views.paciente_lista, name='paciente_list'),
    path('pacientes/crear/', views.paciente_crear, name='paciente_create'),
    path('pacientes/<int:pk>/', views.paciente_detalle, name='paciente_detail'),
    path('pacientes/<int:pk>/editar/', views.paciente_editar, name='paciente_edit'),
    
    # SPRINT 1: ADMISIÓN Y VALORACIÓN (NUEVO)
    path('admision/', views.admision_paciente, name='admision_paciente'),
    path('pacientes/pendientes-valoracion/', views.pacientes_pendientes_valoracion, name='pacientes_pendientes_valoracion'),
    path('pacientes/<int:paciente_id>/valoracion/crear/', views.crear_valoracion_inicial, name='crear_valoracion_inicial'),
    path('pacientes/<int:paciente_id>/valoracion/', views.ver_valoracion_inicial, name='ver_valoracion_inicial'),
    path('pacientes/<int:paciente_id>/valoracion/editar/', views.editar_valoracion_inicial, name='editar_valoracion_inicial'),
    path('valoracion/<int:valoracion_id>/completar/', views.completar_valoracion, name='completar_valoracion'),
    path('pacientes/pendientes-asignacion/', views.pacientes_pendientes_asignacion, name='pacientes_pendientes_asignacion'),
    
    # Procedimientos
    path('procedimientos/', views.procedimiento_lista, name='procedimiento_list'),
    # ... resto de URLs ...
]
"""
