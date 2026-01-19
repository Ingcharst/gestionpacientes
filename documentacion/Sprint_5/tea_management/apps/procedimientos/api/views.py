"""
ViewSets para la API de procedimientos.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.procedimientos.models import (
    Paciente, Procedimiento, SesionTerapeutica,
    ObjetivoTerapeutico, EvolucionPaciente
)
from apps.procedimientos.api.serializers import (
    PacienteListSerializer, PacienteDetailSerializer, PacienteCreateSerializer,
    ProcedimientoListSerializer, ProcedimientoDetailSerializer, ProcedimientoCreateSerializer,
    SesionTerapeuticaListSerializer, SesionTerapeuticaDetailSerializer, SesionTerapeuticaCreateSerializer,
    ObjetivoTerapeuticoSerializer, EvolucionPacienteSerializer,
    EstadisticasProcedimientosSerializer, AgendaSemanalSerializer
)
from apps.usuarios.api.permissions import IsAdminOrReadOnly, IsCoordinadorOrAdmin


class PacienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de pacientes.
    
    list: Listar todos los pacientes
    create: Crear un nuevo paciente
    retrieve: Obtener detalle de un paciente
    update: Actualizar un paciente
    partial_update: Actualización parcial de un paciente
    destroy: Eliminar un paciente
    """
    
    queryset = Paciente.objects.all()
    permission_classes = [IsAuthenticated, IsCoordinadorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'genero', 'tipo_documento']
    search_fields = ['nombres', 'apellidos', 'numero_documento', 'numero_historia_clinica']
    ordering_fields = ['fecha_ingreso', 'apellidos', 'fecha_nacimiento']
    ordering = ['-fecha_ingreso']
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == 'list':
            return PacienteListSerializer
        elif self.action == 'create':
            return PacienteCreateSerializer
        return PacienteDetailSerializer
    
    def perform_create(self, serializer):
        """Guardar el usuario que crea el paciente."""
        serializer.save(creado_por=self.request.user)
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Listar solo pacientes activos."""
        pacientes = self.queryset.filter(estado='ACTIVO')
        serializer = PacienteListSerializer(pacientes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def dar_alta(self, request, pk=None):
        """Dar de alta a un paciente."""
        paciente = self.get_object()
        motivo = request.data.get('motivo', '')
        paciente.dar_alta(motivo)
        serializer = self.get_serializer(paciente)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        """Obtener historial completo del paciente."""
        paciente = self.get_object()
        
        # Obtener procedimientos
        procedimientos = paciente.procedimientos.all()[:10]
        sesiones = paciente.sesiones.all()[:10]
        objetivos = paciente.objetivos_terapeuticos.all()
        evoluciones = paciente.evoluciones.all()[:10]
        
        data = {
            'paciente': PacienteDetailSerializer(paciente).data,
            'procedimientos': ProcedimientoListSerializer(procedimientos, many=True).data,
            'sesiones': SesionTerapeuticaListSerializer(sesiones, many=True).data,
            'objetivos': ObjetivoTerapeuticoSerializer(objetivos, many=True).data,
            'evoluciones': EvolucionPacienteSerializer(evoluciones, many=True).data,
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas generales de pacientes."""
        total = self.queryset.count()
        activos = self.queryset.filter(estado='ACTIVO').count()
        inactivos = self.queryset.filter(estado='INACTIVO').count()
        dados_alta = self.queryset.filter(estado='DADO_ALTA').count()
        
        # Estadísticas por edad
        hoy = timezone.now().date()
        ninos = self.queryset.filter(
            fecha_nacimiento__gte=hoy - timedelta(days=365*12)
        ).count()
        adolescentes = self.queryset.filter(
            fecha_nacimiento__gte=hoy - timedelta(days=365*18),
            fecha_nacimiento__lt=hoy - timedelta(days=365*12)
        ).count()
        
        data = {
            'total_pacientes': total,
            'activos': activos,
            'inactivos': inactivos,
            'dados_alta': dados_alta,
            'ninos': ninos,
            'adolescentes': adolescentes,
        }
        
        return Response(data)


class ProcedimientoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de procedimientos.
    """
    
    queryset = Procedimiento.objects.select_related('paciente', 'profesional', 'consultorio')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'estado', 'paciente', 'profesional', 'fecha', 'pagado']
    search_fields = ['codigo', 'paciente__nombres', 'paciente__apellidos', 'motivo_consulta']
    ordering_fields = ['fecha', 'hora_inicio', 'costo']
    ordering = ['-fecha', '-hora_inicio']
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == 'list':
            return ProcedimientoListSerializer
        elif self.action == 'create':
            return ProcedimientoCreateSerializer
        return ProcedimientoDetailSerializer
    
    def perform_create(self, serializer):
        """Guardar el usuario que crea el procedimiento."""
        serializer.save(creado_por=self.request.user)
    
    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """Completar un procedimiento."""
        procedimiento = self.get_object()
        procedimiento.completar()
        serializer = self.get_serializer(procedimiento)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancelar un procedimiento."""
        procedimiento = self.get_object()
        motivo = request.data.get('motivo', '')
        procedimiento.cancelar(motivo)
        serializer = self.get_serializer(procedimiento)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_fecha(self, request):
        """Filtrar procedimientos por rango de fechas."""
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        queryset = self.queryset
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mis_procedimientos(self, request):
        """Procedimientos del profesional actual."""
        procedimientos = self.queryset.filter(profesional=request.user)
        serializer = ProcedimientoListSerializer(procedimientos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_paciente(self, request):
        """Procedimientos de un paciente específico."""
        paciente_id = request.query_params.get('paciente_id')
        if not paciente_id:
            return Response(
                {'error': 'Se requiere el parámetro paciente_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        procedimientos = self.queryset.filter(paciente_id=paciente_id)
        serializer = ProcedimientoListSerializer(procedimientos, many=True)
        return Response(serializer.data)


class SesionTerapeuticaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de sesiones terapéuticas.
    """
    
    queryset = SesionTerapeutica.objects.select_related(
        'paciente', 'terapeuta', 'terapia', 'consultorio'
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'tipo_asistencia', 'paciente', 'terapeuta', 'terapia', 'fecha', 'pagado']
    search_fields = ['numero_sesion', 'paciente__nombres', 'paciente__apellidos', 'terapia__nombre']
    ordering_fields = ['fecha', 'hora_inicio', 'costo', 'desempeno_paciente']
    ordering = ['-fecha', '-hora_inicio']
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == 'list':
            return SesionTerapeuticaListSerializer
        elif self.action == 'create':
            return SesionTerapeuticaCreateSerializer
        return SesionTerapeuticaDetailSerializer
    
    def perform_create(self, serializer):
        """Guardar el usuario que crea la sesión."""
        serializer.save(creado_por=self.request.user)
    
    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """Completar una sesión."""
        sesion = self.get_object()
        observaciones = request.data.get('observaciones', '')
        sesion.completar(observaciones)
        serializer = self.get_serializer(sesion)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancelar una sesión."""
        sesion = self.get_object()
        motivo = request.data.get('motivo', '')
        sesion.cancelar(motivo)
        serializer = self.get_serializer(sesion)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reprogramar(self, request, pk=None):
        """Reprogramar una sesión."""
        sesion = self.get_object()
        nueva_fecha = request.data.get('fecha')
        nueva_hora = request.data.get('hora_inicio')
        motivo = request.data.get('motivo', '')
        
        if not nueva_fecha or not nueva_hora:
            return Response(
                {'error': 'Se requieren fecha y hora_inicio'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from datetime import datetime
        nueva_hora_obj = datetime.strptime(nueva_hora, '%H:%M:%S').time()
        
        nueva_sesion = sesion.reprogramar(nueva_fecha, nueva_hora_obj, motivo)
        serializer = self.get_serializer(nueva_sesion)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def mis_sesiones(self, request):
        """Sesiones del terapeuta actual."""
        sesiones = self.queryset.filter(terapeuta=request.user)
        serializer = SesionTerapeuticaListSerializer(sesiones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_paciente(self, request):
        """Sesiones de un paciente específico."""
        paciente_id = request.query_params.get('paciente_id')
        if not paciente_id:
            return Response(
                {'error': 'Se requiere el parámetro paciente_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sesiones = self.queryset.filter(paciente_id=paciente_id)
        serializer = SesionTerapeuticaListSerializer(sesiones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def agenda_semanal(self, request):
        """Agenda semanal de sesiones."""
        fecha_inicio = request.query_params.get('fecha_inicio', timezone.now().date())
        if isinstance(fecha_inicio, str):
            from datetime import datetime
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        
        fecha_fin = fecha_inicio + timedelta(days=7)
        
        sesiones = self.queryset.filter(
            fecha__gte=fecha_inicio,
            fecha__lt=fecha_fin
        )
        
        # Agrupar por fecha
        agenda = {}
        for i in range(7):
            fecha = fecha_inicio + timedelta(days=i)
            sesiones_dia = sesiones.filter(fecha=fecha)
            agenda[str(fecha)] = SesionTerapeuticaListSerializer(sesiones_dia, many=True).data
        
        return Response(agenda)
    
    @action(detail=False, methods=['get'])
    def pendientes_pago(self, request):
        """Sesiones pendientes de pago."""
        sesiones = self.queryset.filter(
            estado='COMPLETADA',
            pagado=False
        )
        serializer = SesionTerapeuticaListSerializer(sesiones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def reporte_asistencia(self, request):
        """Reporte de asistencia."""
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        queryset = self.queryset
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)
        
        total = queryset.count()
        asistio = queryset.filter(tipo_asistencia='ASISTIO').count()
        no_asistio = queryset.filter(tipo_asistencia='NO_ASISTIO').count()
        llego_tarde = queryset.filter(tipo_asistencia='LLEGO_TARDE').count()
        
        tasa_asistencia = (asistio / total * 100) if total > 0 else 0
        
        data = {
            'total_sesiones': total,
            'asistio': asistio,
            'no_asistio': no_asistio,
            'llego_tarde': llego_tarde,
            'tasa_asistencia': round(tasa_asistencia, 2)
        }
        
        return Response(data)


class ObjetivoTerapeuticoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de objetivos terapéuticos.
    """
    
    queryset = ObjetivoTerapeutico.objects.select_related('paciente', 'terapia')
    serializer_class = ObjetivoTerapeuticoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'prioridad', 'paciente', 'terapia']
    search_fields = ['titulo', 'descripcion', 'paciente__nombres', 'paciente__apellidos']
    ordering_fields = ['fecha_inicio', 'fecha_limite', 'prioridad', 'porcentaje_avance']
    ordering = ['-prioridad', '-fecha_inicio']
    
    def perform_create(self, serializer):
        """Guardar el usuario que crea el objetivo."""
        serializer.save(creado_por=self.request.user)
    
    @action(detail=True, methods=['post'])
    def marcar_logrado(self, request, pk=None):
        """Marcar objetivo como logrado."""
        objetivo = self.get_object()
        objetivo.marcar_logrado()
        serializer = self.get_serializer(objetivo)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def actualizar_avance(self, request, pk=None):
        """Actualizar porcentaje de avance."""
        objetivo = self.get_object()
        porcentaje = request.data.get('porcentaje')
        
        if porcentaje is None:
            return Response(
                {'error': 'Se requiere el parámetro porcentaje'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            porcentaje = int(porcentaje)
            objetivo.actualizar_avance(porcentaje)
            serializer = self.get_serializer(objetivo)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {'error': 'El porcentaje debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def por_paciente(self, request):
        """Objetivos de un paciente específico."""
        paciente_id = request.query_params.get('paciente_id')
        if not paciente_id:
            return Response(
                {'error': 'Se requiere el parámetro paciente_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        objetivos = self.queryset.filter(paciente_id=paciente_id)
        serializer = self.get_serializer(objetivos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def en_proceso(self, request):
        """Objetivos en proceso."""
        objetivos = self.queryset.filter(estado='EN_PROCESO')
        serializer = self.get_serializer(objetivos, many=True)
        return Response(serializer.data)


class EvolucionPacienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de evoluciones de pacientes.
    """
    
    queryset = EvolucionPaciente.objects.select_related('paciente', 'profesional', 'sesion')
    serializer_class = EvolucionPacienteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['paciente', 'profesional', 'fecha', 'tipo_nota']
    search_fields = ['titulo', 'contenido', 'paciente__nombres', 'paciente__apellidos']
    ordering_fields = ['fecha', 'fecha_creacion']
    ordering = ['-fecha', '-fecha_creacion']
    
    @action(detail=False, methods=['get'])
    def por_paciente(self, request):
        """Evoluciones de un paciente específico."""
        paciente_id = request.query_params.get('paciente_id')
        if not paciente_id:
            return Response(
                {'error': 'Se requiere el parámetro paciente_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        evoluciones = self.queryset.filter(paciente_id=paciente_id)
        serializer = self.get_serializer(evoluciones, many=True)
        return Response(serializer.data)


# ViewSet adicional para estadísticas generales
class EstadisticasViewSet(viewsets.ViewSet):
    """
    ViewSet para estadísticas generales del sistema.
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def generales(self, request):
        """Estadísticas generales."""
        # Procedimientos
        total_procedimientos = Procedimiento.objects.count()
        procedimientos_completados = Procedimiento.objects.filter(estado='COMPLETADO').count()
        procedimientos_cancelados = Procedimiento.objects.filter(estado='CANCELADO').count()
        procedimientos_programados = Procedimiento.objects.filter(estado='PROGRAMADO').count()
        
        # Pacientes
        total_pacientes = Paciente.objects.count()
        pacientes_activos = Paciente.objects.filter(estado='ACTIVO').count()
        
        # Sesiones
        total_sesiones = SesionTerapeutica.objects.count()
        sesiones_completadas = SesionTerapeutica.objects.filter(estado='COMPLETADA').count()
        sesiones_asistio = SesionTerapeutica.objects.filter(tipo_asistencia='ASISTIO').count()
        
        tasa_asistencia = (sesiones_asistio / total_sesiones * 100) if total_sesiones > 0 else 0
        
        # Desempeño promedio
        promedio_desempeno = SesionTerapeutica.objects.filter(
            desempeno_paciente__isnull=False
        ).aggregate(Avg('desempeno_paciente'))['desempeno_paciente__avg'] or 0
        
        # Ingresos
        ingresos_totales = Procedimiento.objects.filter(
            pagado=True
        ).aggregate(Sum('costo'))['costo__sum'] or Decimal('0.00')
        
        ingresos_pendientes = Procedimiento.objects.filter(
            pagado=False,
            estado='COMPLETADO'
        ).aggregate(Sum('costo'))['costo__sum'] or Decimal('0.00')
        
        data = {
            'total_procedimientos': total_procedimientos,
            'procedimientos_completados': procedimientos_completados,
            'procedimientos_cancelados': procedimientos_cancelados,
            'procedimientos_programados': procedimientos_programados,
            'total_pacientes': total_pacientes,
            'pacientes_activos': pacientes_activos,
            'total_sesiones': total_sesiones,
            'sesiones_completadas': sesiones_completadas,
            'tasa_asistencia': round(tasa_asistencia, 2),
            'promedio_desempeno': round(promedio_desempeno, 2),
            'ingresos_totales': float(ingresos_totales),
            'ingresos_pendientes': float(ingresos_pendientes),
        }
        
        serializer = EstadisticasProcedimientosSerializer(data)
        return Response(serializer.data)
