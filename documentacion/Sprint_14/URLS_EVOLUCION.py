# URLs: EVOLUCIONES
# Archivo: apps/procedimientos/urls.py
# AGREGAR estas URLs a urlpatterns

urlpatterns = [
    # ... URLs existentes ...
    
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
