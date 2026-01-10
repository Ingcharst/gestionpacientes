"""
ViewSets para la API de usuarios.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q

from apps.usuarios.models import Usuario, Perfil, RegistroAcceso
from .serializers import (
    UsuarioListSerializer,
    UsuarioDetailSerializer,
    UsuarioCreateSerializer,
    UsuarioUpdateSerializer,
    CambiarPasswordSerializer,
    PerfilSerializer,
    PerfilUpdateSerializer,
    RegistroAccesoSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de usuarios.
    
    Endpoints:
    - GET /api/usuarios/ - Lista todos los usuarios
    - POST /api/usuarios/ - Crea un nuevo usuario
    - GET /api/usuarios/{id}/ - Detalle de un usuario
    - PUT /api/usuarios/{id}/ - Actualiza un usuario
    - PATCH /api/usuarios/{id}/ - Actualización parcial
    - DELETE /api/usuarios/{id}/ - Elimina un usuario
    - POST /api/usuarios/{id}/cambiar_password/ - Cambiar contraseña
    - GET /api/usuarios/me/ - Obtiene el usuario actual
    - GET /api/usuarios/terapeutas/ - Lista solo terapeutas
    """
    
    queryset = Usuario.objects.select_related('perfil').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['rol', 'estado', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'cedula_profesional']
    ordering_fields = ['date_joined', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        """Retorna el serializador apropiado según la acción."""
        if self.action == 'list':
            return UsuarioListSerializer
        elif self.action == 'create':
            return UsuarioCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UsuarioUpdateSerializer
        elif self.action == 'cambiar_password':
            return CambiarPasswordSerializer
        return UsuarioDetailSerializer
    
    def get_permissions(self):
        """Define permisos según la acción."""
        if self.action == 'create':
            return [IsAuthenticated(), IsAdminOrReadOnly()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Retorna información del usuario autenticado."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def terapeutas(self, request):
        """Lista solo usuarios con rol de terapeuta."""
        terapeutas = self.queryset.filter(
            Q(rol=Usuario.Rol.TERAPEUTA) |
            Q(rol=Usuario.Rol.PSICOLOGO) |
            Q(rol=Usuario.Rol.MEDICO),
            estado=Usuario.EstadoUsuario.ACTIVO
        )
        
        page = self.paginate_queryset(terapeutas)
        if page is not None:
            serializer = UsuarioListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UsuarioListSerializer(terapeutas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cambiar_password(self, request, pk=None):
        """Permite cambiar la contraseña del usuario."""
        usuario = self.get_object()
        
        # Verificar que el usuario solo pueda cambiar su propia contraseña
        # o que sea administrador
        if request.user != usuario and not request.user.es_admin:
            return Response(
                {'detail': 'No tienes permiso para cambiar esta contraseña.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CambiarPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'detail': 'Contraseña actualizada exitosamente.'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activa un usuario inactivo."""
        usuario = self.get_object()
        usuario.estado = Usuario.EstadoUsuario.ACTIVO
        usuario.is_active = True
        usuario.save()
        
        return Response(
            {'detail': f'Usuario {usuario.username} activado exitosamente.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactiva un usuario."""
        usuario = self.get_object()
        usuario.estado = Usuario.EstadoUsuario.INACTIVO
        usuario.is_active = False
        usuario.save()
        
        return Response(
            {'detail': f'Usuario {usuario.username} desactivado exitosamente.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Retorna estadísticas de usuarios del sistema."""
        total = Usuario.objects.count()
        activos = Usuario.objects.filter(estado=Usuario.EstadoUsuario.ACTIVO).count()
        inactivos = Usuario.objects.filter(estado=Usuario.EstadoUsuario.INACTIVO).count()
        
        por_rol = {}
        for rol_key, rol_label in Usuario.Rol.choices:
            por_rol[rol_label] = Usuario.objects.filter(rol=rol_key).count()
        
        return Response({
            'total_usuarios': total,
            'usuarios_activos': activos,
            'usuarios_inactivos': inactivos,
            'usuarios_por_rol': por_rol
        })


class PerfilViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de perfiles profesionales.
    
    Endpoints:
    - GET /api/usuarios/perfiles/ - Lista todos los perfiles
    - GET /api/usuarios/perfiles/{id}/ - Detalle de un perfil
    - PUT /api/usuarios/perfiles/{id}/ - Actualiza un perfil
    - PATCH /api/usuarios/perfiles/{id}/ - Actualización parcial
    """
    
    queryset = Perfil.objects.select_related('usuario').all()
    serializer_class = PerfilSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['especialidades', 'disponible']
    search_fields = ['usuario__first_name', 'usuario__last_name', 'universidad']
    
    def get_serializer_class(self):
        """Retorna el serializador apropiado según la acción."""
        if self.action in ['update', 'partial_update']:
            return PerfilUpdateSerializer
        return PerfilSerializer
    
    def get_permissions(self):
        """Define permisos según la acción."""
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def mi_perfil(self, request):
        """Retorna el perfil del usuario autenticado."""
        perfil = request.user.perfil
        serializer = self.get_serializer(perfil)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def agregar_certificacion(self, request, pk=None):
        """Agrega una certificación al perfil."""
        perfil = self.get_object()
        
        nombre = request.data.get('nombre')
        institucion = request.data.get('institucion')
        fecha = request.data.get('fecha')
        
        if not all([nombre, institucion, fecha]):
            return Response(
                {'detail': 'Se requieren nombre, institución y fecha.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        perfil.agregar_certificacion(nombre, institucion, fecha)
        
        return Response(
            {'detail': 'Certificación agregada exitosamente.'},
            status=status.HTTP_200_OK
        )


class RegistroAccesoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consulta de registros de acceso (solo lectura).
    
    Endpoints:
    - GET /api/usuarios/accesos/ - Lista todos los registros
    - GET /api/usuarios/accesos/{id}/ - Detalle de un registro
    """
    
    queryset = RegistroAcceso.objects.select_related('usuario').all()
    serializer_class = RegistroAccesoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['usuario', 'tipo_acceso', 'exitoso']
    search_fields = ['usuario__username', 'ip_address']
    ordering_fields = ['fecha_hora']
    ordering = ['-fecha_hora']
    
    @action(detail=False, methods=['get'])
    def mis_accesos(self, request):
        """Retorna los registros de acceso del usuario autenticado."""
        accesos = self.queryset.filter(usuario=request.user)
        
        page = self.paginate_queryset(accesos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(accesos, many=True)
        return Response(serializer.data)
