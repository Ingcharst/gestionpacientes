"""
Configuración del panel de administración para consultorios.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Consultorio, Sala, AsignacionConsultorio, DisponibilidadConsultorio


class SalaInline(admin.TabularInline):
    """Inline para mostrar salas dentro de consultorio."""
    model = Sala
    extra = 1
    fields = ('nombre', 'tipo', 'area_metros', 'activo')


class AsignacionConsultorioInline(admin.TabularInline):
    """Inline para mostrar asignaciones dentro de consultorio."""
    model = AsignacionConsultorio
    extra = 0
    fields = ('terapeuta', 'tipo_asignacion', 'fecha_inicio', 'fecha_fin', 'activo')
    readonly_fields = ('fecha_asignacion',)


@admin.register(Consultorio)
class ConsultorioAdmin(admin.ModelAdmin):
    """Administración de consultorios."""
    
    inlines = [SalaInline, AsignacionConsultorioInline]
    
    list_display = (
        'codigo', 'nombre', 'tipo', 'piso', 'numero',
        'capacidad', 'estado_badge', 'foto_thumbnail',
        'tiene_equipamiento_badge', 'activo'
    )
    
    list_filter = (
        'tipo', 'estado', 'piso', 'activo',
        'tiene_ventana', 'tiene_aire_acondicionado',
        'accesible_silla_ruedas'
    )
    
    search_fields = (
        'nombre', 'codigo', 'numero',
        'caracteristicas', 'observaciones'
    )
    
    readonly_fields = (
        'fecha_creacion', 'fecha_actualizacion',
        'nombre_completo', 'esta_disponible'
    )
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'nombre', 'codigo', 'tipo',
                'piso', 'numero'
            )
        }),
        ('Características Físicas', {
            'fields': (
                'capacidad', 'area_metros', 'foto',
                'tiene_ventana', 'tiene_aire_acondicionado',
                'accesible_silla_ruedas'
            )
        }),
        ('Equipamiento y Detalles', {
            'fields': (
                'equipamiento', 'caracteristicas', 'observaciones'
            )
        }),
        ('Estado', {
            'fields': (
                'estado', 'activo'
            )
        }),
        ('Información del Sistema', {
            'fields': (
                'nombre_completo', 'esta_disponible',
                'fecha_creacion', 'fecha_actualizacion'
            ),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    ordering = ['piso', 'numero']
    
    def estado_badge(self, obj):
        """Muestra el estado con un badge de color."""
        colors = {
            'DISPONIBLE': 'success',
            'OCUPADO': 'warning',
            'MANTENIMIENTO': 'info',
            'INACTIVO': 'secondary'
        }
        color = colors.get(obj.estado, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def foto_thumbnail(self, obj):
        """Muestra miniatura de la foto."""
        if obj.foto:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />',
                obj.foto.url
            )
        return "Sin foto"
    foto_thumbnail.short_description = 'Foto'
    
    def tiene_equipamiento_badge(self, obj):
        """Muestra si tiene equipamiento."""
        if obj.tiene_equipamiento:
            return format_html(
                '<span class="badge bg-success">✓ {}</span>',
                len(obj.equipamiento)
            )
        return format_html('<span class="badge bg-secondary">Sin equipamiento</span>')
    tiene_equipamiento_badge.short_description = 'Equipamiento'
    
    actions = ['marcar_disponible', 'marcar_mantenimiento', 'activar', 'desactivar']
    
    def marcar_disponible(self, request, queryset):
        """Marca consultorios como disponibles."""
        updated = queryset.update(estado='DISPONIBLE')
        self.message_user(request, f'{updated} consultorio(s) marcado(s) como disponible.')
    marcar_disponible.short_description = "Marcar como disponible"
    
    def marcar_mantenimiento(self, request, queryset):
        """Marca consultorios en mantenimiento."""
        updated = queryset.update(estado='MANTENIMIENTO')
        self.message_user(request, f'{updated} consultorio(s) marcado(s) en mantenimiento.')
    marcar_mantenimiento.short_description = "Marcar en mantenimiento"
    
    def activar(self, request, queryset):
        """Activa consultorios."""
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} consultorio(s) activado(s).')
    activar.short_description = "Activar consultorios"
    
    def desactivar(self, request, queryset):
        """Desactiva consultorios."""
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} consultorio(s) desactivado(s).')
    desactivar.short_description = "Desactivar consultorios"


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    """Administración de salas."""
    
    list_display = (
        'nombre', 'consultorio', 'tipo',
        'area_metros', 'activo'
    )
    
    list_filter = (
        'tipo', 'activo', 'consultorio__piso'
    )
    
    search_fields = (
        'nombre', 'descripcion',
        'consultorio__nombre', 'consultorio__codigo'
    )
    
    readonly_fields = ('fecha_creacion',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('consultorio', 'nombre', 'tipo')
        }),
        ('Detalles', {
            'fields': (
                'area_metros', 'descripcion',
                'equipamiento_especifico', 'activo'
            )
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    ordering = ['consultorio', 'nombre']


@admin.register(AsignacionConsultorio)
class AsignacionConsultorioAdmin(admin.ModelAdmin):
    """Administración de asignaciones de consultorios."""
    
    list_display = (
        'consultorio', 'terapeuta_nombre', 'tipo_asignacion',
        'fecha_inicio', 'fecha_fin', 'vigente_badge',
        'prioridad_stars', 'activo'
    )
    
    list_filter = (
        'tipo_asignacion', 'activo', 'fecha_inicio',
        'prioridad', 'consultorio__piso'
    )
    
    search_fields = (
        'consultorio__nombre', 'consultorio__codigo',
        'terapeuta__first_name', 'terapeuta__last_name',
        'terapeuta__username'
    )
    
    readonly_fields = (
        'fecha_asignacion', 'fecha_actualizacion',
        'esta_vigente', 'es_permanente'
    )
    
    date_hierarchy = 'fecha_inicio'
    
    fieldsets = (
        ('Asignación', {
            'fields': (
                'consultorio', 'terapeuta', 'tipo_asignacion'
            )
        }),
        ('Periodo', {
            'fields': (
                'fecha_inicio', 'fecha_fin', 'dias_semana'
            )
        }),
        ('Horario y Prioridad', {
            'fields': (
                'horario', 'prioridad'
            )
        }),
        ('Detalles', {
            'fields': (
                'notas', 'activo'
            )
        }),
        ('Información del Sistema', {
            'fields': (
                'esta_vigente', 'es_permanente',
                'fecha_asignacion', 'fecha_actualizacion'
            ),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    ordering = ['-fecha_inicio', '-prioridad']
    
    def terapeuta_nombre(self, obj):
        """Muestra el nombre completo del terapeuta."""
        return obj.terapeuta.get_full_name()
    terapeuta_nombre.short_description = 'Terapeuta'
    terapeuta_nombre.admin_order_field = 'terapeuta__first_name'
    
    def vigente_badge(self, obj):
        """Muestra si la asignación está vigente."""
        if obj.esta_vigente:
            return format_html('<span class="badge bg-success">✓ Vigente</span>')
        return format_html('<span class="badge bg-secondary">No vigente</span>')
    vigente_badge.short_description = 'Vigencia'
    
    def prioridad_stars(self, obj):
        """Muestra la prioridad con estrellas."""
        stars = '⭐' * obj.prioridad
        return format_html('<span title="Prioridad {}">{}</span>', obj.prioridad, stars)
    prioridad_stars.short_description = 'Prioridad'
    
    actions = ['activar_asignaciones', 'desactivar_asignaciones']
    
    def activar_asignaciones(self, request, queryset):
        """Activa asignaciones."""
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} asignación(es) activada(s).')
    activar_asignaciones.short_description = "Activar asignaciones"
    
    def desactivar_asignaciones(self, request, queryset):
        """Desactiva asignaciones."""
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} asignación(es) desactivada(s).')
    desactivar_asignaciones.short_description = "Desactivar asignaciones"


@admin.register(DisponibilidadConsultorio)
class DisponibilidadConsultorioAdmin(admin.ModelAdmin):
    """Administración de disponibilidad de consultorios."""
    
    list_display = (
        'consultorio_codigo', 'fecha', 'hora_inicio',
        'hora_fin', 'duracion', 'estado_badge',
        'terapeuta_nombre'
    )
    
    list_filter = (
        'estado', 'fecha', 'consultorio__piso',
        'terapeuta'
    )
    
    search_fields = (
        'consultorio__nombre', 'consultorio__codigo',
        'terapeuta__first_name', 'terapeuta__last_name',
        'motivo_bloqueo'
    )
    
    readonly_fields = (
        'fecha_creacion', 'duracion_minutos', 'esta_disponible'
    )
    
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Consultorio y Fecha', {
            'fields': ('consultorio', 'fecha')
        }),
        ('Horario', {
            'fields': (
                'hora_inicio', 'hora_fin', 'duracion_minutos'
            )
        }),
        ('Estado', {
            'fields': (
                'estado', 'esta_disponible', 'terapeuta'
            )
        }),
        ('Detalles', {
            'fields': (
                'motivo_bloqueo', 'notas'
            )
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 50
    ordering = ['-fecha', 'hora_inicio']
    
    def consultorio_codigo(self, obj):
        """Muestra el código del consultorio."""
        return obj.consultorio.codigo
    consultorio_codigo.short_description = 'Consultorio'
    consultorio_codigo.admin_order_field = 'consultorio__codigo'
    
    def duracion(self, obj):
        """Muestra la duración."""
        return f"{obj.duracion_minutos} min"
    duracion.short_description = 'Duración'
    
    def estado_badge(self, obj):
        """Muestra el estado con badge de color."""
        colors = {
            'DISPONIBLE': 'success',
            'RESERVADO': 'info',
            'OCUPADO': 'warning',
            'BLOQUEADO': 'danger'
        }
        color = colors.get(obj.estado, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def terapeuta_nombre(self, obj):
        """Muestra el nombre del terapeuta si existe."""
        if obj.terapeuta:
            return obj.terapeuta.get_full_name()
        return "-"
    terapeuta_nombre.short_description = 'Terapeuta'
    
    actions = ['marcar_disponible', 'bloquear_horarios']
    
    def marcar_disponible(self, request, queryset):
        """Marca horarios como disponibles."""
        updated = queryset.update(estado='DISPONIBLE', terapeuta=None)
        self.message_user(request, f'{updated} horario(s) marcado(s) como disponible.')
    marcar_disponible.short_description = "Marcar como disponible"
    
    def bloquear_horarios(self, request, queryset):
        """Bloquea horarios."""
        updated = queryset.update(estado='BLOQUEADO')
        self.message_user(request, f'{updated} horario(s) bloqueado(s).')
    bloquear_horarios.short_description = "Bloquear horarios"
