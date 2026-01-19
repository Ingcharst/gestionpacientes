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
from django.conf import settings
from apps.terapias.models import Terapia
from apps.grupos.models import GrupoTerapeutico
from apps.usuarios.models import Usuario


class CodigoCIE10(models.Model):
    """Catálogo de códigos CIE-10 (Clasificación Internacional de Enfermedades)"""
    
    codigo = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        verbose_name='Código CIE-10'
    )

    nombre = models.CharField(
        max_length=200,
        blank=True,
        help_text='Nombre descriptivo'
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


class Paciente(models.Model):
    """
    Modelo para pacientes del centro TEA.
    Historia clínica se genera automáticamente: HC-{documento}-{año}
    """
    
    class TipoDocumento(models.TextChoices):
        CC = 'CC', _('Cédula de Ciudadanía')
        TI = 'TI', _('Tarjeta de Identidad')
        RC = 'RC', _('Registro Civil')
        CE = 'CE', _('Cédula de Extranjería')
        PASAPORTE = 'PASAPORTE', _('Pasaporte')
    
    class Estado(models.TextChoices):
        ACTIVO = 'ACTIVO', _('Activo')
        ADMITIDO = 'ADMITIDO', _('Admitido - Sin Valorar')
        PENDIENTE_VALORACION = 'PENDIENTE_VALORACION', _('Pendiente Valoración')
        PENDIENTE_ASIGNACION = 'PENDIENTE_ASIGNACION', _('Pendiente Asignación Terapias')
        INACTIVO = 'INACTIVO', _('Inactivo')
        SUSPENDIDO = 'SUSPENDIDO', _('Suspendido')
        DADO_ALTA = 'DADO_ALTA', _('Dado de Alta')
    
    class Genero(models.TextChoices):
        MASCULINO = 'M', _('Masculino')
        FEMENINO = 'F', _('Femenino')
        OTRO = 'O', _('Otro')

    class EstadoAsignacion(models.TextChoices):
        SIN_ASIGNAR = 'SIN_ASIGNAR', _('Sin Asignar')
        ASIGNADO = 'ASIGNADO', _('Asignado')
        EN_ESPERA = 'EN_ESPERA', _('En Espera')

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

    edad_actual = models.FloatField(
        verbose_name='Edad',
        validators=[
            MinValueValidator(0),
            MaxValueValidator(20)
        ],
        null=True,
        blank=True,
        editable=False,  # No se puede editar manualmente
        help_text='Edad calculada automáticamente a partir de la fecha de nacimiento'
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

    codigo_enfermedad = models.ForeignKey(
        CodigoCIE10,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pacientes',
        verbose_name='Código CIE-10'
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
    
    # CAMBIO 1: Número de admisión en lugar de HC automática
    numero_admision = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Número de Admisión',
        help_text='Número de admisión del paciente (manual)',
        null=True,
        blank=True
    )
    
    # ✅ MODIFICADO: Ahora es opcional y se auto-genera
    numero_historia_clinica = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,  # ✅ Ahora es opcional en formularios
        editable=True,  # Permite edición manual si es necesario
        verbose_name='Número de Historia Clínica',
        help_text='Se genera automáticamente si no se especifica (HC-{documento}-{año})'
    )
    
    # ✅ NUEVO: Firma digital del acudiente
    firma_acudiente = models.TextField(
        blank=True,
        verbose_name='Firma Digital Acudiente',
        help_text='Firma del acudiente en formato base64'
    )

    fecha_firma_acudiente = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha y Hora de Firma'
    )

    ip_firma = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP donde se firmó'
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
        max_length=30,
        choices=Estado.choices,
        default=Estado.ADMITIDO,
        verbose_name='Estado'
    )
    
    fecha_ingreso = models.DateField(
        default=timezone.now,
        blank=True,
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
    
    tiene_grupo_asignado = models.BooleanField(
        default=False
    )
    
    grupo_actual = models.ForeignKey(
        'grupos.GrupoTerapeutico', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
        
    estado_asignacion = models.CharField(
        max_length=20,
        choices=EstadoAsignacion.choices,
        default=EstadoAsignacion.SIN_ASIGNAR
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

    def calcular_edad(self):
        """Calcula la edad actual del paciente."""
        if not self.fecha_nacimiento:
            return None
        today = timezone.now().date()
        age = today.year - self.fecha_nacimiento.year
        
        cumplio_este_año = (today.month, today.day) >= (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        
        if not cumplio_este_año:
            age -= 1
        
        if age >= 2:
            return age
        else:
            age = (today.year - self.fecha_nacimiento.year) * 12 + (today.month - self.fecha_nacimiento.month)
            if today.day < self.fecha_nacimiento.day:
                age -= 1
            return round(age / 12, 2)
        

    # ✅ NUEVO MÉTODO: Genera número de historia clínica único
    def generar_numero_historia_clinica(self):
        """
        Genera número de historia clínica automáticamente.
        Formato: HC-{NUMERO_DOCUMENTO}-{AÑO}
        Si existe duplicado, agrega sufijo: HC-{NUMERO_DOCUMENTO}-{AÑO}-1
        """
        year = timezone.now().year
        base = f"HC-{self.numero_documento}-{year}"
        
        # Verificar si ya existe
        numero = base
        counter = 1
        
        # Excluir el propio registro si está actualizando
        queryset = Paciente.objects.filter(numero_historia_clinica=numero)
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)
        
        while queryset.exists():
            numero = f"{base}-{counter}"
            counter += 1
            queryset = Paciente.objects.filter(numero_historia_clinica=numero)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
        
        return numero

    # ✅ MÉTODO SAVE SOBRESCRITO: Auto-genera historia clínica si está vacía
    def save(self, *args, **kwargs):
        """
        Sobrescribe save para auto-generar número de historia clínica.
        Si el campo está vacío, lo genera automáticamente.
        """
        # Auto-generar historia clínica si está vacía
        if not self.numero_historia_clinica:
            self.numero_historia_clinica = self.generar_numero_historia_clinica()

        # Calcular y actualizar la edad automáticamente
        if not self.edad_actual:
            self.edad_actual = self.calcular_edad()

        # Guardar normalmente
        super().save(*args, **kwargs)
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del paciente."""
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def edad(self):
        return self.calcular_edad()
    
    @property
    def edad_meses(self):
        """Calcula la edad en meses (útil para niños pequeños)."""
        today = timezone.now().date()
        months = (today.year - self.fecha_nacimiento.year) * 12
        months += today.month - self.fecha_nacimiento.month
        return months

    @property
    def categoria_edad(self):
        """Devuelve la categoría de edad del paciente."""
        if not self.edad:
            return 'Sin fecha de nacimiento'
        
        if self.edad < 1:
            meses = self.edad_meses
            if meses < 1:
                return 'Menos de 1 mes'
            elif meses < 12:
                return f'{meses} meses'
            else:
                return '1 año'
        elif self.edad <= 3:
            return '1-3 años'
        elif self.edad <= 6:
            return '4-6 años'
        elif self.edad <= 12:
            return '7-12 años'
        elif self.edad <= 18:
            return '13-18 años'
        elif self.edad <= 30:
            return '19-30 años'
        elif self.edad <= 50:
            return '31-50 años'
        elif self.edad <= 70:
            return '51-70 años'
        else:
            return 'Más de 70 años'
    
    # ✅ NUEVO: Próximo cumpleaños
    @property
    def dias_hasta_cumpleanos(self):
        """Calcula cuántos días faltan para el próximo cumpleaños."""
        if not self.fecha_nacimiento:
            return None
        
        today = timezone.now().date()
        next_birthday = datetime.date(today.year, self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        
        if today > next_birthday:
            next_birthday = datetime.date(today.year + 1, self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        
        return (next_birthday - today).days

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
        """Override save para generar código y calcular duración automáticamente."""
        # Generar código si no existe
        if not self.codigo:
            from django.utils import timezone
            import random
            fecha_str = timezone.now().strftime('%Y%m%d')
            tipo_prefix = self.tipo[:3].upper() if self.tipo else 'PRO'
            random_suffix = str(random.randint(1000, 9999))
            self.codigo = f"{tipo_prefix}-{fecha_str}-{random_suffix}"
            
            # Verificar unicidad
            while Procedimiento.objects.filter(codigo=self.codigo).exists():
                random_suffix = str(random.randint(1000, 9999))
                self.codigo = f"{tipo_prefix}-{fecha_str}-{random_suffix}"
        
        # Calcular duración
        if self.hora_inicio and self.hora_fin:
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
        """Override save para generar número de sesión y calcular duración real."""
        # Generar número de sesión si no existe
        if not self.numero_sesion:
            from django.utils import timezone
            import random
            fecha_str = timezone.now().strftime('%Y%m%d')
            terapia_prefix = self.terapia.codigo[:3].upper() if self.terapia and hasattr(self.terapia, 'codigo') else 'SES'
            random_suffix = str(random.randint(1000, 9999))
            self.numero_sesion = f"{terapia_prefix}-{fecha_str}-{random_suffix}"
            
            # Verificar unicidad
            while SesionTerapeutica.objects.filter(numero_sesion=self.numero_sesion).exists():
                random_suffix = str(random.randint(1000, 9999))
                self.numero_sesion = f"{terapia_prefix}-{fecha_str}-{random_suffix}"
        
        # Calcular duración real
        if self.hora_inicio and self.hora_fin:
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
    """Registro de evolución y seguimiento de terapia del paciente"""
    
    class TipoSesion(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', 'Individual'
        GRUPAL = 'GRUPAL', 'Grupal'
        EVALUACION = 'EVALUACION', 'Evaluación'
        INTERCONSULTA = 'INTERCONSULTA', 'Interconsulta'
    
    class Desempeno(models.TextChoices):
        EXCELENTE = 'EXCELENTE', 'Excelente'
        BUENO = 'BUENO', 'Bueno'
        REGULAR = 'REGULAR', 'Regular'
        REQUIERE_APOYO = 'REQUIERE_APOYO', 'Requiere Apoyo'
        NO_PARTICIPO = 'NO_PARTICIPO', 'No Participó'
    
    # Relaciones
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='evoluciones_paciente',
        verbose_name='Paciente'
    )
    
    profesional = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='evoluciones_registradas',
        verbose_name='Profesional'
    )
    
    terapia = models.ForeignKey(
        Terapia,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='evoluciones_terapias',
        verbose_name='Terapia'
    )
    
    grupo = models.ForeignKey(
        GrupoTerapeutico,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evoluciones_grupo',
        verbose_name='Grupo Terapéutico'
    )
    
    # Información de la sesión
    fecha_sesion = models.DateField(
        default=timezone.now,
        verbose_name='Fecha de la Sesión'
    )
    
    hora_inicio = models.TimeField(
        null=True,
        blank=True,
        # default=timezone.now,
        verbose_name='Hora de Inicio'
    )
    
    hora_fin = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Hora de Fin'
    )
    
    tipo_sesion = models.CharField(
        max_length=20,
        choices=TipoSesion.choices,
        default=TipoSesion.GRUPAL,
        verbose_name='Tipo de Sesión'
    )
    
    numero_sesion = models.IntegerField(
        default=1,
        verbose_name='Número de Sesión',
        help_text='Sesión número X del total asignado'
    )
    
    asistio = models.BooleanField(
        default=True,
        verbose_name='Asistió a la Sesión'
    )
    
    # Contenido de la evolución
    objetivos_trabajados = models.TextField(
        blank=True,
        verbose_name='Objetivos Trabajados',
        help_text='Objetivos terapéuticos abordados en la sesión'
    )
    
    actividades_realizadas = models.TextField(
        blank=True,
        verbose_name='Actividades Realizadas',
        help_text='Descripción de actividades y ejercicios realizados'
    )
    
    desempeno = models.CharField(
        blank=True,
        max_length=20,
        choices=Desempeno.choices,
        verbose_name='Desempeño del Paciente'
    )
    
    logros_obtenidos = models.TextField(
        blank=True,
        verbose_name='Logros Obtenidos',
        help_text='Avances y logros observados en la sesión'
    )
    
    dificultades_observadas = models.TextField(
        blank=True,
        verbose_name='Dificultades Observadas',
        help_text='Dificultades o retos encontrados'
    )
    
    observaciones_conducta = models.TextField(
        blank=True,
        verbose_name='Observaciones de Conducta',
        help_text='Aspectos conductuales relevantes'
    )
    
    observaciones_generales = models.TextField(
        blank=True,
        verbose_name='Observaciones Generales'
    )
    
    recomendaciones = models.TextField(
        blank=True,
        verbose_name='Recomendaciones',
        help_text='Recomendaciones para próximas sesiones o para el hogar'
    )
    
    proximos_objetivos = models.TextField(
        blank=True,
        verbose_name='Próximos Objetivos',
        help_text='Objetivos para trabajar en próximas sesiones'
    )
    
    # Evaluación cuantitativa (opcional)
    nivel_atencion = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        verbose_name='Nivel de Atención (1-5)',
        help_text='1=Muy bajo, 5=Excelente'
    )
    
    nivel_participacion = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        verbose_name='Nivel de Participación (1-5)'
    )
    
    nivel_colaboracion = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        verbose_name='Nivel de Colaboración (1-5)'
    )
    
    nivel_comprension = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        verbose_name='Nivel de Comprensión (1-5)'
    )
    
    # Material de apoyo
    material_utilizado = models.TextField(
        blank=True,
        verbose_name='Material Utilizado',
        help_text='Material didáctico o recursos utilizados'
    )
    
    tarea_asignada = models.TextField(
        blank=True,
        verbose_name='Tarea Asignada',
        help_text='Tareas o ejercicios para realizar en casa'
    )
    
    # Metadatos
    fecha_registro = models.DateTimeField(
        default=timezone.now,
        # auto_now_add=True,
        verbose_name='Fecha de Registro'
    )
    
    ultima_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Modificación'
    )
    
    firmado = models.BooleanField(
        default=False,
        verbose_name='Evolución Firmada',
        help_text='Indica si la evolución ha sido finalizada y firmada'
    )
    
    class Meta:
        verbose_name = 'Evolución de Paciente'
        verbose_name_plural = 'Evoluciones de Pacientes'
        ordering = ['-fecha_sesion', '-hora_inicio']
        indexes = [
            models.Index(fields=['paciente', 'fecha_sesion']),
            models.Index(fields=['profesional', 'fecha_sesion']),
            models.Index(fields=['terapia', 'fecha_sesion']),
        ]
    
    def __str__(self):
        return f"Evolución {self.paciente.nombre_completo} - {self.fecha_sesion}"
    
    @property
    def duracion_sesion(self):
        """Calcula la duración de la sesión en minutos"""
        if self.hora_inicio and self.hora_fin:
            from datetime import datetime, timedelta
            inicio = datetime.combine(self.fecha_sesion, self.hora_inicio)
            fin = datetime.combine(self.fecha_sesion, self.hora_fin)
            duracion = fin - inicio
            return int(duracion.total_seconds() / 60)
        return 0
    
    @property
    def promedio_evaluacion(self):
        """Calcula el promedio de las evaluaciones cuantitativas"""
        evaluaciones = [
            self.nivel_atencion,
            self.nivel_participacion,
            self.nivel_colaboracion,
            self.nivel_comprension
        ]
        evaluaciones_validas = [e for e in evaluaciones if e is not None]
        if evaluaciones_validas:
            return round(sum(evaluaciones_validas) / len(evaluaciones_validas), 1)
        return None
    
    def save(self, *args, **kwargs):
        # Calcular número de sesión automáticamente
        if not self.pk:  # Solo en creación
            sesiones_anteriores = EvolucionPaciente.objects.filter(
                paciente=self.paciente,
                terapia=self.terapia
            ).count()
            self.numero_sesion = sesiones_anteriores + 1
        
        super().save(*args, **kwargs)


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
    
    diagnostico_profesional = models.TextField(
        verbose_name='Diagnóstico del Profesional',
        help_text='Impresión diagnóstica del profesional'
    )
    
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
    
    completada = models.BooleanField(
        default=False,
        verbose_name='Valoración Completada'
    )
    
    fecha_completada = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha y Hora de Completación'
    )
        
    archivos_adjuntos = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Archivos Adjuntos',
        help_text='URLs de documentos, imágenes, videos de la valoración'
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


class RegistroAsistencia(models.Model):
    """
    Registro de asistencia de pacientes a sesiones de terapia.
    Se genera una lista por cada sesión grupal.
    """
    
    class EstadoAsistencia(models.TextChoices):
        ASISTIO = 'ASISTIO', 'Asistió'
        FALTA = 'FALTA', 'Falta'
        JUSTIFICADA = 'JUSTIFICADA', 'Falta Justificada'
        TARDANZA = 'TARDANZA', 'Llegó Tarde'
    
    sesion_terapeutica = models.ForeignKey(
        SesionTerapeutica,
        on_delete=models.CASCADE,
        related_name='asistencias',
        verbose_name='Sesión Terapéutica'
    )
    
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name='asistencias',
        verbose_name='Paciente'
    )
    
    asignacion_grupo = models.ForeignKey(
        'grupos.AsignacionGrupo',
        on_delete=models.PROTECT,
        related_name='asistencias',
        verbose_name='Asignación al Grupo'
    )
    
    estado = models.CharField(
        max_length=20,
        choices=EstadoAsistencia.choices,
        default=EstadoAsistencia.ASISTIO,
        verbose_name='Estado de Asistencia'
    )
    
    hora_llegada = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Hora de Llegada'
    )
    
    minutos_retraso = models.PositiveIntegerField(
        default=0,
        verbose_name='Minutos de Retraso'
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    # Firma de asistencia (opcional)
    firma_asistencia = models.TextField(
        blank=True,
        verbose_name='Firma Digital',
        help_text='Firma del acudiente confirmando asistencia'
    )
    
    registrado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='asistencias_registradas',
        verbose_name='Registrado Por'
    )
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Registro de Asistencia'
        verbose_name_plural = 'Registros de Asistencia'
        unique_together = [['sesion_terapeutica', 'paciente']]
    
    def __str__(self):
        return f"{self.paciente.nombre_completo} - {self.sesion_terapeutica.fecha}"
    
    def save(self, *args, **kwargs):
        # Incrementar contador de terapias completadas si asistió
        if self.estado == self.EstadoAsistencia.ASISTIO and not self.pk:
            self.asignacion_grupo.terapias_completadas += 1
            self.asignacion_grupo.save(update_fields=['terapias_completadas'])
        super().save(*args, **kwargs)


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
            """
            Guardar valoración y actualizar estado del paciente.
            Cambia paciente a PENDIENTE_ASIGNACION al completar primera valoración.
            """
            # Detectar si cambió a COMPLETADA
            cambio_completada = False
            
            if self.pk:  # Si ya existe
                try:
                    anterior = ValoracionProfesional.objects.get(pk=self.pk)
                    cambio_completada = anterior.estado != 'COMPLETADA' and self.estado == 'COMPLETADA'
                except ValoracionProfesional.DoesNotExist:
                    cambio_completada = self.estado == 'COMPLETADA'
            else:  # Es nueva
                cambio_completada = self.estado == 'COMPLETADA'
            
            # Auto-copiar firma del terapeuta
            if not self.firma_terapeuta and self.terapeuta.firma:
                self.firma_terapeuta = self.terapeuta.firma
            
            # Guardar primero
            super().save(*args, **kwargs)
            
            # Cambiar estado del paciente si completó valoración
            if cambio_completada:
                from apps.grupos.models import AsignacionGrupo
                
                # Verificar si no tiene grupo activo
                tiene_grupo = AsignacionGrupo.objects.filter(
                    paciente=self.paciente,
                    estado='ACTIVA'
                ).exists()
                
                # Cambiar a PENDIENTE_ASIGNACION si no tiene grupo
                if not tiene_grupo and self.paciente.estado != 'ACTIVO':
                    self.paciente.estado = 'PENDIENTE_ASIGNACION'
                    self.paciente.save(update_fields=['estado'])


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
        related_name='admisiones_terapia'
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
        related_name='admisiones_terapia_creadas'
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
        related_name='Asistencias_grupo'
    )
    paciente = models.ForeignKey(
        'Paciente',
        on_delete=models.CASCADE,
        related_name='Asistencias_paciente'
    )
    admision = models.ForeignKey(
        AdmisionTerapia,
        on_delete=models.CASCADE,
        related_name='Admisiones_asistencias'
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
        related_name='asistencias_registradas_sesion'
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







