"""
Modelo Paciente CORREGIDO - Auto-generación de Historia Clínica
Reemplaza el modelo Paciente en apps/procedimientos/models.py
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
    
    # ✅ MODIFICADO: Ahora es opcional y se auto-genera
    numero_historia_clinica = models.CharField(
        max_length=50,
        unique=True,
        blank=True,  # ✅ Ahora es opcional en formularios
        editable=True,  # Permite edición manual si es necesario
        verbose_name='Número de Historia Clínica',
        help_text='Se genera automáticamente si no se especifica (HC-{documento}-{año})'
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
        
        # Guardar normalmente
        super().save(*args, **kwargs)
    
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
