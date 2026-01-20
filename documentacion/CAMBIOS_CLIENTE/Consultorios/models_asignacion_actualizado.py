# AGREGAR AL INICIO DEL ARCHIVO models.py (después de import Usuario):
from apps.terapias.models import Terapia  # ✅ IMPORTAR TERAPIA


# REEMPLAZAR CLASE AsignacionConsultorio COMPLETA:

class AsignacionConsultorio(models.Model):
    """
    Modelo para asignar terapeutas a consultorios.
    Gestiona qué terapeuta utiliza qué consultorio, para qué terapia y en qué horarios.
    """
    
    class TipoAsignacion(models.TextChoices):
        PERMANENTE = 'PERMANENTE', _('Asignación Permanente')
        TEMPORAL = 'TEMPORAL', _('Asignación Temporal')
        COMPARTIDA = 'COMPARTIDA', _('Asignación Compartida')
    
    consultorio = models.ForeignKey(
        Consultorio,
        on_delete=models.PROTECT,
        related_name='asignaciones',
        verbose_name='Consultorio'
    )
    
    terapeuta = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultorios_asignados',
        limit_choices_to={'rol__in': ['TERAPEUTA', 'PSICOLOGO', 'MEDICO']},
        verbose_name='Terapeuta'
    )
    
    # ✅ NUEVO CAMPO AGREGADO
    terapia = models.ForeignKey(
        Terapia,
        on_delete=models.PROTECT,
        related_name='asignaciones_consultorio',
        verbose_name='Terapia',
        help_text='Tipo de terapia que se realizará en este consultorio',
        null=True,  # Permitir null temporalmente para migración
        blank=True
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
            models.Index(fields=['terapia']),  # ✅ NUEVO ÍNDICE
        ]
    
    def __str__(self):
        terapia_nombre = f" - {self.terapia.nombre}" if self.terapia else ""
        return f"{self.terapeuta.get_full_name()} - {self.consultorio.nombre}{terapia_nombre}"
    
    def clean(self):
        """Validaciones personalizadas."""
        from django.core.exceptions import ValidationError
        
        # Validar que el usuario sea terapeuta
        if self.terapeuta and not self.terapeuta.es_terapeuta:
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
        return self.tipo_asignacion == self.TipoAsignacion.PERMANENTE or not self.fecha_fin
    
    def save(self, *args, **kwargs):
        """Validar antes de guardar."""
        self.full_clean()
        super().save(*args, **kwargs)
