"""
URLs del frontend para consultorios.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Lista y gestión de consultorios
    path('', views.consultorio_list, name='consultorio_list'),
    path('crear/', views.consultorio_create, name='consultorio_create'),
    path('<int:pk>/', views.consultorio_detail, name='consultorio_detail'),
    path('<int:pk>/editar/', views.consultorio_update, name='consultorio_update'),
    path('<int:pk>/cambiar-estado/', views.consultorio_cambiar_estado, name='consultorio_cambiar_estado'),
    
    # Salas
    path('<int:consultorio_pk>/salas/crear/', views.sala_create, name='sala_create'),
    path('salas/<int:pk>/editar/', views.sala_update, name='sala_update'),
    
    # Asignaciones
    path('asignaciones/', views.asignacion_list, name='asignacion_list'),
    path('asignaciones/crear/', views.asignacion_create, name='asignacion_create'),
    path('asignaciones/<int:pk>/', views.asignacion_detail, name='asignacion_detail'),
    path('asignaciones/<int:pk>/editar/', views.asignacion_update, name='asignacion_update'),
    path('mis-consultorios/', views.mis_consultorios, name='mis_consultorios'),
    
    # Disponibilidad
    path('disponibilidad/', views.disponibilidad_list, name='disponibilidad_list'),
    path('disponibilidad/crear/', views.disponibilidad_create, name='disponibilidad_create'),
    path('disponibilidad/<int:pk>/editar/', views.disponibilidad_update, name='disponibilidad_update'),
    path('disponibilidad/calendario/', views.calendario_disponibilidad, name='calendario_disponibilidad'),
    
    # Estadísticas
    path('estadisticas/', views.estadisticas_consultorios, name='estadisticas_consultorios'),
]
