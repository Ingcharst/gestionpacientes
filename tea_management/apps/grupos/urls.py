"""
URLs para gestión de grupos terapéuticos.
"""
from django.urls import path
from . import views


app_name = 'grupos'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard_grupos, name='dashboard'),
    
    # Grupos
    path('', views.grupo_lista, name='grupo_list'),
    path('<int:pk>/', views.grupo_detalle, name='grupo_detail'),
    path('crear/', views.grupo_crear, name='grupo_create'),
    path('<int:pk>/editar/', views.grupo_editar, name='grupo_edit'),
    
    # Asignaciones
    path('asignar/', views.asignar_paciente_grupo, name='asignar_paciente'),
    path('asignar/<int:paciente_pk>/<int:grupo_id>/', views.asignar_paciente_grupo, name='asignar_paciente_especifico'),
    path('asignacion/<int:asignacion_pk>/liberar/', views.liberar_paciente, name='liberar_paciente'),

    # Gestión de múltiples grupos por paciente
    path('paciente/<int:paciente_id>/grupos/', views.paciente_grupos, name='paciente_grupos'),
    path('paciente/<int:paciente_id>/agregar-grupo/', views.agregar_grupo_paciente, name='agregar_grupo_paciente'),
    path('asignacion/<int:asignacion_id>/eliminar/', views.eliminar_asignacion_grupo, name='eliminar_asignacion'),
    path('asignacion/<int:asignacion_id>/cambiar-grupo/', views.cambiar_grupo_paciente, name='cambiar_grupo_paciente'),

    # Pacientes Pendientes
    path('pendientes/', views.pacientes_pendientes_lista, name='pacientes_pendientes'),

    # Recomendaciones principales
    path('paciente/<int:paciente_id>/recomendar-grupos/', views.recomendar_grupos_paciente, name='recomendar_grupos_paciente'),

    # Asignar desde recomendación
    path('paciente/<int:paciente_id>/asignar-grupo/<int:grupo_id>/', views.asignar_desde_recomendacion, name='asignar_desde_recomendacion'),
    
    # Exportar recomendaciones a PDF
    path('paciente/<int:paciente_id>/exportar-recomendaciones/', views.exportar_recomendaciones, name='exportar_recomendaciones'),
    
    # Debug (solo para staff)
    path('debug/paciente/<int:paciente_id>/grupo/<int:grupo_id>/', views.debug_recomendacion, name='debug_recomendacion'),
]