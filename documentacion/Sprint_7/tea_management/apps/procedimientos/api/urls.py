"""
URLs para la API de procedimientos.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.procedimientos.api import views

router = DefaultRouter()
router.register(r'pacientes', views.PacienteViewSet, basename='paciente')
router.register(r'procedimientos', views.ProcedimientoViewSet, basename='procedimiento')
router.register(r'sesiones', views.SesionTerapeuticaViewSet, basename='sesion')
router.register(r'objetivos', views.ObjetivoTerapeuticoViewSet, basename='objetivo')
router.register(r'evoluciones', views.EvolucionPacienteViewSet, basename='evolucion')
router.register(r'estadisticas', views.EstadisticasViewSet, basename='estadisticas')

urlpatterns = [
    path('', include(router.urls)),
]
