"""
ViewSets para la API de terapias.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Avg, Count, Q
from decimal import Decimal

from apps.terapias.models import CategoriaTerapia, Terapia
from .serializers import (
    CategoriaTerapiaSerializer,
    TerapiaListSerializer,
    TerapiaDetailSerializer,
    TerapiaCreateSerializer,
    TerapiaBusquedaSerializer,
    EstadisticasTerapiasSerializer
)
from apps.usuarios.api.permissions import IsAdminOrReadOnly


class CategoriaTerapiaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de categorías de terapias.
    
    Endpoints:
    - GET /api/terapias/categorias/ - Lista todas las categorías
    - POST /api/terapias/categorias/ - Crea una nueva categoría
    - GET /api/terapias/categorias/{id}/ - Detalle de una categoría
    - PUT /api/terapias/categorias/{id}/ - Actualiza una categoría
    - DELETE /api/terapias/categorias/{id}/ - Elimina una categoría
    - GET /api/terapias/categorias/con_terapias/ - Categorías con terapias
    """
    
    queryset = CategoriaTerapia.objects.all()
    serializer_class = CategoriaTerapiaSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre', 'codigo', 'descripcion']
    ordering_fields = ['orden', 'nombre']
    ordering = ['orden', 'nombre']
    
    @action(detail=False, methods=['get'])
    def con_terapias(self, request):
        """Lista categorías que tienen terapias activas."""
        categorias = self.queryset.filter(
            terapias__activo=True
        ).distinct()
        
        serializer = self.get_serializer(categorias, many=True)
        return Response(serializer.data)


class TerapiaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de terapias.
    
    Endpoints:
    - GET /api/terapias/ - Lista todas las terapias
    - POST /api/terapias/ - Crea una nueva terapia
    - GET /api/terapias/{id}/ - Detalle de una terapia
    - PUT /api/terapias/{id}/ - Actualiza una terapia
    - DELETE /api/terapias/{id}/ - Elimina una terapia
    - GET /api/terapias/destacadas/ - Lista terapias destacadas
    - GET /api/terapias/por_categoria/ - Agrupa por categoría
    - POST /api/terapias/busqueda_avanzada/ - Búsqueda avanzada
    - GET /api/terapias/{id}/calcular_costo_mensual/ - Calcula costo mensual
    - GET /api/terapias/estadisticas/ - Estadísticas generales
    """
    
    queryset = Terapia.objects.select_related('categoria').all()
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'categoria', 'modalidad', 'especialidad',
        'nivel_intensidad', 'activo', 'destacado',
        'requiere_evaluacion_previa', 'requiere_orden_medica',
        'disponible_online', 'disponible_domicilio'
    ]
    search_fields = [
        'nombre', 'codigo', 'descripcion',
        'descripcion_corta', 'objetivos', 'beneficios'
    ]
    ordering_fields = [
        'nombre', 'codigo', 'costo_sesion',
        'duracion_minutos', 'orden'
    ]
    ordering = ['categoria', 'orden', 'nombre']
    
    def get_serializer_class(self):
        """Retorna el serializador apropiado según la acción."""
        if self.action == 'list':
            return TerapiaListSerializer
        elif self.action == 'create':
            return TerapiaCreateSerializer
        return TerapiaDetailSerializer
    
    @action(detail=False, methods=['get'])
    def destacadas(self, request):
        """Lista solo terapias destacadas."""
        terapias = self.queryset.filter(
            activo=True,
            destacado=True
        )
        
        page = self.paginate_queryset(terapias)
        if page is not None:
            serializer = TerapiaListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TerapiaListSerializer(terapias, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_categoria(self, request):
        """Agrupa terapias por categoría."""
        categoria_id = request.query_params.get('categoria', None)
        
        if categoria_id:
            terapias = self.queryset.filter(categoria_id=categoria_id, activo=True)
            serializer = TerapiaListSerializer(terapias, many=True)
            return Response(serializer.data)
        
        # Agrupar todas por categoría
        categorias = {}
        for categoria in CategoriaTerapia.objects.filter(activo=True):
            terapias = self.queryset.filter(categoria=categoria, activo=True)
            categorias[categoria.nombre] = TerapiaListSerializer(terapias, many=True).data
        
        return Response(categorias)
    
    @action(detail=False, methods=['post'])
    def busqueda_avanzada(self, request):
        """Búsqueda avanzada de terapias con múltiples filtros."""
        serializer = TerapiaBusquedaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        terapias = self.queryset.filter(activo=True)
        
        # Filtros
        categoria = serializer.validated_data.get('categoria')
        modalidad = serializer.validated_data.get('modalidad')
        especialidad = serializer.validated_data.get('especialidad')
        edad = serializer.validated_data.get('edad')
        costo_maximo = serializer.validated_data.get('costo_maximo')
        duracion_minima = serializer.validated_data.get('duracion_minima')
        duracion_maxima = serializer.validated_data.get('duracion_maxima')
        online = serializer.validated_data.get('online')
        domicilio = serializer.validated_data.get('domicilio')
        solo_destacadas = serializer.validated_data.get('solo_destacadas')
        search = serializer.validated_data.get('search')
        
        if categoria:
            terapias = terapias.filter(categoria_id=categoria)
        
        if modalidad:
            terapias = terapias.filter(modalidad=modalidad)
        
        if especialidad:
            terapias = terapias.filter(especialidad=especialidad)
        
        if edad is not None:
            terapias = terapias.filter(
                Q(edad_minima__isnull=True) | Q(edad_minima__lte=edad)
            ).filter(
                Q(edad_maxima__isnull=True) | Q(edad_maxima__gte=edad)
            )
        
        if costo_maximo is not None:
            terapias = terapias.filter(costo_sesion__lte=costo_maximo)
        
        if duracion_minima is not None:
            terapias = terapias.filter(duracion_minutos__gte=duracion_minima)
        
        if duracion_maxima is not None:
            terapias = terapias.filter(duracion_minutos__lte=duracion_maxima)
        
        if online:
            terapias = terapias.filter(disponible_online=True)
        
        if domicilio:
            terapias = terapias.filter(disponible_domicilio=True)
        
        if solo_destacadas:
            terapias = terapias.filter(destacado=True)
        
        if search:
            terapias = terapias.filter(
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search) |
                Q(descripcion_corta__icontains=search)
            )
        
        page = self.paginate_queryset(terapias)
        if page is not None:
            result_serializer = TerapiaListSerializer(page, many=True)
            return self.get_paginated_response(result_serializer.data)
        
        result_serializer = TerapiaListSerializer(terapias, many=True)
        return Response(result_serializer.data)
    
    @action(detail=True, methods=['get'])
    def calcular_costo_mensual(self, request, pk=None):
        """Calcula el costo mensual de una terapia."""
        terapia = self.get_object()
        sesiones_por_mes = request.query_params.get('sesiones', None)
        
        if sesiones_por_mes:
            try:
                sesiones_por_mes = int(sesiones_por_mes)
            except ValueError:
                return Response(
                    {'error': 'El parámetro sesiones debe ser un número entero.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        costo_mensual = terapia.calcular_costo_mensual(sesiones_por_mes)
        
        return Response({
            'terapia': terapia.nombre,
            'costo_mensual': float(costo_mensual),
            'sesiones_por_mes': sesiones_por_mes or (terapia.frecuencia_semanal_recomendada * 4),
            'costo_por_sesion': float(terapia.costo_sesion)
        })
    
    @action(detail=True, methods=['get'])
    def verificar_edad(self, request, pk=None):
        """Verifica si la terapia es apta para una edad específica."""
        terapia = self.get_object()
        edad = request.query_params.get('edad')
        
        if not edad:
            return Response(
                {'error': 'Se requiere el parámetro edad.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            edad = int(edad)
        except ValueError:
            return Response(
                {'error': 'La edad debe ser un número entero.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        es_apto = terapia.es_apto_para_edad(edad)
        
        return Response({
            'terapia': terapia.nombre,
            'edad': edad,
            'es_apto': es_apto,
            'rango_edad': terapia.rango_edad
        })
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Retorna estadísticas de terapias."""
        total = self.queryset.count()
        activas = self.queryset.filter(activo=True).count()
        destacadas = self.queryset.filter(activo=True, destacado=True).count()
        
        # Por categoría
        por_categoria = {}
        for cat in CategoriaTerapia.objects.filter(activo=True):
            count = self.queryset.filter(categoria=cat, activo=True).count()
            por_categoria[cat.nombre] = count
        
        # Por especialidad
        por_especialidad = {}
        for choice in Terapia.Especialidad.choices:
            esp_key = choice[0]
            esp_label = choice[1]
            count = self.queryset.filter(especialidad=esp_key, activo=True).count()
            if count > 0:
                por_especialidad[esp_label] = count
        
        # Por modalidad
        por_modalidad = {}
        for choice in Terapia.Modalidad.choices:
            mod_key = choice[0]
            mod_label = choice[1]
            count = self.queryset.filter(modalidad=mod_key, activo=True).count()
            if count > 0:
                por_modalidad[mod_label] = count
        
        # Promedios
        promedios = self.queryset.filter(activo=True).aggregate(
            costo_promedio=Avg('costo_sesion'),
            duracion_promedio=Avg('duracion_minutos')
        )
        
        data = {
            'total_terapias': total,
            'terapias_activas': activas,
            'terapias_destacadas': destacadas,
            'por_categoria': por_categoria,
            'por_especialidad': por_especialidad,
            'por_modalidad': por_modalidad,
            'costo_promedio': promedios['costo_promedio'] or Decimal('0.00'),
            'duracion_promedio': int(promedios['duracion_promedio'] or 0)
        }
        
        serializer = EstadisticasTerapiasSerializer(data)
        return Response(serializer.data)
