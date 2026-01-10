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
    
    # Sesiones
    path('sesiones/', views.sesion_lista, name='sesion_list'),
    path('sesiones/crear/', views.sesion_crear, name='sesion_create'),
    path('sesiones/<int:pk>/', views.sesion_detalle, name='sesion_detail'),
    path('sesiones/<int:pk>/editar/', views.sesion_editar, name='sesion_update'),

    # Evolución (CRUD simple) - Añadido para dar soporte al 'evolucion_form.html'
    #path('evolucion/crear/', views.evolucion_crear, name='evolucion_create'),

    # Objetivos (CRUD simple) - Añadido para dar soporte al 'objetivo_form.html'
    #path('objetivos/crear/', views.objetivo_crear, name='objetivo_create'),

    # Procedimientos
    path('', views.procedimiento_lista, name='procedimiento_list'),
    path('crear/', views.procedimiento_crear, name='procedimiento_create'),

    # Búsqueda CIE-10
    path('api/cie10/buscar/', views.buscar_cie10, name='buscar_cie10'),
    path('api/cie10/<int:codigo_id>/', views.obtener_cie10, name='obtener_cie10'),

    # Evoluciones
    path('evolucion/crear/', views.crear_evolucion, name='crear_evolucion'),
    path('evolucion/crear/paciente/<int:paciente_id>/', views.crear_evolucion, name='crear_evolucion_paciente'),
    path('evolucion/crear/paciente/<int:paciente_id>/grupo/<int:grupo_id>/', views.crear_evolucion, name='crear_evolucion_grupo'),
    path('evolucion/<int:evolucion_id>/', views.detalle_evolucion, name='detalle_evolucion'),
    path('evolucion/<int:evolucion_id>/editar/', views.editar_evolucion, name='editar_evolucion'),
    path('evolucion/<int:evolucion_id>/firmar/', views.firmar_evolucion, name='firmar_evolucion'),
    path('evolucion/<int:evolucion_id>/eliminar/', views.eliminar_evolucion, name='eliminar_evolucion'),
    path('paciente/<int:paciente_id>/evoluciones/', views.evoluciones_paciente, name='evoluciones_paciente'),
    path('mis-evoluciones/', views.mis_evoluciones, name='mis_evoluciones'),
]
