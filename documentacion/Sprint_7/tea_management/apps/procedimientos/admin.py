"""
Configuración del admin de Django para procedimientos.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from apps.procedimientos.models import (
    Paciente, Procedimiento, SesionTerapeutica,
    ObjetivoTerapeutico, EvolucionPaciente
)


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    """Admin personalizado para Paciente."""
    
    list_display = [
        'numero_historia_clinica', 'nombre_completo_link', 'numero_documento',
        'edad_display', 'estado_badge', 'diagnostico_principal',
        'telefono', 'fecha_ingreso'
    ]
    
    list_filter = ['estado', 'genero', 'tipo_documento', 'fecha_ingreso']
    
    search_fields = [
        'nombres', 'apellidos', 'numero_documento', 'numero_historia_clinica',
        'diagnostico_principal', 'nombre_responsable'
    ]
    
    readonly_fields = [
        'numero_historia_clinica', 'edad', 'edad_meses',
        'nombre_completo', 'esta_activo', 'tiene_alergias', 'tiene_medicamentos',
        'fecha_creacion', 'fecha_actualizacion'
    ]
    
    fieldsets = (
        ('Información Personal', {
            'fields': (
                'numero_historia_clinica', 'nombres', 'apellidos', 'nombre_completo',
                'tipo_documento', 'numero_documento', 'fecha_nacimiento',
                'edad', 'edad_meses', 'genero', 'foto'
            )
        }),
        ('Contacto', {
            'fields': (
                'telefono', 'email', 'direccion', 'ciudad'
            )
        }),
        ('Responsable', {
            'fields': (
                'nombre_responsable', 'parentesco_responsable',
                'telefono_responsable', 'email_responsable'
            )
        }),
        ('Información Médica', {
            'fields': (
                'diagnostico_principal', 'diagnosticos_secundarios',
                'alergias', 'tiene_alergias', 'medicamentos', 'tiene_medicamentos',
                'eps'
            )
        }),
        ('Estado', {
            'fields': (
                'estado', 'esta_activo', 'fecha_ingreso', 'fecha_alta',
                'motivo_inactividad', 'observaciones', 'necesidades_especiales'
            )
        }),
        ('Metadata', {
            'fields': ('creado_por', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'fecha_ingreso'
    ordering = ['-fecha_ingreso']
    
    def nombre_completo_link(self, obj):
        """Link al detalle del paciente."""
        return format_html(
            '<a href="{}">{}</a>',
            f'/admin/procedimientos/paciente/{obj.pk}/change/',
            obj.nombre_completo
        )
    nombre_completo_link.short_description = 'Nombre Completo'
    
    def edad_display(self, obj):
        """Muestra edad en años."""
        return f"{obj.edad} años"
    edad_display.short_description = 'Edad'
    
    def estado_badge(self, obj):
        """Badge de color para el estado."""
        colors = {
            'ACTIVO': '#28a745',
            'INACTIVO': '#6c757d',
            'SUSPENDIDO': '#ffc107',
            'DADO_ALTA': '#17a2b8',
        }
        color = colors.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    actions = ['activar_pacientes', 'inactivar_pacientes']
    
    def activar_pacientes(self, request, queryset):
        """Activar pacientes seleccionados."""
        count = queryset.update(estado='ACTIVO')
        self.message_user(request, f'{count} paciente(s) activado(s).')
    activar_pacientes.short_description = 'Activar pacientes seleccionados'
    
    def inactivar_pacientes(self, request, queryset):
        """Inactivar pacientes seleccionados."""
        count = queryset.update(estado='INACTIVO')
        self.message_user(request, f'{count} paciente(s) inactivado(s).')
    inactivar_pacientes.short_description = 'Inactivar pacientes seleccionados'


@admin.register(Procedimiento)
class ProcedimientoAdmin(admin.ModelAdmin):
    """Admin personalizado para Procedimiento."""
    
    list_display = [
        'codigo', 'tipo_display', 'paciente_link', 'profesional_link',
        'fecha', 'hora_inicio', 'duracion_display', 'estado_badge',
        'costo_display', 'pagado_badge'
    ]
    
    list_filter = ['tipo', 'estado', 'fecha', 'pagado', 'profesional']
    
    search_fields = [
        'codigo', 'paciente__nombres', 'paciente__apellidos',
        'profesional__first_name', 'profesional__last_name', 'motivo_consulta'
    ]
    
    readonly_fields = [
        'duracion_minutos', 'duracion_formateada', 'esta_completado',
        'fecha_hora_inicio', 'costo_formateado',
        'fecha_creacion', 'fecha_actualizacion'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'codigo', 'tipo', 'paciente', 'profesional', 'consultorio'
            )
        }),
        ('Fecha y Hora', {
            'fields': (
                'fecha', 'hora_inicio', 'hora_fin', 'duracion_minutos',
                'duracion_formateada', 'fecha_hora_inicio'
            )
        }),
        ('Descripción', {
            'fields': (
                'motivo_consulta', 'descripcion', 'hallazgos',
                'diagnostico', 'plan_tratamiento', 'recomendaciones'
            )
        }),
        ('Estado', {
            'fields': (
                'estado', 'esta_completado', 'motivo_cancelacion'
            )
        }),
        ('Costos', {
            'fields': (
                'costo', 'costo_formateado', 'pagado', 'metodo_pago'
            )
        }),
        ('Archivos y Observaciones', {
            'fields': ('archivos_adjuntos', 'observaciones'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('creado_por', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'fecha'
    ordering = ['-fecha', '-hora_inicio']
    
    def tipo_display(self, obj):
        """Muestra el tipo de procedimiento."""
        return obj.get_tipo_display()
    tipo_display.short_description = 'Tipo'
    
    def paciente_link(self, obj):
        """Link al paciente."""
        return format_html(
            '<a href="{}">{}</a>',
            f'/admin/procedimientos/paciente/{obj.paciente.pk}/change/',
            obj.paciente.nombre_completo
        )
    paciente_link.short_description = 'Paciente'
    
    def profesional_link(self, obj):
        """Link al profesional."""
        return format_html(
            '<a href="{}">{}</a>',
            f'/admin/usuarios/usuario/{obj.profesional.pk}/change/',
            obj.profesional.get_full_name()
        )
    profesional_link.short_description = 'Profesional'
    
    def duracion_display(self, obj):
        """Muestra la duración."""
        return obj.duracion_formateada
    duracion_display.short_description = 'Duración'
    
    def estado_badge(self, obj):
        """Badge de color para el estado."""
        colors = {
            'PROGRAMADO': '#007bff',
            'EN_CURSO': '#ffc107',
            'COMPLETADO': '#28a745',
            'CANCELADO': '#dc3545',
            'NO_ASISTIO': '#6c757d',
        }
        color = colors.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def costo_display(self, obj):
        """Muestra el costo formateado."""
        return obj.costo_formateado
    costo_display.short_description = 'Costo'
    
    def pagado_badge(self, obj):
        """Badge para estado de pago."""
        if obj.pagado:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px;">✓ Pagado</span>'
            )
        return format_html(
            '<span style="background-color: #ffc107; color: black; padding: 3px 10px; '
            'border-radius: 3px;">⏳ Pendiente</span>'
        )
    pagado_badge.short_description = 'Pago'
    
    actions = ['marcar_completado', 'marcar_pagado']
    
    def marcar_completado(self, request, queryset):
        """Marcar como completado."""
        for procedimiento in queryset:
            procedimiento.completar()
        self.message_user(request, f'{queryset.count()} procedimiento(s) completado(s).')
    marcar_completado.short_description = 'Marcar como completado'
    
    def marcar_pagado(self, request, queryset):
        """Marcar como pagado."""
        count = queryset.update(pagado=True)
        self.message_user(request, f'{count} procedimiento(s) marcado(s) como pagado(s).')
    marcar_pagado.short_description = 'Marcar como pagado'


@admin.register(SesionTerapeutica)
class SesionTerapeuticaAdmin(admin.ModelAdmin):
    """Admin personalizado para Sesión Terapéutica."""
    
    list_display = [
        'numero_sesion', 'paciente_link', 'terapeuta_link', 'terapia_display',
        'fecha', 'hora_inicio', 'duracion_display', 'estado_badge',
        'asistencia_badge', 'desempeno_display', 'pagado_badge'
    ]
    
    list_filter = [
        'estado', 'tipo_asistencia', 'fecha', 'pagado',
        'terapeuta', 'terapia'
    ]
    
    search_fields = [
        'numero_sesion', 'paciente__nombres', 'paciente__apellidos',
        'terapeuta__first_name', 'terapeuta__last_name', 'terapia__nombre'
    ]
    
    readonly_fields = [
        'duracion_real_minutos', 'duracion_programada_formateada',
        'duracion_real_formateada', 'esta_completada', 'asistio',
        'fecha_hora_inicio', 'costo_formateado', 'promedio_desempeno',
        'fecha_creacion', 'fecha_actualizacion'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'numero_sesion', 'paciente', 'terapeuta', 'terapia',
                'consultorio', 'procedimiento'
            )
        }),
        ('Fecha y Hora', {
            'fields': (
                'fecha', 'hora_inicio', 'hora_fin',
                'duracion_programada_minutos', 'duracion_programada_formateada',
                'duracion_real_minutos', 'duracion_real_formateada',
                'fecha_hora_inicio'
            )
        }),
        ('Asistencia', {
            'fields': (
                'tipo_asistencia', 'asistio', 'minutos_retraso',
                'asistio_acompanante', 'nombre_acompanante'
            )
        }),
        ('Contenido de la Sesión', {
            'fields': (
                'objetivos_sesion', 'actividades_realizadas',
                'tecnicas_utilizadas', 'materiales_utilizados'
            )
        }),
        ('Evaluación', {
            'fields': (
                'desempeno_paciente', 'nivel_atencion', 'nivel_participacion',
                'promedio_desempeno', 'estado_animo',
                'logros_sesion', 'dificultades_presentadas'
            )
        }),
        ('Notas del Terapeuta', {
            'fields': (
                'observaciones_terapeuta', 'recomendaciones_proxima_sesion',
                'tareas_casa'
            )
        }),
        ('Estado', {
            'fields': (
                'estado', 'esta_completada', 'motivo_cancelacion',
                'sesion_reprogramada'
            )
        }),
        ('Costos', {
            'fields': (
                'costo', 'costo_formateado', 'pagado'
            )
        }),
        ('Archivos', {
            'fields': ('grabacion_url', 'evidencias_fotograficas'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('creado_por', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'fecha'
    ordering = ['-fecha', '-hora_inicio']
    
    def paciente_link(self, obj):
        """Link al paciente."""
        return format_html(
            '<a href="{}">{}</a>',
            f'/admin/procedimientos/paciente/{obj.paciente.pk}/change/',
            obj.paciente.nombre_completo
        )
    paciente_link.short_description = 'Paciente'
    
    def terapeuta_link(self, obj):
        """Link al terapeuta."""
        return format_html(
            '<a href="{}">{}</a>',
            f'/admin/usuarios/usuario/{obj.terapeuta.pk}/change/',
            obj.terapeuta.get_full_name()
        )
    terapeuta_link.short_description = 'Terapeuta'
    
    def terapia_display(self, obj):
        """Muestra la terapia."""
        return obj.terapia.nombre
    terapia_display.short_description = 'Terapia'
    
    def duracion_display(self, obj):
        """Muestra la duración."""
        if obj.duracion_real_minutos:
            return obj.duracion_real_formateada
        return obj.duracion_programada_formateada
    duracion_display.short_description = 'Duración'
    
    def estado_badge(self, obj):
        """Badge de color para el estado."""
        colors = {
            'PROGRAMADA': '#007bff',
            'EN_CURSO': '#ffc107',
            'COMPLETADA': '#28a745',
            'CANCELADA': '#dc3545',
            'REPROGRAMADA': '#6c757d',
        }
        color = colors.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def asistencia_badge(self, obj):
        """Badge para tipo de asistencia."""
        colors = {
            'ASISTIO': '#28a745',
            'NO_ASISTIO': '#dc3545',
            'LLEGO_TARDE': '#ffc107',
            'SALIO_TEMPRANO': '#fd7e14',
        }
        color = colors.get(obj.tipo_asistencia, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color,
            obj.get_tipo_asistencia_display()
        )
    asistencia_badge.short_description = 'Asistencia'
    
    def desempeno_display(self, obj):
        """Muestra el desempeño."""
        if obj.desempeno_paciente:
            color = '#28a745' if obj.desempeno_paciente >= 7 else '#ffc107' if obj.desempeno_paciente >= 5 else '#dc3545'
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 8px; '
                'border-radius: 50%; font-weight: bold;">{}</span>',
                color,
                obj.desempeno_paciente
            )
        return '-'
    desempeno_display.short_description = 'Desempeño'
    
    def pagado_badge(self, obj):
        """Badge para estado de pago."""
        if obj.pagado:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px;">✓</span>'
            )
        return format_html(
            '<span style="background-color: #ffc107; color: black; padding: 3px 10px; '
            'border-radius: 3px;">⏳</span>'
        )
    pagado_badge.short_description = 'Pago'
    
    actions = ['marcar_completada', 'marcar_pagado']
    
    def marcar_completada(self, request, queryset):
        """Marcar como completada."""
        for sesion in queryset:
            sesion.completar()
        self.message_user(request, f'{queryset.count()} sesión/sesiones completada(s).')
    marcar_completada.short_description = 'Marcar como completada'
    
    def marcar_pagado(self, request, queryset):
        """Marcar como pagado."""
        count = queryset.update(pagado=True)
        self.message_user(request, f'{count} sesión/sesiones marcada(s) como pagada(s).')
    marcar_pagado.short_description = 'Marcar como pagado'


@admin.register(ObjetivoTerapeutico)
class ObjetivoTerapeuticoAdmin(admin.ModelAdmin):
    """Admin personalizado para Objetivo Terapéutico."""
    
    list_display = [
        'titulo', 'paciente_link', 'terapia_display', 'prioridad_badge',
        'fecha_inicio', 'fecha_limite', 'estado_badge', 'progreso_bar'
    ]
    
    list_filter = ['estado', 'prioridad', 'terapia', 'fecha_inicio']
    
    search_fields = [
        'titulo', 'descripcion', 'paciente__nombres', 'paciente__apellidos',
        'area_desarrollo'
    ]
    
    readonly_fields = [
        'esta_logrado', 'dias_transcurridos', 'dias_restantes',
        'fecha_creacion', 'fecha_actualizacion'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('paciente', 'terapia', 'titulo', 'descripcion', 'area_desarrollo')
        }),
        ('Clasificación', {
            'fields': ('prioridad',)
        }),
        ('Plazos', {
            'fields': (
                'fecha_inicio', 'fecha_limite', 'fecha_logro',
                'dias_transcurridos', 'dias_restantes'
            )
        }),
        ('Estado y Progreso', {
            'fields': (
                'estado', 'esta_logrado', 'porcentaje_avance'
            )
        }),
        ('Medición', {
            'fields': (
                'criterios_exito', 'metrica_actual', 'metrica_objetivo'
            )
        }),
        ('Estrategias y Notas', {
            'fields': ('estrategias', 'notas')
        }),
        ('Metadata', {
            'fields': ('creado_por', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'fecha_inicio'
    ordering = ['-prioridad', '-fecha_inicio']
    
    def paciente_link(self, obj):
        """Link al paciente."""
        return format_html(
            '<a href="{}">{}</a>',
            f'/admin/procedimientos/paciente/{obj.paciente.pk}/change/',
            obj.paciente.nombre_completo
        )
    paciente_link.short_description = 'Paciente'
    
    def terapia_display(self, obj):
        """Muestra la terapia."""
        return obj.terapia.nombre
    terapia_display.short_description = 'Terapia'
    
    def prioridad_badge(self, obj):
        """Badge de color para la prioridad."""
        colors = {
            'ALTA': '#dc3545',
            'MEDIA': '#ffc107',
            'BAJA': '#28a745',
        }
        color = colors.get(obj.prioridad, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_prioridad_display()
        )
    prioridad_badge.short_description = 'Prioridad'
    
    def estado_badge(self, obj):
        """Badge de color para el estado."""
        colors = {
            'EN_PROCESO': '#007bff',
            'LOGRADO': '#28a745',
            'PAUSADO': '#ffc107',
            'ABANDONADO': '#6c757d',
        }
        color = colors.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def progreso_bar(self, obj):
        """Barra de progreso."""
        color = '#28a745' if obj.porcentaje_avance >= 75 else '#ffc107' if obj.porcentaje_avance >= 50 else '#dc3545'
        return format_html(
            '<div style="width: 100px; height: 20px; background-color: #e9ecef; border-radius: 10px; overflow: hidden;">'
            '<div style="width: {}%; height: 100%; background-color: {}; display: flex; align-items: center; '
            'justify-content: center; color: white; font-size: 11px; font-weight: bold;">{}</div></div>',
            obj.porcentaje_avance,
            color,
            f'{obj.porcentaje_avance}%'
        )
    progreso_bar.short_description = 'Progreso'
    
    actions = ['marcar_logrado']
    
    def marcar_logrado(self, request, queryset):
        """Marcar como logrado."""
        for objetivo in queryset:
            objetivo.marcar_logrado()
        self.message_user(request, f'{queryset.count()} objetivo(s) marcado(s) como logrado(s).')
    marcar_logrado.short_description = 'Marcar como logrado'


@admin.register(EvolucionPaciente)
class EvolucionPacienteAdmin(admin.ModelAdmin):
    """Admin personalizado para Evolución del Paciente."""
    
    list_display = [
        'fecha', 'paciente_link', 'profesional_link', 'tipo_nota',
        'titulo', 'sesion_link'
    ]
    
    list_filter = ['fecha', 'tipo_nota', 'profesional']
    
    search_fields = [
        'titulo', 'contenido', 'paciente__nombres', 'paciente__apellidos',
        'tipo_nota'
    ]
    
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('paciente', 'sesion', 'fecha', 'profesional', 'tipo_nota', 'titulo')
        }),
        ('Contenido', {
            'fields': ('contenido',)
        }),
        ('Observaciones Específicas', {
            'fields': (
                'observaciones_conducta', 'observaciones_comunicacion',
                'observaciones_socializacion', 'cambios_medicacion'
            )
        }),
        ('Archivos', {
            'fields': ('archivos_adjuntos',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'fecha'
    ordering = ['-fecha', '-fecha_creacion']
    
    def paciente_link(self, obj):
        """Link al paciente."""
        return format_html(
            '<a href="{}">{}</a>',
            f'/admin/procedimientos/paciente/{obj.paciente.pk}/change/',
            obj.paciente.nombre_completo
        )
    paciente_link.short_description = 'Paciente'
    
    def profesional_link(self, obj):
        """Link al profesional."""
        return format_html(
            '<a href="{}">{}</a>',
            f'/admin/usuarios/usuario/{obj.profesional.pk}/change/',
            obj.profesional.get_full_name()
        )
    profesional_link.short_description = 'Profesional'
    
    def sesion_link(self, obj):
        """Link a la sesión."""
        if obj.sesion:
            return format_html(
                '<a href="{}">{}</a>',
                f'/admin/procedimientos/sesionterapeutica/{obj.sesion.pk}/change/',
                obj.sesion.numero_sesion
            )
        return '-'
    sesion_link.short_description = 'Sesión'
