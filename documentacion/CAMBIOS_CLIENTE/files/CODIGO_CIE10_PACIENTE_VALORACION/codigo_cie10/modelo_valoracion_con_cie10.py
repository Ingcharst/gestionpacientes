# AGREGAR EN: apps/procedimientos/models.py

# En el modelo ValoracionProfesional, agregar este campo:

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
        related_name='valoraciones_como_terapeuta'
    )
    terapia = models.ForeignKey(
        Terapia,
        on_delete=models.PROTECT,
        related_name='valoraciones_profesionales_terapia'
    )
    
    # ✅ NUEVO CAMPO - AGREGAR:
    codigo_cie10 = models.ForeignKey(
        'CodigoCIE10',
        on_delete=models.PROTECT,
        related_name='valoraciones_profesionales',
        verbose_name='Código CIE-10',
        null=True,
        blank=True,
        help_text='Diagnóstico según clasificación CIE-10'
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
