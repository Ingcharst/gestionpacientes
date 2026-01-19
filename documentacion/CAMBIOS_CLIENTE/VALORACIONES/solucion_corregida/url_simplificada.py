# ✅ URL PARA LA VISTA SIMPLIFICADA
# Agregar a: apps/procedimientos/urls.py

from django.urls import path
from . import views

# Agregar esta línea al urlpatterns existente:

urlpatterns = [
    # ... URLs existentes ...
    
    # ✅ NUEVA URL para completar valoraciones (simplificada)
    path(
        'pacientes/<int:paciente_id>/completar-valoraciones/',
        views.completar_valoraciones_paciente,
        name='completar_valoraciones_paciente'
    ),
    
    # ... resto de URLs ...
]


# ============================================
# EJEMPLO COMPLETO (REFERENCIA)
# ============================================

"""
urlpatterns = [
    # Pacientes
    path('pacientes/', views.paciente_lista, name='paciente_list'),
    path('pacientes/pendientes-valoracion/', views.pacientes_pendientes_valoracion, name='pacientes_pendientes_valoracion'),
    
    # ✅ AGREGAR ESTA URL:
    path('pacientes/<int:paciente_id>/completar-valoraciones/', views.completar_valoraciones_paciente, name='completar_valoraciones_paciente'),
    
    # Valoraciones
    path('pacientes/<int:pk>/valoraciones/', views.valoraciones_paciente, name='valoraciones_paciente'),
    
    # ... resto de URLs ...
]
"""
