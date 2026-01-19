from django.db import models
from apps.usuarios.models import Usuario
from apps.procedimientos.models import Paciente


class AlertaInasistencia(models.Model):
    """Alerta por 3 inasistencias consecutivas"""
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='alertas_inasistencia'
    )
    
    # Detalles
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    dias_consecutivos = models.IntegerField(default=0)
    fecha_ultima_inasistencia = models.DateField()
    
    # Estado
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('NOTIFICADA', 'Notificada'),
        ('ATENDIDA', 'Atendida'),
        ('CERRADA', 'Cerrada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    
    # Notificación
    sms_enviado = models.BooleanField(default=False)
    fecha_envio_sms = models.DateTimeField(null=True, blank=True)
    telefono_destino = models.CharField(max_length=20, blank=True)
    
    # Seguimiento
    atendida_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertas_inasistencia_atendidas'
    )
    fecha_atencion = models.DateTimeField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Alerta de Inasistencia'
        verbose_name_plural = 'Alertas de Inasistencia'
        ordering = ['-fecha_generacion']
        
    def __str__(self):
        return f"Alerta {self.paciente} - {self.dias_consecutivos} días"


class ConfiguracionAlerta(models.Model):
    """Configuración del sistema de alertas"""
    
    # Inasistencias
    dias_inasistencia_alerta = models.IntegerField(
        default=3,
        help_text='Días consecutivos para generar alerta'
    )
    
    # SMS
    mensaje_sms_template = models.TextField(
        default='Estimado acudiente, el paciente {nombre} ha faltado {dias} días consecutivos. '
                'Por favor comuníquese con la IPS al {telefono_ips}.'
    )
    telefono_ips = models.CharField(
        max_length=20,
        default='3001234567',
        help_text='Teléfono de contacto de la IPS'
    )
    
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Configuración de Alertas'
        verbose_name_plural = 'Configuraciones de Alertas'
        
    def __str__(self):
        return f"Config Alertas - {self.dias_inasistencia_alerta} días"
    
    @classmethod
    def get_config(cls):
        """Obtiene la configuración activa"""
        config, created = cls.objects.get_or_create(
            activo=True,
            defaults={'dias_inasistencia_alerta': 3}
        )
        return config
