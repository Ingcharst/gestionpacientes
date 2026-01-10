"""
URLs para procedimientos (frontend).
"""
from django.urls import path
from apps.procedimientos import views

app_name = 'procedimientos'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Pacientes
    path('pacientes/', views.paciente_lista, name='paciente_lista'),
    path('pacientes/crear/', views.paciente_crear, name='paciente_crear'),
    path('pacientes/<int:pk>/', views.paciente_detalle, name='paciente_detalle'),
    path('pacientes/<int:pk>/editar/', views.paciente_editar, name='paciente_editar'),
    
    # Sesiones
    path('sesiones/', views.sesion_lista, name='sesion_lista'),
    path('sesiones/crear/', views.sesion_crear, name='sesion_crear'),
    path('sesiones/<int:pk>/', views.sesion_detalle, name='sesion_detalle'),
    path('sesiones/<int:pk>/editar/', views.sesion_editar, name='sesion_editar'),
]
