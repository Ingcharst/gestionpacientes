import math
from tkinter import CASCADE
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime, time, timedelta
from apps.terapias.models import Terapia
from django.conf import settings

class GrupoTerapeutico(models.Model):
    """
    Modelo para grupos terapéuticos organizados por horario.
    Ejemplo: "Grupo 9:00 a.m." con capacidad máxima de 10 pacientes.
    """
    
    DIAS_SEMANA = [
        ('L', 'Lunes'),
        ('M', 'Martes'),
        ('X', 'Miércoles'),
        ('J', 'Jueves'),
        ('V', 'Viernes'),
        ('S', 'Sábado'),
        ('D', 'Domingo'),
    ]
    
    # Información Básica
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre del Grupo',
        help_text='Ej: Grupo 9:00 a.m.'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )

    terapia = models.ForeignKey(
        Terapia,
        on_delete=models.PROTECT,
        related_name='grupos_terapeuticos',
        verbose_name='Terapia',
        null=True,
        blank=True,
        help_text='Tipo de terapia que ofrece este grupo'
    )

    # Horario
    hora_inicio = models.TimeField(
        verbose_name='Hora de Inicio',
        help_text='Hora en que inicia la sesión grupal'
    )
    
    hora_fin = models.TimeField(
        verbose_name='Hora de Fin',
        help_text='Hora en que finaliza la sesión grupal'
    )
    
    # Días Disponibles (JSON Array)
    dias_disponibles = models.JSONField(
        default=list,
        verbose_name='Días Disponibles',
        help_text='Lista de días en que funciona el grupo. Ej: ["L","M","X","J","V"]'
    )
    
    # Capacidad
    capacidad_maxima = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        default=10,
        verbose_name='Capacidad Máxima',
        help_text='Número máximo de pacientes que pueden estar asignados al grupo'
    )
    
    pacientes_actuales = models.PositiveIntegerField(
        default=0,
        verbose_name='Pacientes Actuales',
        help_text='Número actual de pacientes asignados (se actualiza automáticamente)'
    )
    
    # Estado
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    notas = models.TextField(
        blank=True,
        verbose_name='Notas Adicionales'
    )
    
    edad_minima = models.FloatField(
        default=2,
        null=True,
        blank=True,
        verbose_name='Edad Mínima (años)',
        help_text='Edad mínima requerida para pertenecer al grupo'
    )
    
    edad_maxima = models.FloatField(
        default=20,
        null=True,
        blank=True,
        verbose_name='Edad Máxima (años)',
        help_text='Edad máxima permitida para pertenecer al grupo'
    )
    
    class Meta:
        verbose_name = 'Grupo Terapéutico'
        verbose_name_plural = 'Grupos Terapéuticos'
        ordering = ['hora_inicio', 'nombre']
        indexes = [
            models.Index(fields=['activo', 'hora_inicio']),
            models.Index(fields=['capacidad_maxima', 'pacientes_actuales']),
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')})"
    
    def clean(self):
        """Validaciones del modelo"""
        if self.hora_fin <= self.hora_inicio:
            raise ValidationError({
                'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio'
            })
        
        if not isinstance(self.dias_disponibles, list):
            raise ValidationError({
                'dias_disponibles': 'Los días disponibles deben ser una lista'
            })
        
        # Validar que los días sean válidos
        dias_validos = [dia[0] for dia in self.DIAS_SEMANA]
        for dia in self.dias_disponibles:
            if dia not in dias_validos:
                raise ValidationError({
                    'dias_disponibles': f'Día inválido: {dia}. Debe ser uno de: {dias_validos}'
                })
    
    @property
    def cupos_disponibles(self):
        """Calcula cupos disponibles en el grupo"""
        return max(0, self.capacidad_maxima - self.pacientes_actuales)
    
    @property
    def tiene_cupo(self):
        """Verifica si hay cupo disponible"""
        return self.pacientes_actuales < self.capacidad_maxima
    
    @property
    def porcentaje_ocupacion(self):
        """Calcula el porcentaje de ocupación del grupo"""
        if self.capacidad_maxima == 0:
            return 0
        return round((self.pacientes_actuales / self.capacidad_maxima) * 100, 2)
    
    @property
    def esta_lleno(self):
        """Verifica si el grupo está lleno"""
        return self.pacientes_actuales >= self.capacidad_maxima
    
    @property
    def dias_semana_texto(self):
        """Retorna los días de la semana en texto legible"""
        dias_dict = dict(self.DIAS_SEMANA)
        return ', '.join([dias_dict.get(dia, dia) for dia in self.dias_disponibles])
    
    def actualizar_contador_pacientes(self):
        """Actualiza el contador de pacientes actuales basado en asignaciones activas"""
        self.pacientes_actuales = self.asignaciones.filter(
            estado='ACTIVA'
        ).count()
        self.save(update_fields=['pacientes_actuales'])
    
    def puede_asignar_dias(self, dias_solicitados):
        """
        Verifica si los días solicitados están disponibles en el grupo.
        
        Args:
            dias_solicitados: Lista de días (ej: ['L', 'M', 'X'])
        
        Returns:
            bool: True si todos los días están disponibles
        """
        if not isinstance(dias_solicitados, list):
            return False
        
        return all(dia in self.dias_disponibles for dia in dias_solicitados)
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class AsignacionGrupo(models.Model):
    """
    Modelo para asignación de pacientes a grupos terapéuticos.
    Controla días de asistencia y número de terapias semanales.
    """
    
    class Estado(models.TextChoices):
        ACTIVA = 'ACTIVA', _('Activa')
        SUSPENDIDA = 'SUSPENDIDA', _('Suspendida')
        FINALIZADA = 'FINALIZADA', _('Finalizada')
        CANCELADA = 'CANCELADA', _('Cancelada')
    
    # Relaciones
    paciente = models.ForeignKey(
        'procedimientos.Paciente',
        on_delete=models.CASCADE,
        related_name='asignaciones_grupo',
        verbose_name='Paciente'
    )
    
    grupo = models.ForeignKey(
        GrupoTerapeutico,
        on_delete=models.CASCADE,
        related_name='asignaciones',
        verbose_name='Grupo Terapéutico'
    )

    # NUEVO: Número total de terapias asignadas
    numero_terapias_asignadas = models.PositiveIntegerField(
        default=20,
        verbose_name='Número Total de Terapias Asignadas',
        help_text='Cantidad total de sesiones programadas'
    )


    terapias_completadas = models.PositiveIntegerField(
        default=0,
        verbose_name='Terapias Completadas'
    )

    
    # Días de Asistencia (JSON Array)
    dias_asistencia = models.JSONField(
        default=list,
        verbose_name='Días de Asistencia',
        help_text='Días en que el paciente asiste. Ej: ["L","M","X"]'
    )

    dias_inasistencias_consecutivas = models.IntegerField(default=0)
    fecha_ultima_asistencia = models.DateField(null=True, blank=True)
    alerta_inasistencia_enviada = models.BooleanField(default=False)
    
    # Terapias
    numero_terapias_semanales = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        default=3,
        verbose_name='Número de Terapias Semanales',
        help_text='Cantidad de sesiones terapéuticas por semana'
    )

    admision_terapia = models.ForeignKey(
        'procedimientos.AdmisionTerapia',
        on_delete=models.CASCADE,
        related_name='asignaciones',
        null=True,  # Temporal para migración
        blank=True
    )
    
    # Fechas
    fecha_inicio_asignacion = models.DateField(
        default=timezone.now,
        verbose_name='Fecha de Inicio'
    )
    
    fecha_fin_asignacion = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Fin',
        help_text='Fecha en que finalizó la asignación'
    )
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ACTIVA,
        verbose_name='Estado'
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    notas = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    motivo_suspension = models.TextField(
        blank=True,
        verbose_name='Motivo de Suspensión/Finalización'
    )
    
    class Meta:
        verbose_name = 'Asignación a Grupo'
        verbose_name_plural = 'Asignaciones a Grupos'
        ordering = ['-fecha_inicio_asignacion']
        unique_together = [['paciente', 'grupo', 'estado']]
        indexes = [
            models.Index(fields=['estado', 'fecha_inicio_asignacion']),
            models.Index(fields=['paciente', 'estado']),
            models.Index(fields=['grupo', 'estado']),
        ]
    
    def __str__(self):
        return f"{self.paciente.nombres} {self.paciente.apellidos} → {self.grupo.nombre} ({self.get_estado_display()})"
    
    def clean(self):
        """Validaciones del modelo"""
        # Validar que los días de asistencia sean válidos
        if not isinstance(self.dias_asistencia, list):
            raise ValidationError({
                'dias_asistencia': 'Los días de asistencia deben ser una lista'
            })
        
        # Validar que los días estén disponibles en el grupo
        if self.grupo and not self.grupo.puede_asignar_dias(self.dias_asistencia):
            raise ValidationError({
                'dias_asistencia': f'Los días solicitados no están disponibles en el grupo. Días disponibles: {self.grupo.dias_disponibles}'
            })
        
        # Validar que el número de terapias no exceda los días de asistencia
        if len(self.dias_asistencia) < self.numero_terapias_semanales:
            raise ValidationError({
                'numero_terapias_semanales': f'El número de terapias ({self.numero_terapias_semanales}) no puede exceder los días de asistencia ({len(self.dias_asistencia)})'
            })
        
        # Validar fechas
        if self.fecha_fin_asignacion and self.fecha_fin_asignacion < self.fecha_inicio_asignacion:
            raise ValidationError({
                'fecha_fin_asignacion': 'La fecha de fin no puede ser anterior a la fecha de inicio'
            })
        
        # Validar que no exista otra asignación activa del mismo paciente al mismo grupo
        if self.estado == 'ACTIVA':
            asignaciones_activas = AsignacionGrupo.objects.filter(
                paciente=self.paciente,
                grupo=self.grupo,
                estado='ACTIVA'
            ).exclude(pk=self.pk)
            
            if asignaciones_activas.exists():
                raise ValidationError(
                    f'El paciente ya tiene una asignación activa a este grupo'
                )
    
    @property
    def dias_asistencia_texto(self):
        """Retorna los días de asistencia en texto legible"""
        dias_dict = dict(GrupoTerapeutico.DIAS_SEMANA)
        return ', '.join([dias_dict.get(dia, dia) for dia in self.dias_asistencia])

    def calcular_fecha_fin_automatica(self):
            """
            Calcula la fecha de fin basada en el total de terapias 
            y la frecuencia semanal.
            """
            if self.numero_terapias_semanales > 0 and self.numero_terapias_asignadas > 0:
                # Ejemplo: 20 sesiones / 3 por semana = 6.66 -> 7 semanas
                semanas_necesarias = math.ceil(self.numero_terapias_asignadas / self.numero_terapias_semanales)
                # Calculamos los días (semanas * 7)
                dias_totales = semanas_necesarias * 7
                # Retornamos la fecha de inicio + los días calculados
                return self.fecha_inicio_asignacion + timedelta(days=dias_totales)
            return None

    @property
    def duracion_dias(self):
        """Calcula la duración en días de la asignación"""
        if self.fecha_fin_asignacion:
            return (self.fecha_fin_asignacion - self.fecha_inicio_asignacion).days
        return (timezone.now().date() - self.fecha_inicio_asignacion).days
    
    @property
    def esta_activa(self):
        """Verifica si la asignación está activa"""
        return self.estado == 'ACTIVA'
    
    def finalizar(self, motivo=''):
        """Finaliza la asignación"""
        self.estado = 'FINALIZADA'
        self.fecha_fin_asignacion = timezone.now().date()
        self.motivo_suspension = motivo
        self.save()
    
    def suspender(self, motivo=''):
        """Suspende temporalmente la asignación"""
        self.estado = 'SUSPENDIDA'
        self.motivo_suspension = motivo
        self.save()
    
    def reactivar(self):
        """Reactiva una asignación suspendida"""
        if self.estado == 'SUSPENDIDA':
            self.estado = 'ACTIVA'
            self.motivo_suspension = ''
            self.save()
    
    def cancelar(self, motivo=''):
        """Cancela la asignación"""
        self.estado = 'CANCELADA'
        self.fecha_fin_asignacion = timezone.now().date()
        self.motivo_suspension = motivo
        self.save()
    
    def save(self, *args, **kwargs):
        if not self.fecha_fin_asignacion:
            self.fecha_fin_asignacion = self.calcular_fecha_fin_automatica()
        self.full_clean()
        super().save(*args, **kwargs)


class PacientePendiente(models.Model):
    """
    Modelo para pacientes en lista de espera que no tienen cupo asignado.
    Genera alertas automáticas para el personal administrativo.
    """
    
    class Prioridad(models.TextChoices):
        ALTA = 'ALTA', _('Alta')
        MEDIA = 'MEDIA', _('Media')
        BAJA = 'BAJA', _('Baja')
    
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', _('Pendiente de Asignación')
        ASIGNADO = 'ASIGNADO', _('Asignado a Grupo')
        CANCELADO = 'CANCELADO', _('Cancelado')
    
    # Relaciones
    paciente = models.ForeignKey(
        'procedimientos.Paciente',
        on_delete=models.CASCADE,
        related_name='solicitudes_pendientes',
        verbose_name='Paciente'
    )
    
    # Preferencias
    preferencia_horario = models.TimeField(
        verbose_name='Horario Preferido',
        help_text='Hora preferida para asistir'
    )
    
    dias_preferidos = models.JSONField(
        default=list,
        verbose_name='Días Preferidos',
        help_text='Días en que puede asistir. Ej: ["L","M","X"]'
    )
    
    # Prioridad
    prioridad = models.CharField(
        max_length=10,
        choices=Prioridad.choices,
        default=Prioridad.MEDIA,
        verbose_name='Prioridad'
    )
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name='Estado'
    )
    
    # Fechas
    fecha_solicitud = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Solicitud'
    )
    
    fecha_asignacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Asignación',
        help_text='Fecha en que fue asignado a un grupo'
    )
    
    # Grupo Asignado (cuando se resuelve)
    grupo_asignado = models.ForeignKey(
        GrupoTerapeutico,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pacientes_asignados_desde_pendientes',
        verbose_name='Grupo Asignado'
    )
    
    # Metadatos
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    motivo_cancelacion = models.TextField(
        blank=True,
        verbose_name='Motivo de Cancelación'
    )
    
    class Meta:
        verbose_name = 'Paciente Pendiente de Asignación'
        verbose_name_plural = 'Pacientes Pendientes de Asignación'
        ordering = ['-prioridad', 'fecha_solicitud']
        indexes = [
            models.Index(fields=['estado', 'prioridad', 'fecha_solicitud']),
            models.Index(fields=['paciente', 'estado']),
        ]
    
    def __str__(self):
        return f"{self.paciente.nombres} {self.paciente.apellidos} - {self.get_prioridad_display()} ({self.get_estado_display()})"
    
    def clean(self):
        """Validaciones del modelo"""
        if not isinstance(self.dias_preferidos, list):
            raise ValidationError({
                'dias_preferidos': 'Los días preferidos deben ser una lista'
            })
        
        # Validar que los días sean válidos
        dias_validos = [dia[0] for dia in GrupoTerapeutico.DIAS_SEMANA]
        for dia in self.dias_preferidos:
            if dia not in dias_validos:
                raise ValidationError({
                    'dias_preferidos': f'Día inválido: {dia}. Debe ser uno de: {dias_validos}'
                })
    
    @property
    def dias_esperando(self):
        """Calcula los días que lleva esperando"""
        if self.estado == 'ASIGNADO' and self.fecha_asignacion:
            return (self.fecha_asignacion - self.fecha_solicitud).days
        return (timezone.now() - self.fecha_solicitud).days
    
    @property
    def dias_preferidos_texto(self):
        """Retorna los días preferidos en texto legible"""
        dias_dict = dict(GrupoTerapeutico.DIAS_SEMANA)
        return ', '.join([dias_dict.get(dia, dia) for dia in self.dias_preferidos])
    
    @property
    def esta_pendiente(self):
        """Verifica si está pendiente de asignación"""
        return self.estado == 'PENDIENTE'
    
    def marcar_como_asignado(self, grupo):
        """Marca el paciente como asignado a un grupo"""
        self.estado = 'ASIGNADO'
        self.grupo_asignado = grupo
        self.fecha_asignacion = timezone.now()
        self.save()
    
    def cancelar(self, motivo=''):
        """Cancela la solicitud pendiente"""
        self.estado = 'CANCELADO'
        self.motivo_cancelacion = motivo
        self.save()
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class AlertaCupo(models.Model):
    """Alerta cuando grupo queda sobrecupo por cambio de capacidad"""
    grupo = models.ForeignKey(
        'GrupoTerapeutico',
        on_delete=models.CASCADE,
        related_name='alertas_cupo'
    )
    
    # Cambio
    capacidad_anterior = models.IntegerField()
    capacidad_nueva = models.IntegerField()
    pacientes_excedentes = models.IntegerField()
    
    # Estado
    ESTADOS = [
        ('PENDIENTE', 'Pendiente de reasignación'),
        ('EN_PROCESO', 'En proceso'),
        ('RESUELTA', 'Resuelta'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    
    # Auditoría
    generada_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='alertas_cupo_generadas'
    )
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    resuelta_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='alertas_cupo_resueltas'
    )
    
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Alerta de Cupo'
        verbose_name_plural = 'Alertas de Cupo'
        ordering = ['-fecha_generacion']
        
    def __str__(self):
        return f"Alerta {self.grupo} - {self.pacientes_excedentes} pacientes"
    
    def pacientes_afectados(self):
        """Obtiene pacientes que deben ser reasignados"""
        from apps.grupos.models import AsignacionGrupo
        
        # Pacientes actuales ordenados por fecha de asignación (últimos primero)
        asignaciones = AsignacionGrupo.objects.filter(
            grupo=self.grupo,
            estado='ACTIVA',
            admision_terapia__estado='VIGENTE'
        ).order_by('-fecha_inicio')[:self.pacientes_excedentes]
        
        return asignaciones



class AsistenciaPaciente(models.Model):
    """
    Registro diario de asistencia de pacientes a grupos terapéuticos
    """
    
    # Relaciones
    paciente = models.ForeignKey(
        'procedimientos.Paciente',
        on_delete=models.CASCADE,
        related_name='asistencias_grupo',
        verbose_name='Paciente'
    )
    
    grupo = models.ForeignKey(
        'GrupoTerapeutico',
        on_delete=models.CASCADE,
        related_name='asistencias',
        verbose_name='Grupo'
    )
    
    asignacion = models.ForeignKey(
        'AsignacionGrupo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asistencias_registradas',
        verbose_name='Asignación'
    )
    
    # Datos de asistencia
    fecha = models.DateField(
        default=timezone.now,
        verbose_name='Fecha',
        db_index=True
    )
    
    asistio = models.BooleanField(
        default=True,
        verbose_name='Asistió'
    )
    
    justificada = models.BooleanField(
        default=False,
        verbose_name='Inasistencia Justificada',
        help_text='Marcar si la falta está justificada'
    )
    
    # Horarios
    hora_inicio = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Hora Inicio'
    )
    
    hora_fin = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Hora Fin'
    )
    
    # Observaciones
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    # Metadatos
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='Usuario_registra',
        verbose_name='Registró asistencia'
    )
    
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Registro'
    )
    
    class Meta:
        verbose_name = 'Asistencia de Paciente'
        verbose_name_plural = 'Asistencias de Pacientes'
        ordering = ['-fecha', 'paciente__apellidos']
        unique_together = [['paciente', 'grupo', 'fecha']]  # Una asistencia por día
        indexes = [
            models.Index(fields=['fecha', 'grupo']),
            models.Index(fields=['paciente', 'fecha']),
            models.Index(fields=['asistio']),
        ]
    
    def __str__(self):
        estado = "✓" if self.asistio else ("✗ (Just.)" if self.justificada else "✗")
        return f"{self.paciente.nombre_completo} - {self.fecha} {estado}"
    
    @property
    def estado_display(self):
        """Retorna el estado legible"""
        if self.asistio:
            return "Asistió"
        elif self.justificada:
            return "Falta Justificada"
        else:
            return "Inasistencia"


