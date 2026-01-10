# ============================================================================
# SPRINT 1 - NUEVO MODELO: VALORACION INICIAL
# apps/procedimientos/models.py
# ============================================================================

"""
INSTRUCCIONES:
Este modelo se agrega AL FINAL del archivo apps/procedimientos/models.py
(después del último modelo, antes del final del archivo)
"""

class ValoracionInicial(models.Model):
    """
    Valoración inicial del paciente por profesional.
    Registra todos los problemas detectados y recomendaciones de terapia.
    
    FLUJO:
    1. Paciente ingresa con estado ADMITIDO
    2. Profesional realiza valoración
    3. Al completar valoración, paciente pasa a PENDIENTE_ASIGNACION
    """
    
    class TipoProblema(models.TextChoices):
        LENGUAJE = 'LENGUAJE', _('Problemas de Lenguaje')
        MOVILIDAD = 'MOVILIDAD', _('Problemas de Movilidad')
        COGNITIVO = 'COGNITIVO', _('Problemas Cognitivos')
        CONDUCTUAL = 'CONDUCTUAL', _('Problemas de Conducta')
        SENSORIAL = 'SENSORIAL', _('Problemas Sensoriales')
        SOCIAL = 'SOCIAL', _('Dificultades Sociales')
        EMOCIONAL = 'EMOCIONAL', _('Problemas Emocionales')
        ATENCION = 'ATENCION', _('Problemas de Atención/Concentración')
        APRENDIZAJE = 'APRENDIZAJE', _('Dificultades de Aprendizaje')
        COMUNICACION = 'COMUNICACION', _('Problemas de Comunicación')
        OTRO = 'OTRO', _('Otro')
    
    # =========================================================================
    # RELACIONES
    # =========================================================================
    
    paciente = models.OneToOneField(
        'Paciente',
        on_delete=models.PROTECT,
        related_name='valoracion_inicial',
        verbose_name='Paciente'
    )
    
    profesional = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='valoraciones_realizadas',
        verbose_name='Profesional que Valora',
        limit_choices_to={'rol__in': ['TERAPEUTA', 'MEDICO', 'PSICOLOGO', 'ADMIN']}
    )
    
    # =========================================================================
    # INFORMACIÓN GENERAL DE LA VALORACIÓN
    # =========================================================================
    
    codigo_valoracion = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name='Código de Valoración',
        help_text='Se genera automáticamente'
    )
    
    fecha_valoracion = models.DateField(
        default=timezone.now,
        verbose_name='Fecha de Valoración'
    )
    
    hora_inicio = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Hora de Inicio'
    )
    
    hora_fin = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Hora de Finalización'
    )
    
    # =========================================================================
    # MOTIVO Y ANTECEDENTES
    # =========================================================================
    
    motivo_consulta = models.TextField(
        verbose_name='Motivo de Consulta',
        help_text='¿Por qué acude el paciente?'
    )
    
    antecedentes_personales = models.TextField(
        blank=True,
        verbose_name='Antecedentes Personales',
        help_text='Historial médico relevante'
    )
    
    antecedentes_familiares = models.TextField(
        blank=True,
        verbose_name='Antecedentes Familiares',
        help_text='Historial familiar relevante'
    )
    
    desarrollo_evolutivo = models.TextField(
        blank=True,
        verbose_name='Desarrollo Evolutivo',
        help_text='Hitos del desarrollo, embarazo, parto, etc.'
    )
    
    # =========================================================================
    # EVALUACIÓN Y PROBLEMAS DETECTADOS
    # =========================================================================
    
    observaciones_generales = models.TextField(
        verbose_name='Observaciones Generales de la Evaluación',
        help_text='Impresiones generales del profesional'
    )
    
    # Problemas detectados (almacenados como JSON para flexibilidad)
    problemas_detectados = models.JSONField(
        default=list,
        verbose_name='Problemas Detectados',
        help_text='Lista de problemas identificados durante la valoración'
    )
    # Formato JSON:
    # [
    #   {
    #     "tipo": "LENGUAJE",
    #     "descripcion": "Dificultad en expresión verbal",
    #     "severidad": "MODERADA",  # LEVE, MODERADA, SEVERA
    #     "observaciones": "Presenta tartamudeo ocasional"
    #   },
    #   {
    #     "tipo": "MOVILIDAD",
    #     "descripcion": "Coordinación motora fina deficiente",
    #     "severidad": "LEVE",
    #     "observaciones": "Dificultad para manipular objetos pequeños"
    #   }
    # ]
    
    nivel_funcionalidad = models.CharField(
        max_length=20,
        choices=[
            ('INDEPENDIENTE', 'Independiente'),
            ('SEMI_DEPENDIENTE', 'Semi-dependiente'),
            ('DEPENDIENTE', 'Dependiente'),
        ],
        null=True,
        blank=True,
        verbose_name='Nivel de Funcionalidad'
    )
    
    # =========================================================================
    # EVALUACIONES ESPECÍFICAS POR ÁREA
    # =========================================================================
    
    evaluacion_lenguaje = models.TextField(
        blank=True,
        verbose_name='Evaluación de Lenguaje',
        help_text='Evaluación detallada del área de lenguaje'
    )
    
    evaluacion_motora = models.TextField(
        blank=True,
        verbose_name='Evaluación Motora',
        help_text='Evaluación de habilidades motoras'
    )
    
    evaluacion_cognitiva = models.TextField(
        blank=True,
        verbose_name='Evaluación Cognitiva',
        help_text='Evaluación de funciones cognitivas'
    )
    
    evaluacion_conductual = models.TextField(
        blank=True,
        verbose_name='Evaluación Conductual',
        help_text='Evaluación de comportamiento y conducta'
    )
    
    evaluacion_social = models.TextField(
        blank=True,
        verbose_name='Evaluación Social',
        help_text='Evaluación de habilidades sociales e interacción'
    )
    
    # =========================================================================
    # PRUEBAS Y TESTS APLICADOS
    # =========================================================================
    
    pruebas_aplicadas = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Pruebas/Tests Aplicados',
        help_text='Tests psicológicos o evaluaciones estandarizadas aplicadas'
    )
    # Formato JSON:
    # [
    #   {
    #     "nombre": "Test WISC-IV",
    #     "puntuacion": "85",
    #     "interpretacion": "CI dentro del promedio"
    #   }
    # ]
    
    # =========================================================================
    # DIAGNÓSTICO Y RECOMENDACIONES
    # =========================================================================
    
    diagnostico_profesional = models.TextField(
        verbose_name='Diagnóstico del Profesional',
        help_text='Impresión diagnóstica del profesional'
    )
    
    diagnostico_cie10 = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Código CIE-10',
        help_text='Código de diagnóstico CIE-10 (si aplica)'
    )
    
    # Terapias recomendadas (relación muchos a muchos)
    terapias_recomendadas = models.ManyToManyField(
        'terapias.Terapia',
        related_name='valoraciones',
        verbose_name='Terapias Recomendadas',
        help_text='Tipos de terapias recomendadas para el paciente'
    )
    
    numero_sesiones_recomendado = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Número de Sesiones Recomendado',
        help_text='Cantidad total de sesiones sugeridas'
    )
    
    frecuencia_recomendada = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Frecuencia Recomendada',
        help_text='Ej: 2 veces por semana, 3 veces por semana'
    )
    
    duracion_estimada_tratamiento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Duración Estimada del Tratamiento',
        help_text='Ej: 6 meses, 1 año'
    )
    
    observaciones_recomendaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones sobre Recomendaciones',
        help_text='Notas adicionales sobre el tratamiento recomendado'
    )
    
    requiere_interconsulta = models.BooleanField(
        default=False,
        verbose_name='Requiere Interconsulta',
        help_text='¿Se requiere evaluación de otro especialista?'
    )
    
    especialidades_interconsulta = models.TextField(
        blank=True,
        verbose_name='Especialidades para Interconsulta',
        help_text='Ej: Neurología, Psiquiatría, etc.'
    )
    
    # =========================================================================
    # ESTADO Y SEGUIMIENTO
    # =========================================================================
    
    completada = models.BooleanField(
        default=False,
        verbose_name='Valoración Completada'
    )
    
    fecha_completada = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha y Hora de Completación'
    )
    
    # =========================================================================
    # ARCHIVOS ADJUNTOS
    # =========================================================================
    
    archivos_adjuntos = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Archivos Adjuntos',
        help_text='URLs de documentos, imágenes, videos de la valoración'
    )
    
    # =========================================================================
    # METADATA
    # =========================================================================
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    # =========================================================================
    # META
    # =========================================================================
    
    class Meta:
        verbose_name = 'Valoración Inicial'
        verbose_name_plural = 'Valoraciones Iniciales'
        ordering = ['-fecha_valoracion']
        indexes = [
            models.Index(fields=['paciente']),
            models.Index(fields=['fecha_valoracion']),
            models.Index(fields=['profesional']),
            models.Index(fields=['completada']),
        ]
    
    def __str__(self):
        return f"Valoración {self.paciente.nombre_completo} - {self.fecha_valoracion}"
    
    # =========================================================================
    # MÉTODOS
    # =========================================================================
    
    def save(self, *args, **kwargs):
        """Override save para generar código y actualizar estado del paciente."""
        
        # Generar código si no existe
        if not self.codigo_valoracion:
            from django.utils import timezone
            import random
            fecha_str = timezone.now().strftime('%Y%m%d')
            random_suffix = str(random.randint(1000, 9999))
            self.codigo_valoracion = f"VAL-{fecha_str}-{random_suffix}"
            
            # Verificar unicidad
            while ValoracionInicial.objects.filter(codigo_valoracion=self.codigo_valoracion).exists():
                random_suffix = str(random.randint(1000, 9999))
                self.codigo_valoracion = f"VAL-{fecha_str}-{random_suffix}"
        
        # Si se marca como completada
        if self.completada and not self.fecha_completada:
            self.fecha_completada = timezone.now()
            
            # Cambiar estado del paciente a PENDIENTE_ASIGNACION
            self.paciente.estado = Paciente.Estado.PENDIENTE_ASIGNACION
            self.paciente.save(update_fields=['estado'])
        
        super().save(*args, **kwargs)
    
    @property
    def duracion_valoracion(self):
        """Calcula la duración de la valoración en minutos."""
        if self.hora_inicio and self.hora_fin:
            from datetime import datetime, timedelta
            inicio = datetime.combine(self.fecha_valoracion, self.hora_inicio)
            fin = datetime.combine(self.fecha_valoracion, self.hora_fin)
            duracion = (fin - inicio).total_seconds() / 60
            return int(duracion)
        return None
    
    @property
    def cantidad_problemas(self):
        """Retorna la cantidad de problemas detectados."""
        return len(self.problemas_detectados) if self.problemas_detectados else 0
    
    @property
    def areas_afectadas(self):
        """Retorna lista de áreas afectadas (tipos de problemas únicos)."""
        if not self.problemas_detectados:
            return []
        return list(set([p.get('tipo') for p in self.problemas_detectados if 'tipo' in p]))
    
    def agregar_problema(self, tipo, descripcion, severidad='MODERADA', observaciones=''):
        """Método helper para agregar un problema detectado."""
        if not self.problemas_detectados:
            self.problemas_detectados = []
        
        problema = {
            'tipo': tipo,
            'descripcion': descripcion,
            'severidad': severidad,
            'observaciones': observaciones
        }
        self.problemas_detectados.append(problema)
        self.save(update_fields=['problemas_detectados'])
    
    def tiene_problema_tipo(self, tipo):
        """Verifica si el paciente tiene algún problema del tipo especificado."""
        if not self.problemas_detectados:
            return False
        return any(p.get('tipo') == tipo for p in self.problemas_detectados)


# ============================================================================
# FIN DEL MODELO ValoracionInicial
# ============================================================================
