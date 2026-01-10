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
    path('asignar/<int:paciente_pk>/', views.asignar_paciente_grupo, name='asignar_paciente_especifico'),
    path('asignacion/<int:asignacion_pk>/liberar/', views.liberar_paciente, name='liberar_paciente'),
    
    # Pacientes Pendientes
    path('pendientes/', views.pacientes_pendientes_lista, name='pacientes_pendientes'),
]
