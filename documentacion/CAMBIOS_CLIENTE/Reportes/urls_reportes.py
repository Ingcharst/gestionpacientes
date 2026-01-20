# apps/reportes/urls.py

from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    # Informes de evolución
    path('informe/crear/<int:admision_id>/', 
         views.crear_informe_evolucion, 
         name='crear_informe'),
    
    path('informe/<int:pk>/', 
         views.informe_detail, 
         name='informe_detail'),
    
    path('informe/<int:pk>/pdf/', 
         views.descargar_pdf_informe, 
         name='descargar_pdf'),
    
    path('paciente/<int:paciente_id>/informes/', 
         views.lista_informes_paciente, 
         name='lista_informes_paciente'),
]
