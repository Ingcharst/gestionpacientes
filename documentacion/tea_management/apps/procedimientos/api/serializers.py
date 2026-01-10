"""
Serializadores para la API de procedimientos.
"""
from rest_framework import serializers
from apps.procedimientos.models import (
    Paciente, Procedimiento, SesionTerapeutica, 
    ObjetivoTerapeutico, EvolucionPaciente
)
from apps.usuarios.api.serializers import UsuarioListSerializer
from apps.consultorios.api.serializers import ConsultorioListSerializer
from apps.terapias.api.serializers import TerapiaListSerializer


class PacienteListSerializer(serializers.ModelSerializer):
    """Serializer para listado de pacientes."""
    
    nombre_completo = serializers.CharField(read_only=True)
    edad = serializers.IntegerField(read_only=True)
    esta_activo = serializers.BooleanField(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Paciente
        fields = [
            'id', 'numero_historia_clinica', 'nombre_completo', 'nombres', 'apellidos',
            'numero_documento', 'fecha_nacimiento', 'edad', 'genero', 
            'telefono', 'estado', 'estado_display', 'esta_activo',
            'diagnostico_principal', 'fecha_ingreso'
        ]


class PacienteDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado de paciente."""
    
    nombre_completo = serializers.CharField(read_only=True)
    edad = serializers.IntegerField(read_only=True)
    edad_meses = serializers.IntegerField(read_only=True)
    esta_activo = serializers.BooleanField(read_only=True)
    tiene_alergias = serializers.BooleanField(read_only=True)
    tiene_medicamentos = serializers.BooleanField(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    tipo_documento_display = serializers.CharField(source='get_tipo_documento_display', read_only=True)
    genero_display = serializers.CharField(source='get_genero_display', read_only=True)
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = Paciente
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion', 'creado_por']


class PacienteCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear pacientes."""
    
    class Meta:
        model = Paciente
        exclude = ['fecha_creacion', 'fecha_actualizacion', 'creado_por']
    
    def validate_numero_documento(self, value):
        """Validar que el número de documento sea único."""
        if Paciente.objects.filter(numero_documento=value).exists():
            raise serializers.ValidationError("Ya existe un paciente con este número de documento.")
        return value
    
    def validate_numero_historia_clinica(self, value):
        """Validar que el número de historia clínica sea único."""
        if Paciente.objects.filter(numero_historia_clinica=value).exists():
            raise serializers.ValidationError("Ya existe un paciente con este número de historia clínica.")
        return value
    
    def validate(self, data):
        """Validaciones generales."""
        # Validar edad
        if data.get('fecha_nacimiento'):
            from django.utils import timezone
            if data['fecha_nacimiento'] > timezone.now().date():
                raise serializers.ValidationError({
                    'fecha_nacimiento': 'La fecha de nacimiento no puede ser futura.'
                })
        
        # Validar fecha de alta
        if data.get('fecha_alta'):
            if not data.get('fecha_ingreso'):
                raise serializers.ValidationError({
                    'fecha_alta': 'No se puede especificar fecha de alta sin fecha de ingreso.'
                })
            if data['fecha_alta'] < data['fecha_ingreso']:
                raise serializers.ValidationError({
                    'fecha_alta': 'La fecha de alta debe ser posterior a la fecha de ingreso.'
                })
        
        return data


class ProcedimientoListSerializer(serializers.ModelSerializer):
    """Serializer para listado de procedimientos."""
    
    paciente_nombre = serializers.CharField(source='paciente.nombre_completo', read_only=True)
    profesional_nombre = serializers.CharField(source='profesional.get_full_name', read_only=True)
    consultorio_nombre = serializers.CharField(source='consultorio.nombre', read_only=True, allow_null=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    duracion_formateada = serializers.CharField(read_only=True)
    costo_formateado = serializers.CharField(read_only=True)
    
    class Meta:
        model = Procedimiento
        fields = [
            'id', 'codigo', 'tipo', 'tipo_display', 'fecha', 'hora_inicio', 'hora_fin',
            'duracion_minutos', 'duracion_formateada', 'estado', 'estado_display',
            'paciente', 'paciente_nombre', 'profesional', 'profesional_nombre',
            'consultorio', 'consultorio_nombre', 'costo', 'costo_formateado', 'pagado',
            'motivo_consulta', 'fecha_creacion'
        ]


class ProcedimientoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado de procedimiento."""
    
    paciente_info = PacienteListSerializer(source='paciente', read_only=True)
    profesional_info = UsuarioListSerializer(source='profesional', read_only=True)
    consultorio_info = ConsultorioListSerializer(source='consultorio', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    duracion_formateada = serializers.CharField(read_only=True)
    esta_completado = serializers.BooleanField(read_only=True)
    costo_formateado = serializers.CharField(read_only=True)
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = Procedimiento
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion', 'creado_por', 'duracion_minutos']


class ProcedimientoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear procedimientos."""
    
    class Meta:
        model = Procedimiento
        exclude = ['fecha_creacion', 'fecha_actualizacion', 'creado_por', 'duracion_minutos']
    
    def validate_codigo(self, value):
        """Validar que el código sea único."""
        if Procedimiento.objects.filter(codigo=value).exists():
            raise serializers.ValidationError("Ya existe un procedimiento con este código.")
        return value
    
    def validate(self, data):
        """Validaciones generales."""
        # Validar horas
        if data.get('hora_fin') and data.get('hora_inicio'):
            if data['hora_fin'] <= data['hora_inicio']:
                raise serializers.ValidationError({
                    'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio.'
                })
        
        # Validar profesional
        if data.get('profesional'):
            roles_validos = ['TERAPEUTA', 'MEDICO', 'PSICOLOGO', 'ADMIN']
            if data['profesional'].rol not in roles_validos:
                raise serializers.ValidationError({
                    'profesional': 'El profesional debe ser terapeuta, médico o psicólogo.'
                })
        
        return data


class SesionTerapeuticaListSerializer(serializers.ModelSerializer):
    """Serializer para listado de sesiones."""
    
    paciente_nombre = serializers.CharField(source='paciente.nombre_completo', read_only=True)
    terapeuta_nombre = serializers.CharField(source='terapeuta.get_full_name', read_only=True)
    terapia_nombre = serializers.CharField(source='terapia.nombre', read_only=True)
    consultorio_nombre = serializers.CharField(source='consultorio.nombre', read_only=True, allow_null=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    tipo_asistencia_display = serializers.CharField(source='get_tipo_asistencia_display', read_only=True)
    duracion_programada_formateada = serializers.CharField(read_only=True)
    duracion_real_formateada = serializers.CharField(read_only=True)
    costo_formateado = serializers.CharField(read_only=True)
    asistio = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = SesionTerapeutica
        fields = [
            'id', 'numero_sesion', 'fecha', 'hora_inicio', 'hora_fin',
            'duracion_programada_minutos', 'duracion_programada_formateada',
            'duracion_real_minutos', 'duracion_real_formateada',
            'estado', 'estado_display', 'tipo_asistencia', 'tipo_asistencia_display',
            'asistio', 'paciente', 'paciente_nombre', 'terapeuta', 'terapeuta_nombre',
            'terapia', 'terapia_nombre', 'consultorio', 'consultorio_nombre',
            'costo', 'costo_formateado', 'pagado', 'desempeno_paciente',
            'fecha_creacion'
        ]


class SesionTerapeuticaDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado de sesión."""
    
    paciente_info = PacienteListSerializer(source='paciente', read_only=True)
    terapeuta_info = UsuarioListSerializer(source='terapeuta', read_only=True)
    terapia_info = TerapiaListSerializer(source='terapia', read_only=True)
    consultorio_info = ConsultorioListSerializer(source='consultorio', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    tipo_asistencia_display = serializers.CharField(source='get_tipo_asistencia_display', read_only=True)
    duracion_programada_formateada = serializers.CharField(read_only=True)
    duracion_real_formateada = serializers.CharField(read_only=True)
    esta_completada = serializers.BooleanField(read_only=True)
    asistio = serializers.BooleanField(read_only=True)
    costo_formateado = serializers.CharField(read_only=True)
    promedio_desempeno = serializers.FloatField(read_only=True)
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = SesionTerapeutica
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion', 'creado_por', 
                           'duracion_real_minutos', 'procedimiento']


class SesionTerapeuticaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear sesiones."""
    
    class Meta:
        model = SesionTerapeutica
        exclude = ['fecha_creacion', 'fecha_actualizacion', 'creado_por', 
                   'duracion_real_minutos', 'procedimiento']
    
    def validate_numero_sesion(self, value):
        """Validar que el número de sesión sea único."""
        if SesionTerapeutica.objects.filter(numero_sesion=value).exists():
            raise serializers.ValidationError("Ya existe una sesión con este número.")
        return value
    
    def validate(self, data):
        """Validaciones generales."""
        # Validar horas
        if data.get('hora_fin') and data.get('hora_inicio'):
            if data['hora_fin'] <= data['hora_inicio']:
                raise serializers.ValidationError({
                    'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio.'
                })
        
        # Validar terapeuta
        if data.get('terapeuta'):
            roles_validos = ['TERAPEUTA', 'MEDICO', 'PSICOLOGO', 'ADMIN']
            if data['terapeuta'].rol not in roles_validos:
                raise serializers.ValidationError({
                    'terapeuta': 'Debe ser un terapeuta, médico o psicólogo.'
                })
        
        # Validar calificaciones
        for campo in ['desempeno_paciente', 'nivel_atencion', 'nivel_participacion']:
            if data.get(campo) and (data[campo] < 1 or data[campo] > 10):
                raise serializers.ValidationError({
                    campo: 'La calificación debe estar entre 1 y 10.'
                })
        
        return data


class ObjetivoTerapeuticoSerializer(serializers.ModelSerializer):
    """Serializer para objetivos terapéuticos."""
    
    paciente_nombre = serializers.CharField(source='paciente.nombre_completo', read_only=True)
    terapia_nombre = serializers.CharField(source='terapia.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    esta_logrado = serializers.BooleanField(read_only=True)
    dias_transcurridos = serializers.IntegerField(read_only=True)
    dias_restantes = serializers.IntegerField(read_only=True)
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = ObjetivoTerapeutico
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion', 'creado_por']
    
    def validate(self, data):
        """Validaciones."""
        if data.get('fecha_limite') and data.get('fecha_inicio'):
            if data['fecha_limite'] < data['fecha_inicio']:
                raise serializers.ValidationError({
                    'fecha_limite': 'La fecha límite debe ser posterior a la fecha de inicio.'
                })
        
        if data.get('porcentaje_avance'):
            if data['porcentaje_avance'] < 0 or data['porcentaje_avance'] > 100:
                raise serializers.ValidationError({
                    'porcentaje_avance': 'El porcentaje debe estar entre 0 y 100.'
                })
        
        return data


class EvolucionPacienteSerializer(serializers.ModelSerializer):
    """Serializer para evolución de pacientes."""
    
    paciente_nombre = serializers.CharField(source='paciente.nombre_completo', read_only=True)
    profesional_nombre = serializers.CharField(source='profesional.get_full_name', read_only=True)
    sesion_numero = serializers.CharField(source='sesion.numero_sesion', read_only=True, allow_null=True)
    
    class Meta:
        model = EvolucionPaciente
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']


class EstadisticasProcedimientosSerializer(serializers.Serializer):
    """Serializer para estadísticas de procedimientos."""
    
    total_procedimientos = serializers.IntegerField()
    procedimientos_completados = serializers.IntegerField()
    procedimientos_cancelados = serializers.IntegerField()
    procedimientos_programados = serializers.IntegerField()
    total_pacientes = serializers.IntegerField()
    pacientes_activos = serializers.IntegerField()
    total_sesiones = serializers.IntegerField()
    sesiones_completadas = serializers.IntegerField()
    tasa_asistencia = serializers.FloatField()
    promedio_desempeno = serializers.FloatField()
    ingresos_totales = serializers.DecimalField(max_digits=12, decimal_places=2)
    ingresos_pendientes = serializers.DecimalField(max_digits=12, decimal_places=2)


class AgendaSemanalSerializer(serializers.Serializer):
    """Serializer para agenda semanal."""
    
    fecha = serializers.DateField()
    sesiones = SesionTerapeuticaListSerializer(many=True)
    procedimientos = ProcedimientoListSerializer(many=True)
