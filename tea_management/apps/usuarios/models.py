from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class Usuario(AbstractUser):
    """
    Modelo de Usuario personalizado que extiende AbstractUser.
    Incluye roles específicos para el centro de atención TEA.
    """
    
    class Rol(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrador')
        COORDINADOR = 'COORDINADOR', _('Coordinador')
        TERAPEUTA = 'TERAPEUTA', _('Terapeuta')
        RECEPCIONISTA = 'RECEPCIONISTA', _('Recepcionista')
        MEDICO = 'MEDICO', _('Médico')
        PSICOLOGO = 'PSICOLOGO', _('Psicólogo')
    
    class EstadoUsuario(models.TextChoices):
        ACTIVO = 'ACTIVO', _('Activo')
        INACTIVO = 'INACTIVO', _('Inactivo')
        SUSPENDIDO = 'SUSPENDIDO', _('Suspendido')

    TIPO_DOCUMENTO = [
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('TI', 'Tarjeta de Identidad'),
        ('PP', 'Pasaporte'),
        ('RC', 'Registro Civil'),
        ('NIT', 'NIT'),
    ]
    
    tipo_identificacion = models.CharField(
        max_length=3,
        choices=TIPO_DOCUMENTO,
        default='CC',
        verbose_name='Tipo de Identificación'
    )
    
    numero_identificacion = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de Identificación',
        help_text='Documento de identidad del usuario'
    )

    
    # Campos adicionales
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.TERAPEUTA,
        verbose_name='Rol',
        help_text='Rol del usuario en el sistema'
    )
    
    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Formato de teléfono inválido. Ej: +5212345678901"
            )
        ],
        verbose_name='Teléfono'
    )
    
    cedula_profesional = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Cédula Profesional',
        help_text='Cédula profesional para personal médico/terapéutico'
    )
    
    estado = models.CharField(
        max_length=15,
        choices=EstadoUsuario.choices,
        default=EstadoUsuario.ACTIVO,
        verbose_name='Estado'
    )
    
    foto_perfil = models.ImageField(
        upload_to='usuarios/fotos/',
        blank=True,
        null=True,
        verbose_name='Foto de Perfil'
    )
    
    fecha_contratacion = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Contratación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    notas = models.TextField(
        blank=True,
        verbose_name='Notas',
        help_text='Observaciones adicionales sobre el usuario'
    )

    firma = models.ImageField(
        upload_to='firmas/',
        null=True,
        blank=True,
        help_text='Firma digital del terapeuta'
    )

 
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['rol', 'estado']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def es_terapeuta(self):
        """Verifica si el usuario es terapeuta."""
        return self.rol in [self.Rol.TERAPEUTA, self.Rol.PSICOLOGO, self.Rol.MEDICO]
    
    @property
    def es_admin(self):
        """Verifica si el usuario es administrador."""
        return self.rol == self.Rol.ADMIN or self.is_superuser
    
    @property
    def puede_gestionar_terapias(self):
        """Verifica si el usuario puede gestionar terapias."""
        return self.rol in [self.Rol.ADMIN, self.Rol.COORDINADOR]


class Perfil(models.Model):
    """
    Modelo de perfil extendido para usuarios.
    Información adicional del perfil profesional.
    """
    
    class Especialidad(models.TextChoices):
        PSICOLOGIA = 'PSICOLOGIA', _('Psicología')
        LENGUAJE = 'LENGUAJE', _('Terapia del Lenguaje')
        OCUPACIONAL = 'OCUPACIONAL', _('Terapia Ocupacional')
        FISICA = 'FISICA', _('Terapia Física')
        PSIQUIATRIA = 'PSIQUIATRIA', _('Psiquiatría')
        NEUROLOGIA = 'NEUROLOGIA', _('Neurología')
        CONDUCTUAL = 'CONDUCTUAL', _('Análisis Conductual (ABA)')
        INTEGRACION_SENSORIAL = 'INTEGRACION_SENSORIAL', _('Integración Sensorial')
        MUSICA = 'MUSICA', _('Musicoterapia')
        ARTE = 'ARTE', _('Arte Terapia')
    
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuario'
    )
    
    especialidades = models.CharField(
        max_length=30,
        choices=Especialidad.choices,
        blank=True,
        verbose_name='Especialidad Principal'
    )
    
    especialidades_secundarias = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Especialidades Secundarias',
        help_text='Lista de especialidades adicionales'
    )
    
    universidad = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Universidad'
    )
    
    anios_experiencia = models.PositiveIntegerField(
        default=0,
        verbose_name='Años de Experiencia'
    )
    
    certificaciones = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Certificaciones',
        help_text='Lista de certificaciones y cursos especializados'
    )
    
    bio = models.TextField(
        blank=True,
        verbose_name='Biografía Profesional',
        help_text='Descripción de experiencia y enfoque terapéutico'
    )
    
    horario_atencion = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Horario de Atención',
        help_text='Horarios disponibles por día de la semana'
    )
    
    disponible = models.BooleanField(
        default=True,
        verbose_name='Disponible para Asignaciones'
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
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Perfil de {self.usuario.get_full_name()}"
    
    def agregar_especialidad(self, especialidad):
        """Agrega una especialidad secundaria."""
        if especialidad not in self.especialidades_secundarias:
            self.especialidades_secundarias.append(especialidad)
            self.save()
    
    def agregar_certificacion(self, nombre, institucion, fecha):
        """Agrega una certificación al perfil."""
        certificacion = {
            'nombre': nombre,
            'institucion': institucion,
            'fecha': fecha
        }
        self.certificaciones.append(certificacion)
        self.save()


class RegistroAcceso(models.Model):
    """
    Modelo para auditoría de accesos al sistema.
    """
    
    class TipoAcceso(models.TextChoices):
        LOGIN = 'LOGIN', _('Inicio de Sesión')
        LOGOUT = 'LOGOUT', _('Cierre de Sesión')
        INTENTO_FALLIDO = 'INTENTO_FALLIDO', _('Intento Fallido')
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='registros_acceso',
        verbose_name='Usuario'
    )
    
    tipo_acceso = models.CharField(
        max_length=20,
        choices=TipoAcceso.choices,
        verbose_name='Tipo de Acceso'
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name='Dirección IP'
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    
    fecha_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y Hora'
    )
    
    exitoso = models.BooleanField(
        default=True,
        verbose_name='Acceso Exitoso'
    )
    
    notas = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    class Meta:
        verbose_name = 'Registro de Acceso'
        verbose_name_plural = 'Registros de Acceso'
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['usuario', '-fecha_hora']),
            models.Index(fields=['tipo_acceso', 'fecha_hora']),
        ]
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_acceso_display()} - {self.fecha_hora}"
