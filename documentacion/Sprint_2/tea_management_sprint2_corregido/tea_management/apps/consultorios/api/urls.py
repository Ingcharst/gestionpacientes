"""
URLs para la API de consultorios.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConsultorioViewSet,
    SalaViewSet,
    AsignacionConsultorioViewSet,
    DisponibilidadConsultorioViewSet
)

# Crear router para los ViewSets
router = DefaultRouter()
router.register(r'', ConsultorioViewSet, basename='consultorio')
router.register(r'salas', SalaViewSet, basename='sala')
router.register(r'asignaciones', AsignacionConsultorioViewSet, basename='asignacion')
router.register(r'disponibilidades', DisponibilidadConsultorioViewSet, basename='disponibilidad')

# URLs de la API
urlpatterns = [
    path('', include(router.urls)),
]
