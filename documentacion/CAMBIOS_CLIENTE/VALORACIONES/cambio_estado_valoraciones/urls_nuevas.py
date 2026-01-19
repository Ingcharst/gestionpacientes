# ✅ URLs PARA CAMBIO DE ESTADO
# Agregar a: apps/procedimientos/urls.py

from django.urls import path
from . import views

# Agregar estas líneas al urlpatterns existente:

urlpatterns = [
    # ... URLs existentes ...
    
    # ✅ NUEVAS URLs para gestión de valoraciones
    
    # Completar todas las valoraciones y cambiar estado
    path(
        'pacientes/<int:paciente_id>/valoraciones/completar/',
        views.completar_todas_valoraciones,
        name='completar_todas_valoraciones'
    ),
    
    # API para verificar estado de valoraciones
    path(
        'pacientes/<int:paciente_id>/valoraciones/verificar/',
        views.verificar_estado_valoraciones,
        name='verificar_estado_valoraciones'
    ),
    
    # Cambiar estado general del paciente
    path(
        'pacientes/<int:paciente_id>/cambiar-estado/',
        views.cambiar_estado_paciente,
        name='cambiar_estado_paciente'
    ),
]


# ============================================
# EJEMPLO COMPLETO DE URLS
# ============================================

"""
URLs completas del archivo urls.py:

urlpatterns = [
    # Pacientes existentes
    path('pacientes/', views.paciente_lista, name='paciente_list'),
    path('pacientes/pendientes-valoracion/', views.pacientes_pendientes_valoracion, name='pacientes_pendientes_valoracion'),
    
    # ✅ AGREGAR ESTAS URLs:
    path('pacientes/<int:paciente_id>/valoraciones/completar/', views.completar_todas_valoraciones, name='completar_todas_valoraciones'),
    path('pacientes/<int:paciente_id>/valoraciones/verificar/', views.verificar_estado_valoraciones, name='verificar_estado_valoraciones'),
    path('pacientes/<int:paciente_id>/cambiar-estado/', views.cambiar_estado_paciente, name='cambiar_estado_paciente'),
    
    # ... resto de URLs ...
]
"""
