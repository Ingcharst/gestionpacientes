# ✅ MODELO ASISTENCIA PACIENTE
# Agregar a: apps/grupos/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone


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
        related_name='asistencias_registradas',
        verbose_name='Registrado Por'
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
