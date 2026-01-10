"""
URLs para la API de usuarios.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, PerfilViewSet, RegistroAccesoViewSet

# Crear router para los ViewSets
router = DefaultRouter()
router.register(r'', UsuarioViewSet, basename='usuario')
router.register(r'perfiles', PerfilViewSet, basename='perfil')
router.register(r'accesos', RegistroAccesoViewSet, basename='acceso')

# URLs de la API
urlpatterns = [
    path('', include(router.urls)),
]
