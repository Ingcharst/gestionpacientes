"""
URLs para el Sistema de Recomendación de Grupos
Agregar estas URLs a apps/grupos/urls.py
"""

from django.urls import path
from . import views

# Estas URLs deben agregarse al urlpatterns existente en apps/grupos/urls.py
urlpatterns_recomendador = [
    # Recomendaciones principales
    path(
        'paciente/<int:paciente_id>/recomendar-grupos/',
        views.recomendar_grupos_paciente,
        name='recomendar_grupos_paciente'
    ),
    
    # Asignar desde recomendación
    path(
        'paciente/<int:paciente_id>/asignar-grupo/<int:grupo_id>/',
        views.asignar_desde_recomendacion,
        name='asignar_desde_recomendacion'
    ),
    
    # Exportar recomendaciones a PDF
    path(
        'paciente/<int:paciente_id>/exportar-recomendaciones/',
        views.exportar_recomendaciones,
        name='exportar_recomendaciones'
    ),
    
    # Debug (solo para staff)
    path(
        'debug/paciente/<int:paciente_id>/grupo/<int:grupo_id>/',
        views.debug_recomendacion,
        name='debug_recomendacion'
    ),
]

# INSTRUCCIONES DE INTEGRACIÓN:
# 
# En apps/grupos/urls.py, agregar:
#
# from .views_recomendador import (
#     recomendar_grupos_paciente,
#     asignar_desde_recomendacion,
#     exportar_recomendaciones,
#     debug_recomendacion
# )
#
# Luego en el urlpatterns existente, agregar:
#
# urlpatterns = [
#     # ... URLs existentes ...
#     
#     # Recomendaciones de grupos (nuevo)
#     path('paciente/<int:paciente_id>/recomendar-grupos/',
#          recomendar_grupos_paciente, name='recomendar_grupos_paciente'),
#     path('paciente/<int:paciente_id>/asignar-grupo/<int:grupo_id>/',
#          asignar_desde_recomendacion, name='asignar_desde_recomendacion'),
#     path('paciente/<int:paciente_id>/exportar-recomendaciones/',
#          exportar_recomendaciones, name='exportar_recomendaciones'),
#     path('debug/paciente/<int:paciente_id>/grupo/<int:grupo_id>/',
#          debug_recomendacion, name='debug_recomendacion'),
# ]
