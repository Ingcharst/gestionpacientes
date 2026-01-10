"""
Modelos para gestión de consultorios y espacios físicos del centro.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from apps.usuarios.models import Usuario


class Consultorio(models.Model):
    """
    Modelo para consultorios del centro de atención.
    Representa espacios físicos donde se realizan las terapias.
    """
    
    class TipoConsultorio(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', _('Consultorio Individual')
        GRUPAL = 'GRUPAL', _('Consultorio Grupal')
        TERAPIA_FISICA = 'TERAPIA_FISICA', _('Sala de Terapia Física')
        TERAPIA_OCUPACIONAL = 'TERAPIA_OCUPACIONAL', _('Sala de Terapia Ocupacional')
        LENGUAJE = 'LENGUAJE', _('Sala de Lenguaje')
        INTEGRACION_SENSORIAL = 'INTEGRACION_SENSORIAL', _('Sala de Integración Sensorial')
        LUDOTECA = 'LUDOTECA', _('Ludoteca/Sala de Juegos')
        EVALUACION = 'EVALUACION', _('Sala de Evaluación')
        MUSICOTERAPIA = 'MUSICOTERAPIA', _('Sala de Musicoterapia')
    
    class EstadoConsultorio(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', _('Disponible')
        OCUPADO = 'OCUPADO', _('Ocupado')
        MANTENIMIENTO = 'MANTENIMIENTO', _('En Mantenimiento')
        INACTIVO = 'INACTIVO', _('Inactivo')
    
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre del Consultorio',
        help_text='Ejemplo: Consultorio 101, Sala Azul'
    )
    
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código',
        help_text='Código único de identificación'
    )
    
    tipo = models.CharField(
        max_length=30,
        choices=TipoConsultorio.choices,
        default=TipoConsultorio.INDIVIDUAL,
        verbose_name='Tipo de Consultorio'
    )
    
    piso = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name='Piso',
        help_text='Planta/Piso donde se encuentra'
    )
    
    numero = models.CharField(
        max_length=20,
        verbose_name='Número',
        help_text='Número de consultorio o sala'
    )
    
    capacidad = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        verbose_name='Capacidad',
        help_text='Número máximo de personas'
    )
    
    area_metros = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name='Área (m²)',
        help_text='Área en metros cuadrados'
    )
    
    estado = models.CharField(
        max_length=20,
        choices=EstadoConsultorio.choices,
        default=EstadoConsultorio.DISPONIBLE,
        verbose_name='Estado'
    )
    
    equipamiento = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Equipamiento',
        help_text='Lista de equipamiento disponible en el consultorio'
    )
    
    caracteristicas = models.TextField(
        blank=True,
        verbose_name='Características',
        help_text='Descripción de características especiales'
    )
    
    foto = models.ImageField(
        upload_to='consultorios/fotos/',
        blank=True,
        null=True,
        verbose_name='Foto del Consultorio'
    )
    
    tiene_ventana = models.BooleanField(
        default=True,
        verbose_name='Tiene Ventana'
    )
    
    tiene_aire_acondicionado = models.BooleanField(
        default=False,
        verbose_name='Tiene Aire Acondicionado'
    )
    
    accesible_silla_ruedas = models.BooleanField(
        default=True,
        verbose_name='Accesible para Silla de Ruedas'
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        verbose_name = 'Consultorio'
        verbose_name_plural = 'Consultorios'
        ordering = ['piso', 'numero']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['tipo', 'estado']),
            models.Index(fields=['piso', 'numero']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del consultorio."""
        return f"Piso {self.piso} - {self.nombre} ({self.numero})"
    
    @property
    def esta_disponible(self):
        """Verifica si el consultorio está disponible."""
        return self.estado == self.EstadoConsultorio.DISPONIBLE and self.activo
    
    @property
    def tiene_equipamiento(self):
        """Verifica si tiene equipamiento registrado."""
        return len(self.equipamiento) > 0
    
    def agregar_equipo(self, nombre_equipo, cantidad=1):
        """Agrega equipamiento al consultorio."""
        equipo = {
            'nombre': nombre_equipo,
            'cantidad': cantidad
        }
        self.equipamiento.append(equipo)
        self.save()


class Sala(models.Model):
    """
    Modelo para salas o espacios específicos dentro de consultorios.
    Permite subdividir consultorios grandes en áreas especializadas.
    """
    
    class TipoSala(models.TextChoices):
        EVALUACION = 'EVALUACION', _('Área de Evaluación')
        TERAPIA = 'TERAPIA', _('Área de Terapia')
        JUEGO = 'JUEGO', _('Área de Juego')
        ESPERA = 'ESPERA', _('Área de Espera')
        OBSERVACION = 'OBSERVACION', _('Área de Observación')
        MATERIAL = 'MATERIAL', _('Área de Material')
    
    consultorio = models.ForeignKey(
        Consultorio,
        on_delete=models.CASCADE,
        related_name='salas',
        verbose_name='Consultorio'
    )
    
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre de la Sala'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TipoSala.choices,
        verbose_name='Tipo de Sala'
    )
    
    area_metros = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name='Área (m²)'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    equipamiento_especifico = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Equipamiento Específico'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    class Meta:
        verbose_name = 'Sala'
        verbose_name_plural = 'Salas'
        ordering = ['consultorio', 'nombre']
        unique_together = ['consultorio', 'nombre']
    
    def __str__(self):
        return f"{self.consultorio.codigo} - {self.nombre}"


class AsignacionConsultorio(models.Model):
    """
    Modelo para asignar terapeutas a consultorios.
    Gestiona qué terapeuta utiliza qué consultorio y en qué horarios.
    """
    
    class TipoAsignacion(models.TextChoices):
        PERMANENTE = 'PERMANENTE', _('Asignación Permanente')
        TEMPORAL = 'TEMPORAL', _('Asignación Temporal')
        COMPARTIDA = 'COMPARTIDA', _('Asignación Compartida')
    
    consultorio = models.ForeignKey(
        Consultorio,
        on_delete=models.CASCADE,
        related_name='asignaciones',
        verbose_name='Consultorio'
    )
    
    terapeuta = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='consultorios_asignados',
        limit_choices_to={'rol__in': ['TERAPEUTA', 'PSICOLOGO', 'MEDICO']},
        verbose_name='Terapeuta'
    )
    
    tipo_asignacion = models.CharField(
        max_length=15,
        choices=TipoAsignacion.choices,
        default=TipoAsignacion.TEMPORAL,
        verbose_name='Tipo de Asignación'
    )
    
    fecha_inicio = models.DateField(
        verbose_name='Fecha de Inicio'
    )
    
    fecha_fin = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Fin',
        help_text='Dejar en blanco para asignaciones permanentes'
    )
    
    horario = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Horario',
        help_text='Horario de uso del consultorio por día'
    )
    
    dias_semana = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Días de la Semana',
        help_text='Lista de días asignados: ["Lunes", "Martes", ...]'
    )
    
    prioridad = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Prioridad',
        help_text='1=Baja, 5=Alta'
    )
    
    notas = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Asignación Activa'
    )
    
    fecha_asignacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Asignación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    class Meta:
        verbose_name = 'Asignación de Consultorio'
        verbose_name_plural = 'Asignaciones de Consultorios'
        ordering = ['-fecha_inicio', '-prioridad']
        indexes = [
            models.Index(fields=['consultorio', 'terapeuta']),
            models.Index(fields=['fecha_inicio', 'fecha_fin']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return f"{self.terapeuta.get_full_name()} - {self.consultorio.nombre}"
    
    def clean(self):
        """Validaciones personalizadas."""
        from django.core.exceptions import ValidationError
        
        # Validar que el usuario sea terapeuta
        if not self.terapeuta.es_terapeuta:
            raise ValidationError({
                'terapeuta': 'Solo se pueden asignar terapeutas a consultorios.'
            })
        
        # Validar fechas
        if self.fecha_fin and self.fecha_inicio > self.fecha_fin:
            raise ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })
    
    @property
    def esta_vigente(self):
        """Verifica si la asignación está vigente."""
        from django.utils import timezone
        hoy = timezone.now().date()
        
        if not self.activo:
            return False
        
        if self.fecha_fin:
            return self.fecha_inicio <= hoy <= self.fecha_fin
        
        return self.fecha_inicio <= hoy
    
    @property
    def es_permanente(self):
        """Verifica si es asignación permanente."""
        return self.tipo_asignacion == self.TipoAsignacion.PERMANENTE
    
    def agregar_dia(self, dia, hora_inicio, hora_fin):
        """Agrega un día al horario de la asignación."""
        if dia not in self.dias_semana:
            self.dias_semana.append(dia)
        
        self.horario[dia] = {
            'hora_inicio': hora_inicio,
            'hora_fin': hora_fin
        }
        self.save()


class DisponibilidadConsultorio(models.Model):
    """
    Modelo para gestionar la disponibilidad de consultorios por fecha y hora.
    Permite reservar franjas horarias específicas.
    """
    
    class EstadoDisponibilidad(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', _('Disponible')
        RESERVADO = 'RESERVADO', _('Reservado')
        OCUPADO = 'OCUPADO', _('Ocupado')
        BLOQUEADO = 'BLOQUEADO', _('Bloqueado')
    
    consultorio = models.ForeignKey(
        Consultorio,
        on_delete=models.CASCADE,
        related_name='disponibilidades',
        verbose_name='Consultorio'
    )
    
    fecha = models.DateField(
        verbose_name='Fecha'
    )
    
    hora_inicio = models.TimeField(
        verbose_name='Hora de Inicio'
    )
    
    hora_fin = models.TimeField(
        verbose_name='Hora de Fin'
    )
    
    estado = models.CharField(
        max_length=15,
        choices=EstadoDisponibilidad.choices,
        default=EstadoDisponibilidad.DISPONIBLE,
        verbose_name='Estado'
    )
    
    terapeuta = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='disponibilidades_consultorio',
        limit_choices_to={'rol__in': ['TERAPEUTA', 'PSICOLOGO', 'MEDICO']},
        verbose_name='Terapeuta Asignado'
    )
    
    motivo_bloqueo = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Motivo de Bloqueo',
        help_text='Solo si el estado es Bloqueado'
    )
    
    notas = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    class Meta:
        verbose_name = 'Disponibilidad de Consultorio'
        verbose_name_plural = 'Disponibilidades de Consultorios'
        ordering = ['fecha', 'hora_inicio']
        unique_together = ['consultorio', 'fecha', 'hora_inicio']
        indexes = [
            models.Index(fields=['consultorio', 'fecha']),
            models.Index(fields=['estado']),
            models.Index(fields=['terapeuta', 'fecha']),
        ]
    
    def __str__(self):
        if self.fecha and self.hora_inicio and self.hora_fin:
            return f"{self.consultorio.nombre} - {self.fecha} {self.hora_inicio}-{self.hora_fin}"
        return f"{self.consultorio.nombre} - Sin horario definido"
    
    def clean(self):
        """Validaciones personalizadas."""
        from django.core.exceptions import ValidationError
        
        # Validar que las horas no sean None antes de comparar
        if self.hora_inicio and self.hora_fin and self.hora_inicio >= self.hora_fin:
            raise ValidationError({
                'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio.'
            })
    
    @property
    def duracion_minutos(self):
        """Calcula la duración en minutos."""
        from datetime import datetime
        
        # Validar que los campos no sean None
        if not self.fecha or not self.hora_inicio or not self.hora_fin:
            return 0
        
        try:
            inicio = datetime.combine(self.fecha, self.hora_inicio)
            fin = datetime.combine(self.fecha, self.hora_fin)
            return int((fin - inicio).total_seconds() / 60)
        except (TypeError, ValueError):
            return 0
    
    @property
    def esta_disponible(self):
        """Verifica si el horario está disponible."""
        return self.estado == self.EstadoDisponibilidad.DISPONIBLE
