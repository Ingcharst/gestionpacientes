"""
Serializadores para la API de terapias.
"""
from rest_framework import serializers
from apps.terapias.models import CategoriaTerapia, Terapia


class CategoriaTerapiaSerializer(serializers.ModelSerializer):
    """Serializador para categorías de terapias."""
    
    numero_terapias = serializers.IntegerField(read_only=True)
    tiene_terapias = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CategoriaTerapia
        fields = [
            'id', 'nombre', 'codigo', 'descripcion',
            'color', 'icono', 'orden', 'activo',
            'numero_terapias', 'tiene_terapias',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = [
            'id', 'fecha_creacion', 'fecha_actualizacion',
            'numero_terapias', 'tiene_terapias'
        ]
    
    def validate_codigo(self, value):
        """Valida que el código sea único."""
        instance = self.instance
        if CategoriaTerapia.objects.filter(codigo=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Este código ya está en uso.")
        return value


class TerapiaListSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listados de terapias."""
    
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    modalidad_display = serializers.CharField(source='get_modalidad_display', read_only=True)
    especialidad_display = serializers.CharField(source='get_especialidad_display', read_only=True)
    duracion_formateada = serializers.CharField(read_only=True)
    costo_formateado = serializers.CharField(read_only=True)
    rango_edad = serializers.CharField(read_only=True)
    
    class Meta:
        model = Terapia
        fields = [
            'id', 'codigo', 'nombre', 'descripcion_corta',
            'categoria', 'categoria_nombre',
            'modalidad', 'modalidad_display',
            'especialidad', 'especialidad_display',
            'duracion_minutos', 'duracion_formateada',
            'costo_sesion', 'costo_formateado',
            'rango_edad', 'activo', 'destacado'
        ]
        read_only_fields = ['id']


class TerapiaDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado para terapias."""
    
    categoria_detail = CategoriaTerapiaSerializer(source='categoria', read_only=True)
    modalidad_display = serializers.CharField(source='get_modalidad_display', read_only=True)
    especialidad_display = serializers.CharField(source='get_especialidad_display', read_only=True)
    nivel_intensidad_display = serializers.CharField(source='get_nivel_intensidad_display', read_only=True)
    
    # Propiedades calculadas
    nombre_completo = serializers.CharField(read_only=True)
    duracion_formateada = serializers.CharField(read_only=True)
    costo_formateado = serializers.CharField(read_only=True)
    rango_edad = serializers.CharField(read_only=True)
    es_grupal = serializers.BooleanField(read_only=True)
    requiere_consultorios_especiales = serializers.BooleanField(read_only=True)
    tiene_equipamiento_especial = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Terapia
        fields = [
            'id', 'codigo', 'nombre', 'categoria', 'categoria_detail',
            'descripcion', 'descripcion_corta',
            'modalidad', 'modalidad_display',
            'especialidad', 'especialidad_display',
            'nivel_intensidad', 'nivel_intensidad_display',
            'duracion_minutos', 'duracion_minima_minutos', 'duracion_maxima_minutos',
            'duracion_formateada', 'frecuencia_semanal_recomendada',
            'costo_sesion', 'costo_minimo', 'costo_paquete_mensual',
            'costo_formateado', 'permite_descuento',
            'edad_minima', 'edad_maxima', 'rango_edad',
            'requiere_evaluacion_previa', 'requiere_orden_medica',
            'capacidad_minima', 'capacidad_maxima', 'requiere_acompanante',
            'tipos_consultorio_requeridos', 'equipamiento_requerido',
            'objetivos', 'metodologia', 'beneficios', 'contraindicaciones', 'notas',
            'disponible_online', 'disponible_domicilio',
            'imagen', 'folleto_url', 'video_url',
            'activo', 'destacado', 'orden',
            'nombre_completo', 'es_grupal',
            'requiere_consultorios_especiales', 'tiene_equipamiento_especial',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = [
            'id', 'fecha_creacion', 'fecha_actualizacion',
            'nombre_completo', 'duracion_formateada', 'costo_formateado',
            'rango_edad', 'es_grupal', 'requiere_consultorios_especiales',
            'tiene_equipamiento_especial'
        ]


class TerapiaCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear terapias."""
    
    class Meta:
        model = Terapia
        fields = [
            'nombre', 'codigo', 'categoria',
            'descripcion', 'descripcion_corta',
            'modalidad', 'especialidad', 'nivel_intensidad',
            'duracion_minutos', 'duracion_minima_minutos', 'duracion_maxima_minutos',
            'frecuencia_semanal_recomendada',
            'costo_sesion', 'costo_minimo', 'costo_paquete_mensual',
            'permite_descuento',
            'edad_minima', 'edad_maxima',
            'requiere_evaluacion_previa', 'requiere_orden_medica',
            'capacidad_minima', 'capacidad_maxima', 'requiere_acompanante',
            'tipos_consultorio_requeridos', 'equipamiento_requerido',
            'objetivos', 'metodologia', 'beneficios', 'contraindicaciones', 'notas',
            'disponible_online', 'disponible_domicilio',
            'imagen', 'folleto_url', 'video_url',
            'activo', 'destacado', 'orden'
        ]
    
    def validate_codigo(self, value):
        """Valida que el código sea único."""
        if Terapia.objects.filter(codigo=value).exists():
            raise serializers.ValidationError("Este código ya está en uso.")
        return value
    
    def validate(self, data):
        """Validaciones personalizadas."""
        # Validar duraciones
        duracion = data.get('duracion_minutos')
        duracion_min = data.get('duracion_minima_minutos')
        duracion_max = data.get('duracion_maxima_minutos')
        
        if duracion_min and duracion_max and duracion_min > duracion_max:
            raise serializers.ValidationError({
                'duracion_maxima_minutos': 'La duración máxima debe ser mayor a la mínima.'
            })
        
        if duracion_min and duracion < duracion_min:
            raise serializers.ValidationError({
                'duracion_minutos': 'La duración debe ser mayor o igual a la duración mínima.'
            })
        
        if duracion_max and duracion > duracion_max:
            raise serializers.ValidationError({
                'duracion_minutos': 'La duración debe ser menor o igual a la duración máxima.'
            })
        
        # Validar edades
        edad_min = data.get('edad_minima')
        edad_max = data.get('edad_maxima')
        
        if edad_min and edad_max and edad_min > edad_max:
            raise serializers.ValidationError({
                'edad_maxima': 'La edad máxima debe ser mayor a la edad mínima.'
            })
        
        # Validar costos
        costo = data.get('costo_sesion')
        costo_min = data.get('costo_minimo')
        
        if costo_min and costo_min > costo:
            raise serializers.ValidationError({
                'costo_minimo': 'El costo mínimo no puede ser mayor al costo de sesión.'
            })
        
        # Validar capacidad
        cap_min = data.get('capacidad_minima')
        cap_max = data.get('capacidad_maxima')
        
        if cap_min > cap_max:
            raise serializers.ValidationError({
                'capacidad_maxima': 'La capacidad máxima debe ser mayor a la capacidad mínima.'
            })
        
        return data


class TerapiaBusquedaSerializer(serializers.Serializer):
    """Serializador para búsqueda avanzada de terapias."""
    
    categoria = serializers.IntegerField(required=False)
    modalidad = serializers.ChoiceField(
        choices=Terapia.Modalidad.choices,
        required=False
    )
    especialidad = serializers.ChoiceField(
        choices=Terapia.Especialidad.choices,
        required=False
    )
    edad = serializers.IntegerField(required=False, min_value=0, max_value=100)
    costo_maximo = serializers.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        min_value=0
    )
    duracion_minima = serializers.IntegerField(required=False, min_value=15)
    duracion_maxima = serializers.IntegerField(required=False, max_value=480)
    online = serializers.BooleanField(required=False)
    domicilio = serializers.BooleanField(required=False)
    solo_destacadas = serializers.BooleanField(required=False)
    search = serializers.CharField(required=False, max_length=200)


class EstadisticasTerapiasSerializer(serializers.Serializer):
    """Serializador para estadísticas de terapias."""
    
    total_terapias = serializers.IntegerField()
    terapias_activas = serializers.IntegerField()
    terapias_destacadas = serializers.IntegerField()
    por_categoria = serializers.DictField()
    por_especialidad = serializers.DictField()
    por_modalidad = serializers.DictField()
    costo_promedio = serializers.DecimalField(max_digits=10, decimal_places=2)
    duracion_promedio = serializers.IntegerField()
