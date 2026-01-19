"""
URLs para procedimientos (frontend).
"""
from django.urls import path
from apps.procedimientos import views

app_name = 'procedimientos'

urlpatterns = [
    # Pacientes
    path('pacientes/', views.paciente_lista, name='paciente_list'),
    path('pacientes/crear/', views.paciente_crear, name='paciente_create'),
    path('pacientes/<int:pk>/', views.paciente_detalle, name='paciente_detail'),
    path('pacientes/<int:pk>/editar/', views.paciente_editar, name='paciente_update'),
    
    # Sesiones
    path('sesiones/', views.sesion_lista, name='sesion_list'),
    path('sesiones/crear/', views.sesion_crear, name='sesion_create'),
    path('sesiones/<int:pk>/', views.sesion_detalle, name='sesion_detail'),
    path('sesiones/<int:pk>/editar/', views.sesion_editar, name='sesion_update'),
    
    # Procedimientos
    path('', views.procedimiento_lista, name='procedimiento_list'),
    path('crear/', views.procedimiento_crear, name='procedimiento_create'),
]
