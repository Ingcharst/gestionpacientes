"""
Permisos personalizados para la API de usuarios.
"""
from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permite escritura solo a administradores.
    Lectura permitida para usuarios autenticados.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return request.user and request.user.es_admin


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite acceso solo al propietario del recurso o a administradores.
    """
    
    def has_object_permission(self, request, view, obj):
        # Lectura permitida para todos los usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escritura permitida solo para el propietario o admin
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user or request.user.es_admin
        
        return obj == request.user or request.user.es_admin


class IsTerapeutaOrAdmin(permissions.BasePermission):
    """
    Permite acceso solo a terapeutas y administradores.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.es_terapeuta or request.user.es_admin)
        )


class IsCoordinadorOrAdmin(permissions.BasePermission):
    """
    Permite acceso solo a coordinadores y administradores.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.puede_gestionar_terapias or request.user.es_admin)
        )
