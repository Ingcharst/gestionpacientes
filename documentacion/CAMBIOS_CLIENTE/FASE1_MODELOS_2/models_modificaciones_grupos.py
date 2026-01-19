# AGREGAR A: apps/usuarios/models.py
"""
En el modelo Usuario existente, agregar:

    firma = models.ImageField(
        upload_to='firmas/',
        null=True,
        blank=True,
        help_text='Firma digital del terapeuta'
    )
"""

# ============================================
# MODIFICAR: apps/grupos/models.py
# ============================================

# En el modelo AsignacionGrupo existente, agregar estos campos:
"""
    # Vincular con admisión
    admision_terapia = models.ForeignKey(
        'procedimientos.AdmisionTerapia',
        on_delete=models.CASCADE,
        related_name='asignaciones',
        null=True,  # Temporal para migración
        blank=True
    )
    
    # Control inasistencias
    dias_inasistencias_consecutivas = models.IntegerField(default=0)
    fecha_ultima_asistencia = models.DateField(null=True, blank=True)
    alerta_inasistencia_enviada = models.BooleanField(default=False)
    
    # Deprecar campo 'estado' si existe o agregar estos estados:
    ESTADOS_ASIGNACION = [
        ('ACTIVA', 'Activa'),
        ('FINALIZADA', 'Finalizada'),
        ('SUSPENDIDA', 'Suspendida'),
    ]
    # Si no existe, agregar:
    # estado = models.CharField(max_length=20, choices=ESTADOS_ASIGNACION, default='ACTIVA')
"""


# AGREGAR A: apps/grupos/models.py

from django.db import models


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
        related_name='alertas_generadas'
    )
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    resuelta_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='alertas_resueltas'
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
