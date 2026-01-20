"""
URLs para el módulo de reportes.
"""
from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    # Dashboard principal
    path('', views.reportes_dashboard, name='dashboard'),
    
    # Informe Mensual por Paciente (Facturación)
    path('informe-mensual-paciente/', views.informe_mensual_paciente_form, name='informe_mensual_form'),
    path('informe-mensual-paciente/<int:paciente_id>/pdf/', views.generar_informe_mensual_paciente_pdf, name='informe_mensual_pdf'),
    path('informe-mensual-paciente/<int:paciente_id>/excel/', views.generar_informe_mensual_paciente_excel, name='informe_mensual_excel'),
    
    # Informe Trimestral de Avance
    path('informe-trimestral-avance/', views.informe_trimestral_avance_form, name='informe_trimestral_form'),
    path('informe-trimestral-avance/<int:paciente_id>/pdf/', views.generar_informe_trimestral_avance_pdf, name='informe_trimestral_pdf'),
    
    # Reporte de Asistencia
    path('asistencia/', views.reporte_asistencia_form, name='asistencia_form'),
    path('asistencia/pdf/', views.generar_reporte_asistencia_pdf, name='asistencia_pdf'),
    
    # Reporte de Terapeutas
    path('terapeutas/', views.reporte_terapeutas_form, name='terapeutas_form'),
    path('terapeutas/pdf/', views.generar_reporte_terapeutas_pdf, name='terapeutas_pdf'),
    
    # Reporte de Grupos
    path('grupos/', views.reporte_grupos, name='grupos'),
    path('grupos/pdf/', views.generar_reporte_grupos_pdf, name='grupos_pdf'),

    # Informes de evolución
    path('informe/crear/<int:admision_id>/', views.crear_informe_evolucion, name='crear_informe'),
    path('informe/<int:pk>/', views.informe_detail, name='informe_detail'),
    path('informe/<int:pk>/pdf/', views.descargar_pdf_informe, name='descargar_pdf'),
    path('paciente/<int:paciente_id>/informes/', views.lista_informes_paciente, name='lista_informes_paciente'),
]
