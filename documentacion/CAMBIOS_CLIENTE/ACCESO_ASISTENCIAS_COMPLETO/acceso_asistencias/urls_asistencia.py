# ✅ URLs PARA ASISTENCIAS
# Agregar a: apps/grupos/urls.py

from django.urls import path
from . import views

app_name = 'grupos'

urlpatterns = [
    # ... URLs existentes ...
    
    # ✅ NUEVAS URLs para asistencias
    
    # Tomar asistencia de un grupo
    path(
        'grupos/<int:grupo_id>/asistencia/',
        views.control_asistencia_grupo,
        name='control_asistencia_grupo'
    ),
    
    # Mis grupos (terapeuta)
    path(
        'mis-grupos/',
        views.lista_grupos_terapeuta,
        name='mis_grupos'
    ),
    
    # Historial asistencia de un paciente
    path(
        'pacientes/<int:paciente_id>/historial-asistencia/',
        views.historial_asistencia_paciente,
        name='historial_asistencia_paciente'
    ),
]


# ================================================
# EJEMPLO COMPLETO DE urls.py
# ================================================

"""
from django.urls import path
from . import views

app_name = 'grupos'

urlpatterns = [
    # Grupos Terapéuticos
    path('', views.grupo_lista, name='grupo_lista'),
    path('grupos/crear/', views.grupo_crear, name='grupo_crear'),
    path('grupos/<int:pk>/', views.grupo_detalle, name='detalle_grupo'),
    path('grupos/<int:pk>/editar/', views.grupo_editar, name='grupo_editar'),
    
    # ✅ Asistencias
    path('grupos/<int:grupo_id>/asistencia/', views.control_asistencia_grupo, name='control_asistencia_grupo'),
    path('mis-grupos/', views.lista_grupos_terapeuta, name='mis_grupos'),
    path('pacientes/<int:paciente_id>/historial-asistencia/', views.historial_asistencia_paciente, name='historial_asistencia_paciente'),
]
"""
