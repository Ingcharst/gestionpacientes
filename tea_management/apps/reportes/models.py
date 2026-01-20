"""
Modelos para el módulo de reportes.
Por ahora no se requieren modelos específicos,
los reportes se generan directamente desde los modelos existentes.
"""

from django.db import models
from apps.procedimientos.models import Paciente, AdmisionTerapia
from apps.terapias.models import Terapia
from apps.usuarios.models import Usuario

class PlantillaInforme(models.Model):
    """
    Plantilla de texto predeterminado por terapia y rango de edad.
    Ejemplo: Cognitiva 3-6 años, Ocupacional 7-11 años, etc.
    """
    
    RANGOS_EDAD = [
        ('3-6', '3 a 6 años'),
        ('7-11', '7 a 11 años'),
        ('12-16', '12 a 16 años'),
    ]
    
    terapia = models.ForeignKey(
        Terapia,
        on_delete=models.CASCADE,
        related_name='plantillas_informe'
    )
    
    rango_edad = models.CharField(
        max_length=10,
        choices=RANGOS_EDAD,
        verbose_name='Rango de Edad'
    )
    
    # Contenido del informe
    titulo = models.CharField(
        max_length=200,
        default='INFORME DE TERAPIAS'
    )
    
    contenido_principal = models.TextField(
        verbose_name='Contenido del Informe',
        help_text='Texto predeterminado. Use {nombre_paciente}, {edad}, etc. para campos dinámicos'
    )
    
    recomendaciones_familia = models.TextField(
        blank=True,
        verbose_name='Recomendaciones Familia'
    )
    
    recomendaciones_escuela = models.TextField(
        blank=True,
        verbose_name='Recomendaciones Escolaridad'
    )
    
    # Control
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Plantilla de Informe'
        verbose_name_plural = 'Plantillas de Informes'
        unique_together = ['terapia', 'rango_edad']
        ordering = ['terapia', 'rango_edad']
    
    def __str__(self):
        return f"{self.terapia.nombre} - {self.get_rango_edad_display()}"
    
    def obtener_rango_edad_paciente(self, edad):
        """Determina el rango de edad según la edad del paciente"""
        if 3 <= edad <= 6:
            return '3-6'
        elif 7 <= edad <= 11:
            return '7-11'
        elif 12 <= edad <= 16:
            return '12-16'
        return None


class InformeEvolucion(models.Model):
    """
    Informe de evolución generado para un paciente.
    """
    
    ESTADOS = [
        ('BORRADOR', 'Borrador'),
        ('FINALIZADO', 'Finalizado'),
        ('ENVIADO', 'Enviado'),
    ]
    
    # Relaciones
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='informes_evolucion'
    )
    
    admision = models.ForeignKey(
        AdmisionTerapia,
        on_delete=models.CASCADE,
        related_name='informes',
        verbose_name='Admisión Relacionada'
    )
    
    terapia = models.ForeignKey(
        Terapia,
        on_delete=models.PROTECT,
        related_name='informes'
    )
    
    profesional = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='informes_generados',
        limit_choices_to={'rol__in': ['TERAPEUTA', 'MEDICO', 'PSICOLOGO']}
    )
    
    plantilla_usada = models.ForeignKey(
        PlantillaInforme,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Plantilla Utilizada'
    )
    
    # Periodo evaluado
    periodo_inicio = models.DateField(
        verbose_name='Inicio del Período Evaluado'
    )
    
    periodo_fin = models.DateField(
        verbose_name='Fin del Período Evaluado'
    )
    
    # Contenido
    contenido_informe = models.TextField(
        verbose_name='Contenido del Informe',
        help_text='Texto final del informe (se genera automáticamente de la plantilla)'
    )
    
    observaciones_especificas = models.TextField(
        blank=True,
        verbose_name='Observaciones Específicas del Profesional',
        help_text='Observaciones adicionales personalizadas'
    )
    
    # Firma
    firma_profesional = models.ImageField(
        upload_to='firmas_informes/',
        null=True,
        blank=True,
        verbose_name='Firma del Profesional'
    )
    
    # Estado y fechas
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='BORRADOR'
    )
    
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    
    # Archivo PDF generado
    archivo_pdf = models.FileField(
        upload_to='informes_pdf/',
        null=True,
        blank=True,
        verbose_name='PDF Generado'
    )
    
    class Meta:
        verbose_name = 'Informe de Evolución'
        verbose_name_plural = 'Informes de Evolución'
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"Informe {self.paciente.nombre_completo} - {self.terapia.nombre} ({self.periodo_inicio})"
    
    def save(self, *args, **kwargs):
        """Auto-copiar firma del profesional"""
        if not self.firma_profesional and self.profesional.firma:
            self.firma_profesional = self.profesional.firma
        super().save(*args, **kwargs)
    
    def generar_contenido_desde_plantilla(self):
        """
        Genera el contenido del informe sustituyendo placeholders
        """
        if not self.plantilla_usada:
            return
        
        # Datos del paciente
        contexto = {
            'nombre_paciente': self.paciente.nombre_completo,
            'edad': int(self.paciente.edad_actual) if self.paciente.edad_actual else 0,
            'documento': self.paciente.numero_documento,
            'fecha_nacimiento': self.paciente.fecha_nacimiento.strftime('%d/%m/%Y'),
            'admision': self.admision.numero_admision,
            'numero_intervenciones': self.admision.cantidad_realizada,
            'escolaridad': getattr(self.paciente, 'nivel_escolar', 'N/A'),
            'acudiente': self.paciente.nombre_responsable,
            'diagnostico': self.paciente.diagnostico_principal,
            'profesional': self.profesional.get_full_name(),
            'eps': self.paciente.eps,
            'autorizacion': self.admision.numero_admision,
            'periodo_inicio': self.periodo_inicio.strftime('%d/%m/%Y'),
            'periodo_fin': self.periodo_fin.strftime('%d/%m/%Y'),
        }
        
        # Sustituir en el contenido
        contenido = self.plantilla_usada.contenido_principal
        for clave, valor in contexto.items():
            contenido = contenido.replace(f'{{{clave}}}', str(valor))
        
        self.contenido_informe = contenido
        self.save(update_fields=['contenido_informe'])
    
    def finalizar(self):
        """Marca el informe como finalizado"""
        from django.utils import timezone
        self.estado = 'FINALIZADO'
        self.fecha_finalizacion = timezone.now()
        self.save()
