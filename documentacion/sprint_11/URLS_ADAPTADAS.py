# URLS ADAPTADAS
# Archivo: apps/grupos/urls.py

# AGREGAR estas URLs a urlpatterns:

from django.urls import path
from . import views

app_name = 'grupos'

urlpatterns = [
    # ... URLs existentes ...
    
    # Gestión de múltiples grupos por paciente
    path('paciente/<int:paciente_id>/grupos/', 
         views.paciente_grupos, 
         name='paciente_grupos'),
    
    path('paciente/<int:paciente_id>/agregar-grupo/', 
         views.agregar_grupo_paciente, 
         name='agregar_grupo_paciente'),
    
    path('asignacion/<int:asignacion_id>/eliminar/', 
         views.eliminar_asignacion_grupo, 
         name='eliminar_asignacion'),
    
    path('asignacion/<int:asignacion_id>/cambiar-grupo/', 
         views.cambiar_grupo_paciente, 
         name='cambiar_grupo_paciente'),
]
