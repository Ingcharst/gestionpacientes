"""
Serializadores para la API de consultorios.
"""
from rest_framework import serializers
from django.utils import timezone
from apps.consultorios.models import (
    Consultorio, Sala, AsignacionConsultorio, DisponibilidadConsultorio
)
from apps.usuarios.api.serializers import UsuarioListSerializer


class SalaSerializer(serializers.ModelSerializer):
    """Serializador para salas."""
    
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    consultorio_nombre = serializers.CharField(source='consultorio.nombre', read_only=True)
    
    class Meta:
        model = Sala
        fields = [
            'id', 'consultorio', 'consultorio_nombre', 'nombre',
            'tipo', 'tipo_display', 'area_metros', 'descripcion',
            'equipamiento_especifico', 'activo', 'fecha_creacion'
        ]
        read_only_fields = ['id', 'fecha_creacion']


class ConsultorioListSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listados de consultorios."""
    
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    nombre_completo = serializers.CharField(read_only=True)
    esta_disponible = serializers.BooleanField(read_only=True)
    numero_salas = serializers.SerializerMethodField()
    
    class Meta:
        model = Consultorio
        fields = [
            'id', 'codigo', 'nombre', 'nombre_completo',
            'tipo', 'tipo_display', 'piso', 'numero',
            'capacidad', 'estado', 'estado_display',
            'esta_disponible', 'activo', 'numero_salas'
        ]
        read_only_fields = ['id']
    
    def get_numero_salas(self, obj):
        """Retorna el número de salas del consultorio."""
        return obj.salas.filter(activo=True).count()


class ConsultorioDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado para consultorios."""
    
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    nombre_completo = serializers.CharField(read_only=True)
    esta_disponible = serializers.BooleanField(read_only=True)
    tiene_equipamiento = serializers.BooleanField(read_only=True)
    salas = SalaSerializer(many=True, read_only=True)
    numero_asignaciones = serializers.SerializerMethodField()
    
    class Meta:
        model = Consultorio
        fields = [
            'id', 'codigo', 'nombre', 'nombre_completo',
            'tipo', 'tipo_display', 'piso', 'numero',
            'capacidad', 'area_metros', 'estado', 'estado_display',
            'equipamiento', 'caracteristicas', 'foto',
            'tiene_ventana', 'tiene_aire_acondicionado',
            'accesible_silla_ruedas', 'observaciones',
            'esta_disponible', 'tiene_equipamiento', 'activo',
            'salas', 'numero_asignaciones',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = [
            'id', 'fecha_creacion', 'fecha_actualizacion',
            'nombre_completo', 'esta_disponible', 'tiene_equipamiento'
        ]
    
    def get_numero_asignaciones(self, obj):
        """Retorna el número de asignaciones activas."""
        return obj.asignaciones.filter(activo=True).count()


class ConsultorioCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear consultorios."""
    
    class Meta:
        model = Consultorio
        fields = [
            'nombre', 'codigo', 'tipo', 'piso', 'numero',
            'capacidad', 'area_metros', 'equipamiento',
            'caracteristicas', 'foto', 'tiene_ventana',
            'tiene_aire_acondicionado', 'accesible_silla_ruedas',
            'observaciones', 'estado', 'activo'
        ]
    
    def validate_codigo(self, value):
        """Valida que el código sea único."""
        if Consultorio.objects.filter(codigo=value).exists():
            raise serializers.ValidationError("Este código ya está en uso.")
        return value
    
    def validate_capacidad(self, value):
        """Valida que la capacidad sea razonable."""
        if value < 1:
            raise serializers.ValidationError("La capacidad debe ser al menos 1.")
        if value > 50:
            raise serializers.ValidationError("La capacidad parece demasiado alta.")
        return value


class AsignacionConsultorioSerializer(serializers.ModelSerializer):
    """Serializador para asignaciones de consultorios."""
    
    consultorio_nombre = serializers.CharField(source='consultorio.nombre', read_only=True)
    consultorio_codigo = serializers.CharField(source='consultorio.codigo', read_only=True)
    terapeuta_nombre = serializers.CharField(source='terapeuta.get_full_name', read_only=True)
    tipo_asignacion_display = serializers.CharField(source='get_tipo_asignacion_display', read_only=True)
    esta_vigente = serializers.BooleanField(read_only=True)
    es_permanente = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AsignacionConsultorio
        fields = [
            'id', 'consultorio', 'consultorio_nombre', 'consultorio_codigo',
            'terapeuta', 'terapeuta_nombre', 'tipo_asignacion',
            'tipo_asignacion_display', 'fecha_inicio', 'fecha_fin',
            'horario', 'dias_semana', 'prioridad', 'notas',
            'activo', 'esta_vigente', 'es_permanente',
            'fecha_asignacion', 'fecha_actualizacion'
        ]
        read_only_fields = [
            'id', 'fecha_asignacion', 'fecha_actualizacion',
            'esta_vigente', 'es_permanente'
        ]
    
    def validate(self, data):
        """Validaciones personalizadas."""
        # Validar que el terapeuta sea realmente un terapeuta
        terapeuta = data.get('terapeuta')
        if terapeuta and not terapeuta.es_terapeuta:
            raise serializers.ValidationError({
                'terapeuta': 'Solo se pueden asignar terapeutas a consultorios.'
            })
        
        # Validar fechas
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        if fecha_fin and fecha_inicio and fecha_inicio > fecha_fin:
            raise serializers.ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })
        
        return data


class AsignacionConsultorioDetailSerializer(AsignacionConsultorioSerializer):
    """Serializador detallado para asignaciones con información completa."""
    
    consultorio_detail = ConsultorioListSerializer(source='consultorio', read_only=True)
    terapeuta_detail = UsuarioListSerializer(source='terapeuta', read_only=True)
    
    class Meta(AsignacionConsultorioSerializer.Meta):
        fields = AsignacionConsultorioSerializer.Meta.fields + [
            'consultorio_detail', 'terapeuta_detail'
        ]


class DisponibilidadConsultorioSerializer(serializers.ModelSerializer):
    """Serializador para disponibilidad de consultorios."""
    
    consultorio_nombre = serializers.CharField(source='consultorio.nombre', read_only=True)
    consultorio_codigo = serializers.CharField(source='consultorio.codigo', read_only=True)
    terapeuta_nombre = serializers.CharField(source='terapeuta.get_full_name', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    duracion_minutos = serializers.IntegerField(read_only=True)
    esta_disponible = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = DisponibilidadConsultorio
        fields = [
            'id', 'consultorio', 'consultorio_nombre', 'consultorio_codigo',
            'fecha', 'hora_inicio', 'hora_fin', 'duracion_minutos',
            'estado', 'estado_display', 'terapeuta', 'terapeuta_nombre',
            'motivo_bloqueo', 'notas', 'esta_disponible', 'fecha_creacion'
        ]
        read_only_fields = [
            'id', 'fecha_creacion', 'duracion_minutos', 'esta_disponible'
        ]
    
    def validate(self, data):
        """Validaciones personalizadas."""
        hora_inicio = data.get('hora_inicio')
        hora_fin = data.get('hora_fin')
        
        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise serializers.ValidationError({
                'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio.'
            })
        
        # Validar que no haya solapamiento de horarios
        consultorio = data.get('consultorio')
        fecha = data.get('fecha')
        
        if consultorio and fecha and hora_inicio and hora_fin:
            # Excluir la instancia actual si estamos editando
            queryset = DisponibilidadConsultorio.objects.filter(
                consultorio=consultorio,
                fecha=fecha
            )
            
            # Si estamos editando, excluir el objeto actual
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            # Verificar solapamiento
            solapamiento = queryset.filter(
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio
            ).exists()
            
            if solapamiento:
                raise serializers.ValidationError(
                    'Ya existe un horario que se solapa con el especificado.'
                )
        
        return data


class ConsultorioDisponibilidadQuerySerializer(serializers.Serializer):
    """Serializador para consultas de disponibilidad."""
    
    fecha_inicio = serializers.DateField(required=True)
    fecha_fin = serializers.DateField(required=False)
    hora_inicio = serializers.TimeField(required=False)
    hora_fin = serializers.TimeField(required=False)
    tipo_consultorio = serializers.ChoiceField(
        choices=Consultorio.TipoConsultorio.choices,
        required=False
    )
    
    def validate(self, data):
        """Validaciones."""
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        if fecha_fin and fecha_inicio > fecha_fin:
            raise serializers.ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })
        
        return data


class EstadisticasConsultoriosSerializer(serializers.Serializer):
    """Serializador para estadísticas de consultorios."""
    
    total_consultorios = serializers.IntegerField()
    consultorios_disponibles = serializers.IntegerField()
    consultorios_ocupados = serializers.IntegerField()
    consultorios_mantenimiento = serializers.IntegerField()
    por_tipo = serializers.DictField()
    por_piso = serializers.DictField()
    tasa_ocupacion = serializers.FloatField()
