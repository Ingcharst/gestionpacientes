"""
Configuración del panel de administración para terapias.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import CategoriaTerapia, Terapia


@admin.register(CategoriaTerapia)
class CategoriaTerapiaAdmin(admin.ModelAdmin):
    """Administración de categorías de terapias."""
    
    list_display = (
        'codigo', 'nombre', 'color_badge',
        'numero_terapias_count', 'orden', 'activo'
    )
    
    list_filter = ('activo',)
    
    search_fields = ('nombre', 'codigo', 'descripcion')
    
    readonly_fields = (
        'fecha_creacion', 'fecha_actualizacion',
        'numero_terapias', 'tiene_terapias'
    )
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'codigo', 'descripcion')
        }),
        ('Visualización', {
            'fields': ('color', 'icono', 'orden')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Información del Sistema', {
            'fields': (
                'numero_terapias', 'tiene_terapias',
                'fecha_creacion', 'fecha_actualizacion'
            ),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    ordering = ['orden', 'nombre']
    
    def color_badge(self, obj):
        """Muestra un badge con el color de la categoría."""
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            obj.color,
            obj.nombre
        )
    color_badge.short_description = 'Color'
    
    def numero_terapias_count(self, obj):
        """Muestra el número de terapias."""
        count = obj.numero_terapias
        if count > 0:
            return format_html(
                '<span class="badge bg-success">{} terapias</span>',
                count
            )
        return format_html('<span class="badge bg-secondary">Sin terapias</span>')
    numero_terapias_count.short_description = 'Terapias'
    
    actions = ['activar', 'desactivar']
    
    def activar(self, request, queryset):
        """Activa categorías."""
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} categoría(s) activada(s).')
    activar.short_description = "Activar categorías"
    
    def desactivar(self, request, queryset):
        """Desactiva categorías."""
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} categoría(s) desactivada(s).')
    desactivar.short_description = "Desactivar categorías"


@admin.register(Terapia)
class TerapiaAdmin(admin.ModelAdmin):
    """Administración de terapias."""
    
    list_display = (
        'codigo', 'nombre_corto', 'categoria',
        'especialidad_badge', 'modalidad_badge',
        'duracion_display', 'costo_display',
        'activo', 'destacado'
    )
    
    list_filter = (
        'categoria', 'especialidad', 'modalidad',
        'nivel_intensidad', 'activo', 'destacado',
        'requiere_evaluacion_previa', 'requiere_orden_medica',
        'disponible_online', 'disponible_domicilio'
    )
    
    search_fields = (
        'nombre', 'codigo', 'descripcion',
        'descripcion_corta', 'objetivos'
    )
    
    readonly_fields = (
        'fecha_creacion', 'fecha_actualizacion',
        'nombre_completo', 'duracion_formateada',
        'costo_formateado', 'rango_edad',
        'es_grupal', 'requiere_consultorios_especiales',
        'tiene_equipamiento_especial'
    )
    
    date_hierarchy = 'fecha_creacion'
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'nombre', 'codigo', 'categoria',
                'descripcion', 'descripcion_corta'
            )
        }),
        ('Clasificación', {
            'fields': (
                'modalidad', 'especialidad', 'nivel_intensidad'
            )
        }),
        ('Duración y Frecuencia', {
            'fields': (
                'duracion_minutos', 'duracion_minima_minutos',
                'duracion_maxima_minutos', 'duracion_formateada',
                'frecuencia_semanal_recomendada'
            )
        }),
        ('Costos', {
            'fields': (
                'costo_sesion', 'costo_minimo',
                'costo_paquete_mensual', 'costo_formateado',
                'permite_descuento'
            )
        }),
        ('Requisitos', {
            'fields': (
                'edad_minima', 'edad_maxima', 'rango_edad',
                'requiere_evaluacion_previa', 'requiere_orden_medica'
            )
        }),
        ('Configuración', {
            'fields': (
                'capacidad_minima', 'capacidad_maxima',
                'requiere_acompanante'
            )
        }),
        ('Consultorios y Equipamiento', {
            'fields': (
                'tipos_consultorio_requeridos',
                'equipamiento_requerido',
                'requiere_consultorios_especiales',
                'tiene_equipamiento_especial'
            ),
            'classes': ('collapse',)
        }),
        ('Información Adicional', {
            'fields': (
                'objetivos', 'metodologia', 'beneficios',
                'contraindicaciones', 'notas'
            ),
            'classes': ('collapse',)
        }),
        ('Disponibilidad', {
            'fields': (
                'disponible_online', 'disponible_domicilio'
            )
        }),
        ('Multimedia', {
            'fields': (
                'imagen', 'folleto_url', 'video_url'
            ),
            'classes': ('collapse',)
        }),
        ('Estado y Orden', {
            'fields': (
                'activo', 'destacado', 'orden'
            )
        }),
        ('Información del Sistema', {
            'fields': (
                'nombre_completo', 'es_grupal',
                'fecha_creacion', 'fecha_actualizacion'
            ),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    ordering = ['categoria', 'orden', 'nombre']
    
    def nombre_corto(self, obj):
        """Muestra el nombre truncado."""
        if len(obj.nombre) > 50:
            return f"{obj.nombre[:50]}..."
        return obj.nombre
    nombre_corto.short_description = 'Nombre'
    nombre_corto.admin_order_field = 'nombre'
    
    def especialidad_badge(self, obj):
        """Muestra la especialidad con badge."""
        colors = {
            'LENGUAJE': 'primary',
            'OCUPACIONAL': 'success',
            'FISICA': 'info',
            'PSICOLOGIA': 'warning',
            'CONDUCTUAL': 'danger',
            'INTEGRACION_SENSORIAL': 'secondary',
            'MUSICOTERAPIA': 'dark',
            'ARTETERAPIA': 'light',
            'NEUROLOGICA': 'primary',
            'SOCIAL': 'success',
            'COGNITIVA': 'info',
            'ALIMENTACION': 'warning',
        }
        color = colors.get(obj.especialidad, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_especialidad_display()
        )
    especialidad_badge.short_description = 'Especialidad'
    
    def modalidad_badge(self, obj):
        """Muestra la modalidad con badge."""
        colors = {
            'INDIVIDUAL': 'primary',
            'GRUPAL': 'success',
            'FAMILIAR': 'info',
            'PAREJA': 'warning',
            'MIXTA': 'secondary',
        }
        color = colors.get(obj.modalidad, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_modalidad_display()
        )
    modalidad_badge.short_description = 'Modalidad'
    
    def duracion_display(self, obj):
        """Muestra la duración formateada."""
        return obj.duracion_formateada
    duracion_display.short_description = 'Duración'
    
    def costo_display(self, obj):
        """Muestra el costo formateado."""
        return format_html(
            '<strong style="color: green;">{}</strong>',
            obj.costo_formateado
        )
    costo_display.short_description = 'Costo'
    
    actions = [
        'activar', 'desactivar', 'marcar_destacado',
        'desmarcar_destacado', 'duplicar_terapia'
    ]
    
    def activar(self, request, queryset):
        """Activa terapias."""
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} terapia(s) activada(s).')
    activar.short_description = "Activar terapias"
    
    def desactivar(self, request, queryset):
        """Desactiva terapias."""
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} terapia(s) desactivada(s).')
    desactivar.short_description = "Desactivar terapias"
    
    def marcar_destacado(self, request, queryset):
        """Marca terapias como destacadas."""
        updated = queryset.update(destacado=True)
        self.message_user(request, f'{updated} terapia(s) marcada(s) como destacada(s).')
    marcar_destacado.short_description = "Marcar como destacado"
    
    def desmarcar_destacado(self, request, queryset):
        """Desmarca terapias destacadas."""
        updated = queryset.update(destacado=False)
        self.message_user(request, f'{updated} terapia(s) desmarcada(s).')
    desmarcar_destacado.short_description = "Desmarcar destacado"
    
    def duplicar_terapia(self, request, queryset):
        """Duplica terapias seleccionadas."""
        count = 0
        for terapia in queryset:
            terapia.pk = None
            terapia.codigo = f"{terapia.codigo}_COPIA"
            terapia.nombre = f"{terapia.nombre} (Copia)"
            terapia.save()
            count += 1
        self.message_user(request, f'{count} terapia(s) duplicada(s).')
    duplicar_terapia.short_description = "Duplicar terapias"
