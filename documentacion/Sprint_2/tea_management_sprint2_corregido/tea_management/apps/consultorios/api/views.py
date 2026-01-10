"""
ViewSets para la API de consultorios.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Q
from django.utils import timezone

from apps.consultorios.models import (
    Consultorio, Sala, AsignacionConsultorio, DisponibilidadConsultorio
)
from .serializers import (
    ConsultorioListSerializer,
    ConsultorioDetailSerializer,
    ConsultorioCreateSerializer,
    SalaSerializer,
    AsignacionConsultorioSerializer,
    AsignacionConsultorioDetailSerializer,
    DisponibilidadConsultorioSerializer,
    ConsultorioDisponibilidadQuerySerializer,
    EstadisticasConsultoriosSerializer
)
from apps.usuarios.api.permissions import IsAdminOrReadOnly, IsCoordinadorOrAdmin


class ConsultorioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de consultorios.
    
    Endpoints:
    - GET /api/consultorios/ - Lista todos los consultorios
    - POST /api/consultorios/ - Crea un nuevo consultorio
    - GET /api/consultorios/{id}/ - Detalle de un consultorio
    - PUT /api/consultorios/{id}/ - Actualiza un consultorio
    - PATCH /api/consultorios/{id}/ - Actualización parcial
    - DELETE /api/consultorios/{id}/ - Elimina un consultorio
    - GET /api/consultorios/disponibles/ - Lista consultorios disponibles
    - GET /api/consultorios/por_tipo/ - Agrupa por tipo
    - POST /api/consultorios/{id}/agregar_equipo/ - Agrega equipamiento
    - GET /api/consultorios/estadisticas/ - Estadísticas generales
    """
    
    queryset = Consultorio.objects.prefetch_related('salas', 'asignaciones').all()
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tipo', 'estado', 'piso', 'activo']
    search_fields = ['nombre', 'codigo', 'numero', 'caracteristicas']
    ordering_fields = ['codigo', 'nombre', 'piso', 'numero', 'capacidad']
    ordering = ['piso', 'numero']
    
    def get_serializer_class(self):
        """Retorna el serializador apropiado según la acción."""
        if self.action == 'list':
            return ConsultorioListSerializer
        elif self.action == 'create':
            return ConsultorioCreateSerializer
        return ConsultorioDetailSerializer
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """Lista solo consultorios disponibles."""
        consultorios = self.queryset.filter(
            estado=Consultorio.EstadoConsultorio.DISPONIBLE,
            activo=True
        )
        
        page = self.paginate_queryset(consultorios)
        if page is not None:
            serializer = ConsultorioListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ConsultorioListSerializer(consultorios, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """Agrupa consultorios por tipo."""
        tipo = request.query_params.get('tipo', None)
        
        if tipo:
            consultorios = self.queryset.filter(tipo=tipo, activo=True)
            serializer = ConsultorioListSerializer(consultorios, many=True)
            return Response(serializer.data)
        
        # Agrupar todos por tipo
        tipos = {}
        for choice in Consultorio.TipoConsultorio.choices:
            tipo_key = choice[0]
            tipo_label = choice[1]
            consultorios = self.queryset.filter(tipo=tipo_key, activo=True)
            tipos[tipo_label] = ConsultorioListSerializer(consultorios, many=True).data
        
        return Response(tipos)
    
    @action(detail=True, methods=['post'])
    def agregar_equipo(self, request, pk=None):
        """Agrega equipamiento al consultorio."""
        consultorio = self.get_object()
        
        nombre = request.data.get('nombre')
        cantidad = request.data.get('cantidad', 1)
        
        if not nombre:
            return Response(
                {'detail': 'Se requiere el nombre del equipo.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        consultorio.agregar_equipo(nombre, cantidad)
        
        return Response(
            {'detail': 'Equipamiento agregado exitosamente.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Cambia el estado del consultorio."""
        consultorio = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if nuevo_estado not in dict(Consultorio.EstadoConsultorio.choices):
            return Response(
                {'detail': 'Estado no válido.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        consultorio.estado = nuevo_estado
        consultorio.save()
        
        return Response(
            {'detail': f'Estado cambiado a {consultorio.get_estado_display()}.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Retorna estadísticas de consultorios."""
        total = self.queryset.filter(activo=True).count()
        disponibles = self.queryset.filter(
            estado=Consultorio.EstadoConsultorio.DISPONIBLE,
            activo=True
        ).count()
        ocupados = self.queryset.filter(
            estado=Consultorio.EstadoConsultorio.OCUPADO,
            activo=True
        ).count()
        mantenimiento = self.queryset.filter(
            estado=Consultorio.EstadoConsultorio.MANTENIMIENTO,
            activo=True
        ).count()
        
        # Por tipo
        por_tipo = {}
        for choice in Consultorio.TipoConsultorio.choices:
            tipo_key = choice[0]
            tipo_label = choice[1]
            count = self.queryset.filter(tipo=tipo_key, activo=True).count()
            por_tipo[tipo_label] = count
        
        # Por piso
        pisos = self.queryset.filter(activo=True).values_list('piso', flat=True).distinct()
        por_piso = {}
        for piso in pisos:
            count = self.queryset.filter(piso=piso, activo=True).count()
            por_piso[f'Piso {piso}'] = count
        
        # Tasa de ocupación
        tasa_ocupacion = (ocupados / total * 100) if total > 0 else 0
        
        data = {
            'total_consultorios': total,
            'consultorios_disponibles': disponibles,
            'consultorios_ocupados': ocupados,
            'consultorios_mantenimiento': mantenimiento,
            'por_tipo': por_tipo,
            'por_piso': por_piso,
            'tasa_ocupacion': round(tasa_ocupacion, 2)
        }
        
        serializer = EstadisticasConsultoriosSerializer(data)
        return Response(serializer.data)


class SalaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de salas.
    
    Endpoints:
    - GET /api/consultorios/salas/ - Lista todas las salas
    - POST /api/consultorios/salas/ - Crea una nueva sala
    - GET /api/consultorios/salas/{id}/ - Detalle de una sala
    - PUT /api/consultorios/salas/{id}/ - Actualiza una sala
    - DELETE /api/consultorios/salas/{id}/ - Elimina una sala
    """
    
    queryset = Sala.objects.select_related('consultorio').all()
    serializer_class = SalaSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['consultorio', 'tipo', 'activo']
    search_fields = ['nombre', 'descripcion', 'consultorio__nombre']
    ordering = ['consultorio', 'nombre']


class AsignacionConsultorioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de asignaciones de consultorios.
    
    Endpoints:
    - GET /api/consultorios/asignaciones/ - Lista asignaciones
    - POST /api/consultorios/asignaciones/ - Crea asignación
    - GET /api/consultorios/asignaciones/{id}/ - Detalle de asignación
    - PUT /api/consultorios/asignaciones/{id}/ - Actualiza asignación
    - DELETE /api/consultorios/asignaciones/{id}/ - Elimina asignación
    - GET /api/consultorios/asignaciones/vigentes/ - Asignaciones vigentes
    - GET /api/consultorios/asignaciones/por_terapeuta/ - Por terapeuta
    - GET /api/consultorios/asignaciones/mis_asignaciones/ - Mis asignaciones
    """
    
    queryset = AsignacionConsultorio.objects.select_related(
        'consultorio', 'terapeuta'
    ).all()
    permission_classes = [IsAuthenticated, IsCoordinadorOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['consultorio', 'terapeuta', 'tipo_asignacion', 'activo']
    search_fields = [
        'consultorio__nombre', 'consultorio__codigo',
        'terapeuta__first_name', 'terapeuta__last_name'
    ]
    ordering_fields = ['fecha_inicio', 'fecha_fin', 'prioridad']
    ordering = ['-fecha_inicio']
    
    def get_serializer_class(self):
        """Retorna el serializador apropiado."""
        if self.action == 'retrieve':
            return AsignacionConsultorioDetailSerializer
        return AsignacionConsultorioSerializer
    
    @action(detail=False, methods=['get'])
    def vigentes(self, request):
        """Lista solo asignaciones vigentes."""
        hoy = timezone.now().date()
        asignaciones = self.queryset.filter(
            activo=True,
            fecha_inicio__lte=hoy
        ).filter(
            Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=hoy)
        )
        
        page = self.paginate_queryset(asignaciones)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(asignaciones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_terapeuta(self, request):
        """Agrupa asignaciones por terapeuta."""
        terapeuta_id = request.query_params.get('terapeuta', None)
        
        if not terapeuta_id:
            return Response(
                {'detail': 'Se requiere el ID del terapeuta.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        asignaciones = self.queryset.filter(
            terapeuta_id=terapeuta_id,
            activo=True
        )
        
        serializer = self.get_serializer(asignaciones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mis_asignaciones(self, request):
        """Retorna las asignaciones del terapeuta autenticado."""
        if not request.user.es_terapeuta:
            return Response(
                {'detail': 'Solo los terapeutas pueden acceder a esta función.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        asignaciones = self.queryset.filter(
            terapeuta=request.user,
            activo=True
        )
        
        serializer = self.get_serializer(asignaciones, many=True)
        return Response(serializer.data)


class DisponibilidadConsultorioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de disponibilidad de consultorios.
    
    Endpoints:
    - GET /api/consultorios/disponibilidades/ - Lista disponibilidades
    - POST /api/consultorios/disponibilidades/ - Crea disponibilidad
    - GET /api/consultorios/disponibilidades/{id}/ - Detalle
    - PUT /api/consultorios/disponibilidades/{id}/ - Actualiza
    - DELETE /api/consultorios/disponibilidades/{id}/ - Elimina
    - GET /api/consultorios/disponibilidades/por_fecha/ - Por fecha
    - POST /api/consultorios/disponibilidades/consultar/ - Consultar disponibilidad
    """
    
    queryset = DisponibilidadConsultorio.objects.select_related(
        'consultorio', 'terapeuta'
    ).all()
    serializer_class = DisponibilidadConsultorioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['consultorio', 'fecha', 'estado', 'terapeuta']
    search_fields = ['consultorio__nombre', 'consultorio__codigo']
    ordering_fields = ['fecha', 'hora_inicio']
    ordering = ['-fecha', 'hora_inicio']
    
    @action(detail=False, methods=['get'])
    def por_fecha(self, request):
        """Lista disponibilidades por rango de fechas."""
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin', fecha_inicio)
        
        if not fecha_inicio:
            return Response(
                {'detail': 'Se requiere fecha_inicio.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        disponibilidades = self.queryset.filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin
        )
        
        page = self.paginate_queryset(disponibilidades)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(disponibilidades, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def consultar(self, request):
        """Consulta disponibilidad de consultorios con filtros avanzados."""
        serializer = ConsultorioDisponibilidadQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        fecha_inicio = serializer.validated_data['fecha_inicio']
        fecha_fin = serializer.validated_data.get('fecha_fin', fecha_inicio)
        hora_inicio = serializer.validated_data.get('hora_inicio')
        hora_fin = serializer.validated_data.get('hora_fin')
        tipo_consultorio = serializer.validated_data.get('tipo_consultorio')
        
        # Consultar disponibilidades
        disponibilidades = self.queryset.filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin,
            estado=DisponibilidadConsultorio.EstadoDisponibilidad.DISPONIBLE
        )
        
        if hora_inicio and hora_fin:
            disponibilidades = disponibilidades.filter(
                hora_inicio__lte=hora_inicio,
                hora_fin__gte=hora_fin
            )
        
        if tipo_consultorio:
            disponibilidades = disponibilidades.filter(
                consultorio__tipo=tipo_consultorio
            )
        
        result_serializer = self.get_serializer(disponibilidades, many=True)
        return Response(result_serializer.data)
