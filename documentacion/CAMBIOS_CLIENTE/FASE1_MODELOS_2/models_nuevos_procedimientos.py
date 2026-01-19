# AGREGAR A: apps/procedimientos/models.py

from django.db import models
from django.core.validators import MinValueValidator
from apps.usuarios.models import Usuario
from apps.grupos.models import GrupoTerapeutico, Terapia


# MODIFICAR modelo CodigoCIE10 existente - agregar campo si no existe:
"""
    nombre = models.CharField(
        max_length=200,
        blank=True,
        help_text='Nombre descriptivo'
    )
"""

# MODIFICAR modelo Paciente existente - agregar estos campos:
"""
    codigo_enfermedad = models.ForeignKey(
        'CodigoCIE10',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pacientes',
        verbose_name='Código CIE-10'
    )
    
    # Deprecar (agregar null=True, blank=True):
    numero_historia_clinica = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text='[DEPRECADO]'
    )
"""


class ValoracionProfesional(models.Model):
    """Valoración individual por terapeuta"""
    paciente = models.ForeignKey(
        'Paciente',
        on_delete=models.CASCADE,
        related_name='valoraciones_profesionales'
    )
    terapeuta = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='valoraciones_realizadas'
    )
    terapia = models.ForeignKey(
        Terapia,
        on_delete=models.PROTECT,
        related_name='valoraciones'
    )
    fecha_valoracion = models.DateTimeField(auto_now_add=True)
    
    # Campos de valoración
    estado_salud_general = models.TextField()
    observaciones = models.TextField()
    recomendaciones = models.TextField()
    objetivos_terapeuticos = models.TextField(blank=True)
    
    # Estado
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADA', 'Completada'),
        ('REVISADA', 'Revisada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='COMPLETADA')
    
    # Firma
    firma_terapeuta = models.ImageField(upload_to='firmas_valoraciones/', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Valoración Profesional'
        verbose_name_plural = 'Valoraciones Profesionales'
        unique_together = ['paciente', 'terapeuta', 'terapia']
        ordering = ['-fecha_valoracion']
        
    def __str__(self):
        return f"{self.paciente} - {self.terapeuta} - {self.terapia}"
    
    def save(self, *args, **kwargs):
        # Auto-copiar firma del terapeuta
        if not self.firma_terapeuta and self.terapeuta.firma:
            self.firma_terapeuta = self.terapeuta.firma
        super().save(*args, **kwargs)


class AdmisionTerapia(models.Model):
    """Admisión por terapia ordenada por EPS"""
    paciente = models.ForeignKey(
        'Paciente',
        on_delete=models.CASCADE,
        related_name='admisiones'
    )
    terapia = models.ForeignKey(
        Terapia,
        on_delete=models.PROTECT,
        related_name='admisiones'
    )
    
    # Número EPS
    numero_admision = models.CharField(max_length=50, unique=True)
    
    # Vigencia (4 semanas)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    # Cantidad
    cantidad_ordenada = models.IntegerField(validators=[MinValueValidator(1)])
    cantidad_realizada = models.IntegerField(default=0)
    
    # Estado
    ESTADOS = [
        ('VIGENTE', 'Vigente'),
        ('VENCIDA', 'Vencida'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='VIGENTE')
    
    # Auditoría
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='admisiones_creadas'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Admisión por Terapia'
        verbose_name_plural = 'Admisiones por Terapia'
        ordering = ['-fecha_inicio']
        
    def __str__(self):
        return f"{self.numero_admision} - {self.paciente} - {self.terapia}"
    
    @property
    def esta_vigente(self):
        from django.utils import timezone
        hoy = timezone.now().date()
        return self.fecha_inicio <= hoy <= self.fecha_fin and self.estado == 'VIGENTE'
    
    @property
    def terapias_pendientes(self):
        return max(0, self.cantidad_ordenada - self.cantidad_realizada)
    
    @property
    def progreso_porcentaje(self):
        if self.cantidad_ordenada == 0:
            return 0
        return int((self.cantidad_realizada / self.cantidad_ordenada) * 100)


class AsistenciaSesion(models.Model):
    """Control de asistencia diaria"""
    grupo = models.ForeignKey(
        GrupoTerapeutico,
        on_delete=models.CASCADE,
        related_name='asistencias'
    )
    paciente = models.ForeignKey(
        'Paciente',
        on_delete=models.CASCADE,
        related_name='asistencias'
    )
    admision = models.ForeignKey(
        AdmisionTerapia,
        on_delete=models.CASCADE,
        related_name='asistencias'
    )
    
    # Sesión
    fecha = models.DateField()
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    
    # Asistencia
    asistio = models.BooleanField(default=False)
    justificada = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True)
    
    # Auditoría
    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='asistencias_registradas'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        unique_together = ['grupo', 'paciente', 'fecha']
        ordering = ['-fecha']
        
    def __str__(self):
        estado = "✓" if self.asistio else "✗"
        return f"{estado} {self.paciente} - {self.fecha}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Actualizar contador de admisión si asistió
        if self.asistio and self.admision:
            self.admision.cantidad_realizada += 1
            self.admision.save()
