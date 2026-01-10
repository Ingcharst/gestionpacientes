# MODELO CIE-10
# Archivo: apps/procedimientos/models.py
# AGREGAR AL FINAL del archivo, ANTES de ValoracionInicial

class CodigoCIE10(models.Model):
    """Catálogo de códigos CIE-10 (Clasificación Internacional de Enfermedades)"""
    
    codigo = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        verbose_name='Código CIE-10'
    )
    
    descripcion = models.TextField(
        verbose_name='Descripción'
    )
    
    categoria = models.CharField(
        max_length=100,
        db_index=True,
        blank=True,
        verbose_name='Categoría'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        verbose_name = 'Código CIE-10'
        verbose_name_plural = 'Códigos CIE-10'
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['categoria']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"
    
    @property
    def codigo_completo(self):
        """Retorna código con descripción para búsqueda"""
        return f"{self.codigo} - {self.descripcion}"


# ============================================================================
# MODIFICAR MODELO ValoracionInicial
# ============================================================================

# BUSCAR el campo diagnostico_cie10 en ValoracionInicial
# CAMBIAR de CharField a ForeignKey:

# ANTES:
# diagnostico_cie10 = models.CharField(max_length=10, blank=True)

# DESPUÉS:
diagnostico_cie10 = models.ForeignKey(
    CodigoCIE10,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='valoraciones',
    verbose_name='Diagnóstico CIE-10'
)

diagnostico_cie10_texto = models.CharField(
    max_length=10,
    blank=True,
    verbose_name='Código CIE-10 (texto)',
    help_text='Solo si no está en catálogo'
)
