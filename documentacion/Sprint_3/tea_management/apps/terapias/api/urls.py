"""
URLs para la API de terapias.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaTerapiaViewSet, TerapiaViewSet

# Crear router para los ViewSets
router = DefaultRouter()
router.register(r'categorias', CategoriaTerapiaViewSet, basename='categoria')
router.register(r'', TerapiaViewSet, basename='terapia')

# URLs de la API
urlpatterns = [
    path('', include(router.urls)),
]
