# MODELO: EVOLUCIÓN DE PACIENTE
# Archivo: apps/procedimientos/models.py
# AGREGAR AL FINAL del archivo

from django.utils import timezone

class EvolucionPaciente(models.Model):
    """Registro de evolución y seguimiento de terapia del paciente"""
    
    class TipoSesion(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', 'Individual'
        GRUPAL = 'GRUPAL', 'Grupal'
        EVALUACION = 'EVALUACION', 'Evaluación'
        INTERCONSULTA = 'INTERCONSULTA', 'Interconsulta'
    
    class Desempeno(models.TextChoices):
        EXCELENTE = 'EXCELENTE', 'Excelente'
        BUENO = 'BUENO', 'Bueno'
        REGULAR = 'REGULAR', 'Regular'
        REQUIERE_APOYO = 'REQUIERE_APOYO', 'Requiere Apoyo'
        NO_PARTICIPO = 'NO_PARTICIPO', 'No Participó'
    
    # Relaciones
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='evoluciones',
        verbose_name='Paciente'
    )
    
    profesional = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='evoluciones_registradas',
        verbose_name='Profesional'
    )
    
    terapia = models.ForeignKey(
        'Terapia',
        on_delete=models.PROTECT,
        related_name='evoluciones',
        verbose_name='Terapia'
    )
    
    grupo = models.ForeignKey(
        'grupos.GrupoTerapeutico',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evoluciones',
        verbose_name='Grupo Terapéutico'
    )
    
    # Información de la sesión
    fecha_sesion = models.DateField(
        default=timezone.now,
        verbose_name='Fecha de la Sesión'
    )
    
    hora_inicio = models.TimeField(
        verbose_name='Hora de Inicio'
    )
    
    hora_fin = models.TimeField(
        verbose_name='Hora de Fin'
    )
    
    tipo_sesion = models.CharField(
        max_length=20,
        choices=TipoSesion.choices,
        default=TipoSesion.GRUPAL,
        verbose_name='Tipo de Sesión'
    )
    
    numero_sesion = models.IntegerField(
        default=1,
        verbose_name='Número de Sesión',
        help_text='Sesión número X del total asignado'
    )
    
    asistio = models.BooleanField(
        default=True,
        verbose_name='Asistió a la Sesión'
    )
    
    # Contenido de la evolución
    objetivos_trabajados = models.TextField(
        verbose_name='Objetivos Trabajados',
        help_text='Objetivos terapéuticos abordados en la sesión'
    )
    
    actividades_realizadas = models.TextField(
        verbose_name='Actividades Realizadas',
        help_text='Descripción de actividades y ejercicios realizados'
    )
    
    desempeno = models.CharField(
        max_length=20,
        choices=Desempeno.choices,
        verbose_name='Desempeño del Paciente'
    )
    
    logros_obtenidos = models.TextField(
        blank=True,
        verbose_name='Logros Obtenidos',
        help_text='Avances y logros observados en la sesión'
    )
    
    dificultades_observadas = models.TextField(
        blank=True,
        verbose_name='Dificultades Observadas',
        help_text='Dificultades o retos encontrados'
    )
    
    observaciones_conducta = models.TextField(
        blank=True,
        verbose_name='Observaciones de Conducta',
        help_text='Aspectos conductuales relevantes'
    )
    
    observaciones_generales = models.TextField(
        blank=True,
        verbose_name='Observaciones Generales'
    )
    
    recomendaciones = models.TextField(
        blank=True,
        verbose_name='Recomendaciones',
        help_text='Recomendaciones para próximas sesiones o para el hogar'
    )
    
    proximos_objetivos = models.TextField(
        blank=True,
        verbose_name='Próximos Objetivos',
        help_text='Objetivos para trabajar en próximas sesiones'
    )
    
    # Evaluación cuantitativa (opcional)
    nivel_atencion = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        verbose_name='Nivel de Atención (1-5)',
        help_text='1=Muy bajo, 5=Excelente'
    )
    
    nivel_participacion = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        verbose_name='Nivel de Participación (1-5)'
    )
    
    nivel_colaboracion = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        verbose_name='Nivel de Colaboración (1-5)'
    )
    
    nivel_comprension = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        verbose_name='Nivel de Comprensión (1-5)'
    )
    
    # Material de apoyo
    material_utilizado = models.TextField(
        blank=True,
        verbose_name='Material Utilizado',
        help_text='Material didáctico o recursos utilizados'
    )
    
    tarea_asignada = models.TextField(
        blank=True,
        verbose_name='Tarea Asignada',
        help_text='Tareas o ejercicios para realizar en casa'
    )
    
    # Metadatos
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Registro'
    )
    
    ultima_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Modificación'
    )
    
    firmado = models.BooleanField(
        default=False,
        verbose_name='Evolución Firmada',
        help_text='Indica si la evolución ha sido finalizada y firmada'
    )
    
    class Meta:
        verbose_name = 'Evolución de Paciente'
        verbose_name_plural = 'Evoluciones de Pacientes'
        ordering = ['-fecha_sesion', '-hora_inicio']
        indexes = [
            models.Index(fields=['paciente', 'fecha_sesion']),
            models.Index(fields=['profesional', 'fecha_sesion']),
            models.Index(fields=['terapia', 'fecha_sesion']),
        ]
    
    def __str__(self):
        return f"Evolución {self.paciente.nombre_completo} - {self.fecha_sesion}"
    
    @property
    def duracion_sesion(self):
        """Calcula la duración de la sesión en minutos"""
        if self.hora_inicio and self.hora_fin:
            from datetime import datetime, timedelta
            inicio = datetime.combine(self.fecha_sesion, self.hora_inicio)
            fin = datetime.combine(self.fecha_sesion, self.hora_fin)
            duracion = fin - inicio
            return int(duracion.total_seconds() / 60)
        return 0
    
    @property
    def promedio_evaluacion(self):
        """Calcula el promedio de las evaluaciones cuantitativas"""
        evaluaciones = [
            self.nivel_atencion,
            self.nivel_participacion,
            self.nivel_colaboracion,
            self.nivel_comprension
        ]
        evaluaciones_validas = [e for e in evaluaciones if e is not None]
        if evaluaciones_validas:
            return round(sum(evaluaciones_validas) / len(evaluaciones_validas), 1)
        return None
    
    def save(self, *args, **kwargs):
        # Calcular número de sesión automáticamente
        if not self.pk:  # Solo en creación
            sesiones_anteriores = EvolucionPaciente.objects.filter(
                paciente=self.paciente,
                terapia=self.terapia
            ).count()
            self.numero_sesion = sesiones_anteriores + 1
        
        super().save(*args, **kwargs)
