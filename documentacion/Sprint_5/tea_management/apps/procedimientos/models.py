"""
Modelos para gestión de procedimientos y sesiones terapéuticas.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta


class Paciente(models.Model):
    """
    Modelo para pacientes del centro TEA.
    """
    
    class TipoDocumento(models.TextChoices):
        CC = 'CC', _('Cédula de Ciudadanía')
        TI = 'TI', _('Tarjeta de Identidad')
        RC = 'RC', _('Registro Civil')
        CE = 'CE', _('Cédula de Extranjería')
        PASAPORTE = 'PASAPORTE', _('Pasaporte')
    
    class Estado(models.TextChoices):
        ACTIVO = 'ACTIVO', _('Activo')
        INACTIVO = 'INACTIVO', _('Inactivo')
        SUSPENDIDO = 'SUSPENDIDO', _('Suspendido')
        DADO_ALTA = 'DADO_ALTA', _('Dado de Alta')
    
    class Genero(models.TextChoices):
        MASCULINO = 'M', _('Masculino')
        FEMENINO = 'F', _('Femenino')
        OTRO = 'O', _('Otro')
    
    # Información Personal
    nombres = models.CharField(
        max_length=100,
        verbose_name='Nombres'
    )
    
    apellidos = models.CharField(
        max_length=100,
        verbose_name='Apellidos'
    )
    
    tipo_documento = models.CharField(
        max_length=20,
        choices=TipoDocumento.choices,
        default=TipoDocumento.RC,
        verbose_name='Tipo de Documento'
    )
    
    numero_documento = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de Documento'
    )
    
    fecha_nacimiento = models.DateField(
        verbose_name='Fecha de Nacimiento'
    )
    
    genero = models.CharField(
        max_length=1,
        choices=Genero.choices,
        verbose_name='Género'
    )
    
    foto = models.ImageField(
        upload_to='pacientes/fotos/',
        blank=True,
        null=True,
        verbose_name='Fotografía'
    )
    
    # Contacto
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono'
    )
    
    email = models.EmailField(
        blank=True,
        verbose_name='Email'
    )
    
    direccion = models.TextField(
        blank=True,
        verbose_name='Dirección'
    )
    
    ciudad = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Ciudad'
    )
    
    # Responsables
    nombre_responsable = models.CharField(
        max_length=200,
        verbose_name='Nombre del Responsable'
    )
    
    parentesco_responsable = models.CharField(
        max_length=50,
        verbose_name='Parentesco'
    )
    
    telefono_responsable = models.CharField(
        max_length=20,
        verbose_name='Teléfono del Responsable'
    )
    
    email_responsable = models.EmailField(
        blank=True,
        verbose_name='Email del Responsable'
    )
    
    # Información Médica
    diagnostico_principal = models.TextField(
        verbose_name='Diagnóstico Principal',
        help_text='Diagnóstico médico principal'
    )
    
    diagnosticos_secundarios = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Diagnósticos Secundarios',
        help_text='Lista de diagnósticos adicionales'
    )
    
    alergias = models.TextField(
        blank=True,
        verbose_name='Alergias',
        help_text='Alergias conocidas del paciente'
    )
    
    medicamentos = models.TextField(
        blank=True,
        verbose_name='Medicamentos',
        help_text='Medicamentos que toma actualmente'
    )
    
    eps = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='EPS'
    )
    
    numero_historia_clinica = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número de Historia Clínica',
        help_text='Número único de historia clínica'
    )
    
    # Información Adicional
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones Generales'
    )
    
    necesidades_especiales = models.TextField(
        blank=True,
        verbose_name='Necesidades Especiales',
        help_text='Necesidades especiales o consideraciones'
    )
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ACTIVO,
        verbose_name='Estado'
    )
    
    fecha_ingreso = models.DateField(
        default=timezone.now,
        verbose_name='Fecha de Ingreso'
    )
    
    fecha_alta = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Alta'
    )
    
    motivo_inactividad = models.TextField(
        blank=True,
        verbose_name='Motivo de Inactividad'
    )
    
    # Metadata
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    creado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='pacientes_creados',
        verbose_name='Creado Por'
    )
    
    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['apellidos', 'nombres']
        indexes = [
            models.Index(fields=['numero_documento']),
            models.Index(fields=['numero_historia_clinica']),
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_nacimiento']),
        ]
    
    def __str__(self):
        return f"{self.numero_historia_clinica} - {self.nombre_completo}"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del paciente."""
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def edad(self):
        """Calcula la edad actual del paciente."""
        today = timezone.now().date()
        age = today.year - self.fecha_nacimiento.year
        if today.month < self.fecha_nacimiento.month or \
           (today.month == self.fecha_nacimiento.month and today.day < self.fecha_nacimiento.day):
            age -= 1
        return age
    
    @property
    def edad_meses(self):
        """Calcula la edad en meses (útil para niños pequeños)."""
        today = timezone.now().date()
        months = (today.year - self.fecha_nacimiento.year) * 12
        months += today.month - self.fecha_nacimiento.month
        return months
    
    @property
    def esta_activo(self):
        """Verifica si el paciente está activo."""
        return self.estado == self.Estado.ACTIVO
    
    @property
    def tiene_alergias(self):
        """Verifica si tiene alergias registradas."""
        return bool(self.alergias.strip())
    
    @property
    def tiene_medicamentos(self):
        """Verifica si toma medicamentos."""
        return bool(self.medicamentos.strip())
    
    def agregar_diagnostico_secundario(self, diagnostico):
        """Agrega un diagnóstico secundario."""
        if diagnostico not in self.diagnosticos_secundarios:
            self.diagnosticos_secundarios.append(diagnostico)
            self.save(update_fields=['diagnosticos_secundarios'])
    
    def dar_alta(self, motivo=''):
        """Da de alta al paciente."""
        self.estado = self.Estado.DADO_ALTA
        self.fecha_alta = timezone.now().date()
        self.motivo_inactividad = motivo
        self.save(update_fields=['estado', 'fecha_alta', 'motivo_inactividad'])


class Procedimiento(models.Model):
    """
    Modelo para registro general de procedimientos realizados.
    Puede ser evaluación, consulta, terapia, etc.
    """
    
    class TipoProcedimiento(models.TextChoices):
        EVALUACION = 'EVALUACION', _('Evaluación')
        CONSULTA = 'CONSULTA', _('Consulta Médica')
        TERAPIA = 'TERAPIA', _('Sesión de Terapia')
        SEGUIMIENTO = 'SEGUIMIENTO', _('Seguimiento')
        VALORACION = 'VALORACION', _('Valoración')
        OTRO = 'OTRO', _('Otro')
    
    class Estado(models.TextChoices):
        PROGRAMADO = 'PROGRAMADO', _('Programado')
        EN_CURSO = 'EN_CURSO', _('En Curso')
        COMPLETADO = 'COMPLETADO', _('Completado')
        CANCELADO = 'CANCELADO', _('Cancelado')
        NO_ASISTIO = 'NO_ASISTIO', _('No Asistió')
    
    # Información Básica
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código',
        help_text='Código único del procedimiento'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TipoProcedimiento.choices,
        verbose_name='Tipo de Procedimiento'
    )
    
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name='procedimientos',
        verbose_name='Paciente'
    )
    
    profesional = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='procedimientos_realizados',
        verbose_name='Profesional',
        limit_choices_to={'rol__in': ['TERAPEUTA', 'MEDICO', 'PSICOLOGO']}
    )
    
    consultorio = models.ForeignKey(
        'consultorios.Consultorio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='procedimientos',
        verbose_name='Consultorio'
    )
    
    # Fecha y Hora
    fecha = models.DateField(
        verbose_name='Fecha'
    )
    
    hora_inicio = models.TimeField(
        verbose_name='Hora de Inicio'
    )
    
    hora_fin = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Hora de Fin'
    )
    
    duracion_minutos = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Duración (minutos)'
    )
    
    # Descripción
    motivo_consulta = models.TextField(
        verbose_name='Motivo de Consulta',
        help_text='Razón por la cual se realiza el procedimiento'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción detallada del procedimiento'
    )
    
    hallazgos = models.TextField(
        blank=True,
        verbose_name='Hallazgos',
        help_text='Hallazgos durante el procedimiento'
    )
    
    diagnostico = models.TextField(
        blank=True,
        verbose_name='Diagnóstico',
        help_text='Diagnóstico o impresión diagnóstica'
    )
    
    plan_tratamiento = models.TextField(
        blank=True,
        verbose_name='Plan de Tratamiento',
        help_text='Plan de tratamiento recomendado'
    )
    
    recomendaciones = models.TextField(
        blank=True,
        verbose_name='Recomendaciones'
    )
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PROGRAMADO,
        verbose_name='Estado'
    )
    
    motivo_cancelacion = models.TextField(
        blank=True,
        verbose_name='Motivo de Cancelación'
    )
    
    # Costos
    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Costo',
        help_text='Costo del procedimiento'
    )
    
    pagado = models.BooleanField(
        default=False,
        verbose_name='Pagado'
    )
    
    metodo_pago = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Método de Pago'
    )
    
    # Archivos Adjuntos
    archivos_adjuntos = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Archivos Adjuntos',
        help_text='URLs de archivos adjuntos (estudios, imágenes, etc.)'
    )
    
    # Metadata
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones Adicionales'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    creado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='procedimientos_creados',
        verbose_name='Creado Por'
    )
    
    class Meta:
        verbose_name = 'Procedimiento'
        verbose_name_plural = 'Procedimientos'
        ordering = ['-fecha', '-hora_inicio']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['paciente', 'fecha']),
            models.Index(fields=['profesional', 'fecha']),
            models.Index(fields=['estado']),
            models.Index(fields=['fecha']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.get_tipo_display()} - {self.paciente.nombre_completo}"
    
    def clean(self):
        """Validaciones personalizadas."""
        # Validar que hora_fin sea posterior a hora_inicio
        if self.hora_fin and self.hora_inicio:
            if self.hora_fin <= self.hora_inicio:
                raise ValidationError({
                    'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio.'
                })
        
        # Validar que el profesional tenga el rol adecuado
        if self.profesional:
            roles_validos = ['TERAPEUTA', 'MEDICO', 'PSICOLOGO', 'ADMIN']
            if self.profesional.rol not in roles_validos:
                raise ValidationError({
                    'profesional': 'El profesional debe ser terapeuta, médico o psicólogo.'
                })
    
    def save(self, *args, **kwargs):
        """Override save para calcular duración automáticamente."""
        if self.hora_inicio and self.hora_fin:
            # Calcular duración
            inicio = datetime.combine(self.fecha, self.hora_inicio)
            fin = datetime.combine(self.fecha, self.hora_fin)
            duracion = (fin - inicio).total_seconds() / 60
            self.duracion_minutos = int(duracion)
        
        super().save(*args, **kwargs)
    
    @property
    def duracion_formateada(self):
        """Retorna la duración en formato legible."""
        if not self.duracion_minutos:
            return "N/A"
        
        horas = self.duracion_minutos // 60
        minutos = self.duracion_minutos % 60
        
        if horas > 0 and minutos > 0:
            return f"{horas}h {minutos}min"
        elif horas > 0:
            return f"{horas}h"
        else:
            return f"{minutos}min"
    
    @property
    def esta_completado(self):
        """Verifica si el procedimiento está completado."""
        return self.estado == self.Estado.COMPLETADO
    
    @property
    def fecha_hora_inicio(self):
        """Retorna datetime combinado de fecha y hora de inicio."""
        return datetime.combine(self.fecha, self.hora_inicio)
    
    @property
    def costo_formateado(self):
        """Retorna el costo formateado."""
        return f"${self.costo:,.2f}"
    
    def completar(self):
        """Marca el procedimiento como completado."""
        self.estado = self.Estado.COMPLETADO
        if not self.hora_fin:
            self.hora_fin = timezone.now().time()
        self.save()
    
    def cancelar(self, motivo=''):
        """Cancela el procedimiento."""
        self.estado = self.Estado.CANCELADO
        self.motivo_cancelacion = motivo
        self.save(update_fields=['estado', 'motivo_cancelacion'])


class SesionTerapeutica(models.Model):
    """
    Modelo para sesiones terapéuticas específicas.
    Hereda y extiende el concepto de Procedimiento para terapias.
    """
    
    class Estado(models.TextChoices):
        PROGRAMADA = 'PROGRAMADA', _('Programada')
        EN_CURSO = 'EN_CURSO', _('En Curso')
        COMPLETADA = 'COMPLETADA', _('Completada')
        CANCELADA = 'CANCELADA', _('Cancelada')
        REPROGRAMADA = 'REPROGRAMADA', _('Reprogramada')
    
    class TipoAsistencia(models.TextChoices):
        ASISTIO = 'ASISTIO', _('Asistió')
        NO_ASISTIO = 'NO_ASISTIO', _('No Asistió')
        LLEGO_TARDE = 'LLEGO_TARDE', _('Llegó Tarde')
        SALIO_TEMPRANO = 'SALIO_TEMPRANO', _('Salió Temprano')
    
    # Relación con Procedimiento (opcional)
    procedimiento = models.OneToOneField(
        Procedimiento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sesion_terapeutica',
        verbose_name='Procedimiento Base'
    )
    
    # Información Básica
    numero_sesion = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número de Sesión',
        help_text='Número único de la sesión'
    )
    
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name='sesiones',
        verbose_name='Paciente'
    )
    
    terapeuta = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='sesiones_impartidas',
        verbose_name='Terapeuta',
        limit_choices_to={'rol__in': ['TERAPEUTA', 'MEDICO', 'PSICOLOGO']}
    )
    
    terapia = models.ForeignKey(
        'terapias.Terapia',
        on_delete=models.PROTECT,
        related_name='sesiones',
        verbose_name='Tipo de Terapia'
    )
    
    consultorio = models.ForeignKey(
        'consultorios.Consultorio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sesiones',
        verbose_name='Consultorio'
    )
    
    # Fecha y Hora
    fecha = models.DateField(
        verbose_name='Fecha de la Sesión'
    )
    
    hora_inicio = models.TimeField(
        verbose_name='Hora de Inicio'
    )
    
    hora_fin = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Hora de Fin'
    )
    
    duracion_programada_minutos = models.PositiveIntegerField(
        verbose_name='Duración Programada (minutos)'
    )
    
    duracion_real_minutos = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Duración Real (minutos)'
    )
    
    # Asistencia
    tipo_asistencia = models.CharField(
        max_length=20,
        choices=TipoAsistencia.choices,
        default=TipoAsistencia.ASISTIO,
        verbose_name='Tipo de Asistencia'
    )
    
    minutos_retraso = models.PositiveIntegerField(
        default=0,
        verbose_name='Minutos de Retraso'
    )
    
    asistio_acompanante = models.BooleanField(
        default=True,
        verbose_name='Asistió Acompañante'
    )
    
    nombre_acompanante = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nombre del Acompañante'
    )
    
    # Contenido de la Sesión
    objetivos_sesion = models.TextField(
        verbose_name='Objetivos de la Sesión',
        help_text='Objetivos específicos trabajados'
    )
    
    actividades_realizadas = models.TextField(
        verbose_name='Actividades Realizadas',
        help_text='Descripción de las actividades'
    )
    
    tecnicas_utilizadas = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Técnicas Utilizadas',
        help_text='Lista de técnicas terapéuticas aplicadas'
    )
    
    materiales_utilizados = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Materiales Utilizados',
        help_text='Lista de materiales usados en la sesión'
    )
    
    # Evaluación y Progreso
    desempeno_paciente = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True,
        blank=True,
        verbose_name='Desempeño del Paciente (1-10)',
        help_text='Calificación del desempeño'
    )
    
    nivel_atencion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True,
        blank=True,
        verbose_name='Nivel de Atención (1-10)'
    )
    
    nivel_participacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True,
        blank=True,
        verbose_name='Nivel de Participación (1-10)'
    )
    
    estado_animo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Estado de Ánimo',
        help_text='Estado anímico observado'
    )
    
    logros_sesion = models.TextField(
        blank=True,
        verbose_name='Logros de la Sesión',
        help_text='Logros alcanzados durante la sesión'
    )
    
    dificultades_presentadas = models.TextField(
        blank=True,
        verbose_name='Dificultades Presentadas',
        help_text='Dificultades encontradas'
    )
    
    # Notas del Terapeuta
    observaciones_terapeuta = models.TextField(
        blank=True,
        verbose_name='Observaciones del Terapeuta'
    )
    
    recomendaciones_proxima_sesion = models.TextField(
        blank=True,
        verbose_name='Recomendaciones para Próxima Sesión'
    )
    
    tareas_casa = models.TextField(
        blank=True,
        verbose_name='Tareas para Casa',
        help_text='Ejercicios o actividades para realizar en casa'
    )
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PROGRAMADA,
        verbose_name='Estado'
    )
    
    motivo_cancelacion = models.TextField(
        blank=True,
        verbose_name='Motivo de Cancelación/Reprogramación'
    )
    
    sesion_reprogramada = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sesion_original',
        verbose_name='Sesión Reprogramada'
    )
    
    # Costos
    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Costo de la Sesión'
    )
    
    pagado = models.BooleanField(
        default=False,
        verbose_name='Pagado'
    )
    
    # Archivos
    grabacion_url = models.URLField(
        blank=True,
        verbose_name='URL de Grabación',
        help_text='Enlace a grabación de la sesión (si aplica)'
    )
    
    evidencias_fotograficas = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Evidencias Fotográficas',
        help_text='URLs de fotos de la sesión'
    )
    
    # Metadata
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    creado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='sesiones_creadas',
        verbose_name='Creado Por'
    )
    
    class Meta:
        verbose_name = 'Sesión Terapéutica'
        verbose_name_plural = 'Sesiones Terapéuticas'
        ordering = ['-fecha', '-hora_inicio']
        indexes = [
            models.Index(fields=['numero_sesion']),
            models.Index(fields=['paciente', 'fecha']),
            models.Index(fields=['terapeuta', 'fecha']),
            models.Index(fields=['terapia']),
            models.Index(fields=['estado']),
            models.Index(fields=['fecha']),
        ]
    
    def __str__(self):
        return f"{self.numero_sesion} - {self.terapia.nombre} - {self.paciente.nombre_completo}"
    
    def clean(self):
        """Validaciones personalizadas."""
        # Validar que hora_fin sea posterior a hora_inicio
        if self.hora_fin and self.hora_inicio:
            if self.hora_fin <= self.hora_inicio:
                raise ValidationError({
                    'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio.'
                })
        
        # Validar que el terapeuta tenga el rol adecuado
        if self.terapeuta:
            roles_validos = ['TERAPEUTA', 'MEDICO', 'PSICOLOGO', 'ADMIN']
            if self.terapeuta.rol not in roles_validos:
                raise ValidationError({
                    'terapeuta': 'Debe ser un terapeuta, médico o psicólogo.'
                })
        
        # Validar calificaciones
        if self.desempeno_paciente and (self.desempeno_paciente < 1 or self.desempeno_paciente > 10):
            raise ValidationError({
                'desempeno_paciente': 'El desempeño debe estar entre 1 y 10.'
            })
    
    def save(self, *args, **kwargs):
        """Override save para calcular duración real."""
        if self.hora_inicio and self.hora_fin:
            # Calcular duración real
            inicio = datetime.combine(self.fecha, self.hora_inicio)
            fin = datetime.combine(self.fecha, self.hora_fin)
            duracion = (fin - inicio).total_seconds() / 60
            self.duracion_real_minutos = int(duracion)
        
        super().save(*args, **kwargs)
    
    @property
    def duracion_real_formateada(self):
        """Retorna la duración real en formato legible."""
        if not self.duracion_real_minutos:
            return "N/A"
        
        horas = self.duracion_real_minutos // 60
        minutos = self.duracion_real_minutos % 60
        
        if horas > 0 and minutos > 0:
            return f"{horas}h {minutos}min"
        elif horas > 0:
            return f"{horas}h"
        else:
            return f"{minutos}min"
    
    @property
    def duracion_programada_formateada(self):
        """Retorna la duración programada en formato legible."""
        horas = self.duracion_programada_minutos // 60
        minutos = self.duracion_programada_minutos % 60
        
        if horas > 0 and minutos > 0:
            return f"{horas}h {minutos}min"
        elif horas > 0:
            return f"{horas}h"
        else:
            return f"{minutos}min"
    
    @property
    def esta_completada(self):
        """Verifica si la sesión está completada."""
        return self.estado == self.Estado.COMPLETADA
    
    @property
    def asistio(self):
        """Verifica si el paciente asistió."""
        return self.tipo_asistencia in [self.TipoAsistencia.ASISTIO, 
                                        self.TipoAsistencia.LLEGO_TARDE, 
                                        self.TipoAsistencia.SALIO_TEMPRANO]
    
    @property
    def fecha_hora_inicio(self):
        """Retorna datetime combinado."""
        return datetime.combine(self.fecha, self.hora_inicio)
    
    @property
    def costo_formateado(self):
        """Retorna el costo formateado."""
        return f"${self.costo:,.2f}"
    
    @property
    def promedio_desempeno(self):
        """Calcula promedio de métricas de desempeño."""
        metricas = [m for m in [self.desempeno_paciente, self.nivel_atencion, self.nivel_participacion] if m]
        if not metricas:
            return None
        return sum(metricas) / len(metricas)
    
    def completar(self, observaciones=''):
        """Marca la sesión como completada."""
        self.estado = self.Estado.COMPLETADA
        if not self.hora_fin:
            self.hora_fin = timezone.now().time()
        if observaciones:
            self.observaciones_terapeuta = observaciones
        self.save()
    
    def cancelar(self, motivo=''):
        """Cancela la sesión."""
        self.estado = self.Estado.CANCELADA
        self.motivo_cancelacion = motivo
        self.save(update_fields=['estado', 'motivo_cancelacion'])
    
    def reprogramar(self, nueva_fecha, nueva_hora, motivo=''):
        """Reprograma la sesión creando una nueva."""
        self.estado = self.Estado.REPROGRAMADA
        self.motivo_cancelacion = motivo
        self.save()
        
        # Crear nueva sesión
        nueva_sesion = SesionTerapeutica.objects.create(
            paciente=self.paciente,
            terapeuta=self.terapeuta,
            terapia=self.terapia,
            consultorio=self.consultorio,
            fecha=nueva_fecha,
            hora_inicio=nueva_hora,
            duracion_programada_minutos=self.duracion_programada_minutos,
            objetivos_sesion=self.objetivos_sesion,
            costo=self.costo,
            creado_por=self.creado_por
        )
        
        self.sesion_reprogramada = nueva_sesion
        self.save(update_fields=['sesion_reprogramada'])
        
        return nueva_sesion
    
    def agregar_tecnica(self, tecnica):
        """Agrega una técnica utilizada."""
        if tecnica not in self.tecnicas_utilizadas:
            self.tecnicas_utilizadas.append(tecnica)
            self.save(update_fields=['tecnicas_utilizadas'])
    
    def agregar_material(self, material):
        """Agrega un material utilizado."""
        if material not in self.materiales_utilizados:
            self.materiales_utilizados.append(material)
            self.save(update_fields=['materiales_utilizados'])


class ObjetivoTerapeutico(models.Model):
    """
    Modelo para objetivos terapéuticos a largo plazo del paciente.
    """
    
    class Estado(models.TextChoices):
        EN_PROCESO = 'EN_PROCESO', _('En Proceso')
        LOGRADO = 'LOGRADO', _('Logrado')
        PAUSADO = 'PAUSADO', _('Pausado')
        ABANDONADO = 'ABANDONADO', _('Abandonado')
    
    class Prioridad(models.TextChoices):
        ALTA = 'ALTA', _('Alta')
        MEDIA = 'MEDIA', _('Media')
        BAJA = 'BAJA', _('Baja')
    
    # Información Básica
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='objetivos_terapeuticos',
        verbose_name='Paciente'
    )
    
    terapia = models.ForeignKey(
        'terapias.Terapia',
        on_delete=models.PROTECT,
        related_name='objetivos_terapeuticos',
        verbose_name='Terapia Asociada'
    )
    
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título del Objetivo'
    )
    
    descripcion = models.TextField(
        verbose_name='Descripción Detallada'
    )
    
    # Clasificación
    area_desarrollo = models.CharField(
        max_length=100,
        verbose_name='Área de Desarrollo',
        help_text='Área que se busca desarrollar'
    )
    
    prioridad = models.CharField(
        max_length=10,
        choices=Prioridad.choices,
        default=Prioridad.MEDIA,
        verbose_name='Prioridad'
    )
    
    # Plazos
    fecha_inicio = models.DateField(
        verbose_name='Fecha de Inicio'
    )
    
    fecha_limite = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Límite Estimada'
    )
    
    fecha_logro = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Logro'
    )
    
    # Estado y Progreso
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.EN_PROCESO,
        verbose_name='Estado'
    )
    
    porcentaje_avance = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Porcentaje de Avance'
    )
    
    # Medición
    criterios_exito = models.TextField(
        verbose_name='Criterios de Éxito',
        help_text='Cómo se medirá el logro del objetivo'
    )
    
    metrica_actual = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Métrica Actual'
    )
    
    metrica_objetivo = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Métrica Objetivo'
    )
    
    # Estrategias
    estrategias = models.TextField(
        blank=True,
        verbose_name='Estrategias a Utilizar',
        help_text='Estrategias para alcanzar el objetivo'
    )
    
    # Observaciones
    notas = models.TextField(
        blank=True,
        verbose_name='Notas Adicionales'
    )
    
    # Metadata
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    creado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='objetivos_creados',
        verbose_name='Creado Por'
    )
    
    class Meta:
        verbose_name = 'Objetivo Terapéutico'
        verbose_name_plural = 'Objetivos Terapéuticos'
        ordering = ['-prioridad', '-fecha_inicio']
        indexes = [
            models.Index(fields=['paciente', 'estado']),
            models.Index(fields=['terapia']),
            models.Index(fields=['fecha_inicio']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.paciente.nombre_completo}"
    
    @property
    def esta_logrado(self):
        """Verifica si el objetivo está logrado."""
        return self.estado == self.Estado.LOGRADO
    
    @property
    def dias_transcurridos(self):
        """Calcula días desde el inicio."""
        return (timezone.now().date() - self.fecha_inicio).days
    
    @property
    def dias_restantes(self):
        """Calcula días restantes hasta la fecha límite."""
        if not self.fecha_limite:
            return None
        return (self.fecha_limite - timezone.now().date()).days
    
    def marcar_logrado(self):
        """Marca el objetivo como logrado."""
        self.estado = self.Estado.LOGRADO
        self.fecha_logro = timezone.now().date()
        self.porcentaje_avance = 100
        self.save(update_fields=['estado', 'fecha_logro', 'porcentaje_avance'])
    
    def actualizar_avance(self, porcentaje):
        """Actualiza el porcentaje de avance."""
        self.porcentaje_avance = max(0, min(100, porcentaje))
        if self.porcentaje_avance == 100 and self.estado != self.Estado.LOGRADO:
            self.marcar_logrado()
        else:
            self.save(update_fields=['porcentaje_avance'])


class EvolucionPaciente(models.Model):
    """
    Modelo para registro de evolución del paciente.
    Registro cronológico de observaciones y cambios.
    """
    
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='evoluciones',
        verbose_name='Paciente'
    )
    
    sesion = models.ForeignKey(
        SesionTerapeutica,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evoluciones',
        verbose_name='Sesión Relacionada'
    )
    
    fecha = models.DateField(
        default=timezone.now,
        verbose_name='Fecha'
    )
    
    profesional = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='evoluciones_registradas',
        verbose_name='Profesional'
    )
    
    tipo_nota = models.CharField(
        max_length=50,
        verbose_name='Tipo de Nota',
        help_text='Ej: Evolución, Interconsulta, Resumen, etc.'
    )
    
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    
    contenido = models.TextField(
        verbose_name='Contenido',
        help_text='Descripción detallada de la evolución'
    )
    
    observaciones_conducta = models.TextField(
        blank=True,
        verbose_name='Observaciones de Conducta'
    )
    
    observaciones_comunicacion = models.TextField(
        blank=True,
        verbose_name='Observaciones de Comunicación'
    )
    
    observaciones_socializacion = models.TextField(
        blank=True,
        verbose_name='Observaciones de Socialización'
    )
    
    cambios_medicacion = models.TextField(
        blank=True,
        verbose_name='Cambios en Medicación'
    )
    
    archivos_adjuntos = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Archivos Adjuntos'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    class Meta:
        verbose_name = 'Evolución del Paciente'
        verbose_name_plural = 'Evoluciones de Pacientes'
        ordering = ['-fecha', '-fecha_creacion']
        indexes = [
            models.Index(fields=['paciente', 'fecha']),
            models.Index(fields=['profesional']),
        ]
    
    def __str__(self):
        return f"{self.fecha} - {self.titulo} - {self.paciente.nombre_completo}"