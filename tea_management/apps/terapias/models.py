"""
Modelos para gestión de catálogo de terapias del centro TEA.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


class CategoriaTerapia(models.Model):
    """
    Modelo para categorías de terapias.
    Permite agrupar terapias por su naturaleza o área de intervención.
    """
    
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre de la Categoría',
        help_text='Ejemplo: Terapia del Lenguaje, Terapia Ocupacional'
    )
    
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código',
        help_text='Código único de identificación'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción de la categoría y qué incluye'
    )
    
    color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name='Color',
        help_text='Color en formato hexadecimal (#RRGGBB)'
    )
    
    icono = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Icono',
        help_text='Clase de icono (Font Awesome, Bootstrap Icons, etc.)'
    )
    
    orden = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden',
        help_text='Orden de visualización (menor primero)'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    class Meta:
        verbose_name = 'Categoría de Terapia'
        verbose_name_plural = 'Categorías de Terapias'
        ordering = ['orden', 'nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo', 'orden']),
        ]
    
    def __str__(self):
        return self.nombre
    
    @property
    def numero_terapias(self):
        """Retorna el número de terapias activas en esta categoría."""
        return self.terapias.filter(activo=True).count()
    
    @property
    def tiene_terapias(self):
        """Verifica si la categoría tiene terapias."""
        return self.terapias.exists()


class Terapia(models.Model):
    """
    Modelo para terapias del catálogo maestro.
    Define los tipos de terapias que se ofrecen en el centro.
    """
    
    class Modalidad(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', _('Individual')
        GRUPAL = 'GRUPAL', _('Grupal')
        FAMILIAR = 'FAMILIAR', _('Familiar')
        PAREJA = 'PAREJA', _('En Pareja')
        MIXTA = 'MIXTA', _('Mixta')
    
    class Especialidad(models.TextChoices):
        LENGUAJE = 'LENGUAJE', _('Lenguaje y Comunicación')
        OCUPACIONAL = 'OCUPACIONAL', _('Terapia Ocupacional')
        FISICA = 'FISICA', _('Terapia Física')
        PSICOLOGIA = 'PSICOLOGIA', _('Psicología')
        CONDUCTUAL = 'CONDUCTUAL', _('Terapia Conductual (ABA)')
        INTEGRACION_SENSORIAL = 'INTEGRACION_SENSORIAL', _('Integración Sensorial')
        MUSICOTERAPIA = 'MUSICOTERAPIA', _('Musicoterapia')
        ARTETERAPIA = 'ARTETERAPIA', _('Arteterapia')
        NEUROLOGICA = 'NEUROLOGICA', _('Terapia Neurológica')
        SOCIAL = 'SOCIAL', _('Habilidades Sociales')
        COGNITIVA = 'COGNITIVA', _('Estimulación Cognitiva')
        ALIMENTACION = 'ALIMENTACION', _('Terapia de Alimentación')
    
    class NivelIntensidad(models.TextChoices):
        BAJA = 'BAJA', _('Intensidad Baja')
        MEDIA = 'MEDIA', _('Intensidad Media')
        ALTA = 'ALTA', _('Intensidad Alta')
        MUY_ALTA = 'MUY_ALTA', _('Intensidad Muy Alta')
    
    # Información Básica
    nombre = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Nombre de la Terapia',
        help_text='Nombre descriptivo de la terapia'
    )
    
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código',
        help_text='Código único de identificación'
    )
    
    categoria = models.ForeignKey(
        CategoriaTerapia,
        on_delete=models.PROTECT,
        related_name='terapias',
        verbose_name='Categoría'
    )
    
    descripcion = models.TextField(
        verbose_name='Descripción',
        help_text='Descripción detallada de la terapia'
    )
    
    descripcion_corta = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Descripción Corta',
        help_text='Resumen breve para listados'
    )
    
    # Clasificación
    modalidad = models.CharField(
        max_length=20,
        choices=Modalidad.choices,
        default=Modalidad.INDIVIDUAL,
        verbose_name='Modalidad'
    )
    
    especialidad = models.CharField(
        max_length=30,
        choices=Especialidad.choices,
        verbose_name='Especialidad'
    )
    
    nivel_intensidad = models.CharField(
        max_length=10,
        choices=NivelIntensidad.choices,
        default=NivelIntensidad.MEDIA,
        verbose_name='Nivel de Intensidad'
    )
    
    # Duración y Frecuencia
    duracion_minutos = models.PositiveIntegerField(
        validators=[MinValueValidator(15), MaxValueValidator(480)],
        verbose_name='Duración (minutos)',
        help_text='Duración estándar de la sesión en minutos'
    )
    
    duracion_minima_minutos = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=15,
        validators=[MinValueValidator(15)],
        verbose_name='Duración Mínima (minutos)',
        help_text='Duración mínima permitida'
    )
    
    duracion_maxima_minutos = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=30,
        validators=[MaxValueValidator(480)],
        verbose_name='Duración Máxima (minutos)',
        help_text='Duración máxima permitida'
    )
    
    frecuencia_semanal_recomendada = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        verbose_name='Frecuencia Semanal Recomendada',
        help_text='Número de sesiones recomendadas por semana'
    )
    
    # Costos
    costo_sesion = models.DecimalField(
        default=Decimal('0.00'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Costo por Sesión',
        help_text='Costo estándar por sesión individual'
    )
    
    costo_minimo = models.DecimalField(
        default=Decimal('0.00'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Costo Mínimo',
        help_text='Costo mínimo (si aplica descuento)'
    )
    
    costo_paquete_mensual = models.DecimalField(
        default=Decimal('0.00'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Costo Paquete Mensual',
        help_text='Costo de paquete mensual (si aplica)'
    )
    
    permite_descuento = models.BooleanField(
        default=True,
        verbose_name='Permite Descuento'
    )
    
    # Requisitos
    edad_minima = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Edad Mínima',
        help_text='Edad mínima recomendada en años'
    )
    
    edad_maxima = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Edad Máxima',
        help_text='Edad máxima recomendada en años'
    )
    
    requiere_evaluacion_previa = models.BooleanField(
        default=True,
        verbose_name='Requiere Evaluación Previa',
        help_text='Indica si requiere evaluación antes de iniciar'
    )
    
    requiere_orden_medica = models.BooleanField(
        default=False,
        verbose_name='Requiere Orden Médica'
    )
    
    # Configuración
    capacidad_minima = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name='Capacidad Mínima',
        help_text='Número mínimo de pacientes (para grupales)'
    )
    
    capacidad_maxima = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name='Capacidad Máxima',
        help_text='Número máximo de pacientes'
    )
    
    requiere_acompanante = models.BooleanField(
        default=False,
        verbose_name='Requiere Acompañante',
        help_text='Indica si el paciente debe estar acompañado'
    )
    
    # Relación con Consultorios
    tipos_consultorio_requeridos = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Tipos de Consultorio Requeridos',
        help_text='Lista de tipos de consultorio compatibles'
    )
    
    equipamiento_requerido = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Equipamiento Requerido',
        help_text='Lista de equipamiento necesario'
    )
    
    # Información Adicional
    objetivos = models.TextField(
        blank=True,
        verbose_name='Objetivos',
        help_text='Objetivos terapéuticos'
    )
    
    metodologia = models.TextField(
        blank=True,
        verbose_name='Metodología',
        help_text='Metodología y técnicas utilizadas'
    )
    
    beneficios = models.TextField(
        blank=True,
        verbose_name='Beneficios',
        help_text='Beneficios esperados de la terapia'
    )
    
    contraindicaciones = models.TextField(
        blank=True,
        verbose_name='Contraindicaciones',
        help_text='Casos en los que no se recomienda'
    )
    
    notas = models.TextField(
        blank=True,
        verbose_name='Notas Adicionales'
    )
    
    # Disponibilidad
    disponible_online = models.BooleanField(
        default=False,
        verbose_name='Disponible Online',
        help_text='Puede realizarse de forma virtual'
    )
    
    disponible_domicilio = models.BooleanField(
        default=False,
        verbose_name='Disponible a Domicilio',
        help_text='Puede realizarse en casa del paciente'
    )
    
    # Imagen y Documentación
    imagen = models.ImageField(
        upload_to='terapias/imagenes/',
        blank=True,
        null=True,
        verbose_name='Imagen de la Terapia'
    )
    
    folleto_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='URL del Folleto',
        help_text='Enlace a folleto informativo'
    )
    
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='URL del Video',
        help_text='Enlace a video explicativo'
    )
    
    # Estado
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    destacado = models.BooleanField(
        default=False,
        verbose_name='Destacado',
        help_text='Mostrar en página principal'
    )
    
    orden = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden',
        help_text='Orden de visualización'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    class Meta:
        verbose_name = 'Terapia'
        verbose_name_plural = 'Terapias'
        ordering = ['categoria', 'orden', 'nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['categoria', 'activo']),
            models.Index(fields=['especialidad']),
            models.Index(fields=['modalidad']),
            models.Index(fields=['activo', 'destacado']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def clean(self):
        """Validaciones personalizadas."""
        from django.core.exceptions import ValidationError
        
        # Validar duraciones
        if self.duracion_minima_minutos and self.duracion_maxima_minutos:
            if self.duracion_minima_minutos > self.duracion_maxima_minutos:
                raise ValidationError({
                    'duracion_maxima_minutos': 'La duración máxima debe ser mayor a la mínima.'
                })
        
        # Validar que duración estándar esté en rango
        if self.duracion_minima_minutos and self.duracion_minutos < self.duracion_minima_minutos:
            raise ValidationError({
                'duracion_minutos': 'La duración debe ser mayor o igual a la duración mínima.'
            })
        
        if self.duracion_maxima_minutos and self.duracion_minutos > self.duracion_maxima_minutos:
            raise ValidationError({
                'duracion_minutos': 'La duración debe ser menor o igual a la duración máxima.'
            })
        
        # Validar edades
        if self.edad_minima and self.edad_maxima:
            if self.edad_minima > self.edad_maxima:
                raise ValidationError({
                    'edad_maxima': 'La edad máxima debe ser mayor a la edad mínima.'
                })
        
        # Validar costos
        if self.costo_minimo and self.costo_minimo > self.costo_sesion:
            raise ValidationError({
                'costo_minimo': 'El costo mínimo no puede ser mayor al costo de sesión.'
            })
        
        # Validar capacidad
        if self.capacidad_minima > self.capacidad_maxima:
            raise ValidationError({
                'capacidad_maxima': 'La capacidad máxima debe ser mayor a la capacidad mínima.'
            })
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo con categoría."""
        return f"{self.categoria.nombre} - {self.nombre}"
    
    @property
    def duracion_formateada(self):
        """Retorna la duración en formato legible."""
        # Validar que duracion_minutos no sea None
        if not self.duracion_minutos:
            return "No definida"
        
        horas = self.duracion_minutos // 60
        minutos = self.duracion_minutos % 60
        
        if horas > 0 and minutos > 0:
            return f"{horas}h {minutos}min"
        elif horas > 0:
            return f"{horas}h"
        else:
            return f"{minutos}min"
    
    @property
    def costo_formateado(self):
        """Retorna el costo formateado."""
        if not self.costo_sesion:
            return "No definido"
        return f"${self.costo_sesion:,.2f}"
    
    @property
    def rango_edad(self):
        """Retorna el rango de edad recomendado."""
        if self.edad_minima and self.edad_maxima:
            return f"{self.edad_minima}-{self.edad_maxima} años"
        elif self.edad_minima:
            return f"Desde {self.edad_minima} años"
        elif self.edad_maxima:
            return f"Hasta {self.edad_maxima} años"
        return "Todas las edades"
    
    @property
    def es_grupal(self):
        """Verifica si es terapia grupal."""
        return self.modalidad == self.Modalidad.GRUPAL
    
    @property
    def requiere_consultorios_especiales(self):
        """Verifica si requiere consultorios especiales."""
        return len(self.tipos_consultorio_requeridos) > 0
    
    @property
    def tiene_equipamiento_especial(self):
        """Verifica si requiere equipamiento especial."""
        return len(self.equipamiento_requerido) > 0
    
    def calcular_costo_mensual(self, sesiones_por_mes=None):
        """Calcula el costo mensual estimado."""
        if not self.costo_sesion:
            return Decimal('0.00')
        
        if sesiones_por_mes is None:
            if not self.frecuencia_semanal_recomendada:
                return self.costo_sesion
            sesiones_por_mes = self.frecuencia_semanal_recomendada * 4
        
        if self.costo_paquete_mensual:
            return self.costo_paquete_mensual
        
        return self.costo_sesion * sesiones_por_mes
    
    def es_apto_para_edad(self, edad):
        """Verifica si la terapia es apta para una edad específica."""
        if self.edad_minima and edad < self.edad_minima:
            return False
        if self.edad_maxima and edad > self.edad_maxima:
            return False
        return True
