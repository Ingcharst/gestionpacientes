"""
Configuración del panel de administración para gestión de grupos.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import GrupoTerapeutico, AsignacionGrupo, PacientePendiente, AlertaCupo


@admin.register(GrupoTerapeutico)
class GrupoTerapeuticoAdmin(admin.ModelAdmin):
    """Admin para grupos terapéuticos"""
    
    list_display = [
        'nombre',
        'horario_display',
        'capacidad_display',
        'ocupacion_display',
        'dias_display',
        'activo',
        'fecha_creacion',
    ]
    
    list_filter = [
        'activo',
        'hora_inicio',
        'capacidad_maxima',
    ]
    
    search_fields = [
        'nombre',
        'descripcion',
    ]
    
    readonly_fields = [
        'pacientes_actuales',
        'cupos_disponibles',
        'porcentaje_ocupacion',
        'fecha_creacion',
        'fecha_actualizacion',
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'activo')
        }),
        ('Horario', {
            'fields': ('hora_inicio', 'hora_fin', 'dias_disponibles')
        }),
        ('Capacidad', {
            'fields': (
                'capacidad_maxima',
                'pacientes_actuales',
                'cupos_disponibles',
                'porcentaje_ocupacion',
            )
        }),
        ('Información Adicional', {
            'fields': ('notas', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activar_grupos', 'desactivar_grupos', 'actualizar_contadores']
    
    def horario_display(self, obj):
        """Muestra el horario del grupo"""
        return f"{obj.hora_inicio.strftime('%H:%M')} - {obj.hora_fin.strftime('%H:%M')}"
    horario_display.short_description = 'Horario'
    
    def capacidad_display(self, obj):
        """Muestra la capacidad del grupo"""
        return f"{obj.pacientes_actuales}/{obj.capacidad_maxima}"
    capacidad_display.short_description = 'Capacidad'
    
    def ocupacion_display(self, obj):
        """Muestra barra de ocupación visual"""
        porcentaje = obj.porcentaje_ocupacion
        
        if porcentaje >= 90:
            color = 'red'
        elif porcentaje >= 70:
            color = 'orange'
        else:
            color = 'green'
        
        porcentaje_formateado = f"{porcentaje:.1f}"
        return format_html(
            '<div style="width:100px; background-color:#f0f0f0; border-radius:3px;">'
            '<div style="width:{}%; background-color:{}; height:20px; border-radius:3px; text-align:center; color:white; font-size:11px; line-height:20px;">{}%</div>'
            '</div>',
            porcentaje, color, porcentaje_formateado
        )
    ocupacion_display.short_description = 'Ocupación'
    
    def dias_display(self, obj):
        """Muestra los días de la semana"""
        return obj.dias_semana_texto
    dias_display.short_description = 'Días'
    
    def activar_grupos(self, request, queryset):
        """Acción para activar grupos seleccionados"""
        count = queryset.update(activo=True)
        self.message_user(request, f'{count} grupo(s) activado(s) exitosamente.')
    activar_grupos.short_description = 'Activar grupos seleccionados'
    
    def desactivar_grupos(self, request, queryset):
        """Acción para desactivar grupos seleccionados"""
        count = queryset.update(activo=False)
        self.message_user(request, f'{count} grupo(s) desactivado(s) exitosamente.')
    desactivar_grupos.short_description = 'Desactivar grupos seleccionados'
    
    def actualizar_contadores(self, request, queryset):
        """Recalcula el contador de pacientes"""
        for grupo in queryset:
            grupo.actualizar_contador_pacientes()
        self.message_user(request, f'Contadores actualizados para {queryset.count()} grupo(s).')
    actualizar_contadores.short_description = 'Actualizar contadores de pacientes'


@admin.register(AsignacionGrupo)
class AsignacionGrupoAdmin(admin.ModelAdmin):
    """Admin para asignaciones a grupos"""
    
    list_display = [
        'paciente_display',
        'grupo',
        'dias_display',
        'numero_terapias_semanales',
        'estado_display',
        'fecha_inicio_asignacion',
        'duracion_display',
    ]
    
    list_filter = [
        'estado',
        'grupo',
        'fecha_inicio_asignacion',
        'numero_terapias_semanales',
    ]
    
    search_fields = [
        'paciente__nombres',
        'paciente__apellidos',
        'paciente__numero_documento',
        'grupo__nombre',
    ]
    
    readonly_fields = [
        'fecha_creacion',
        'fecha_actualizacion',
        'duracion_dias',
    ]
    
    fieldsets = (
        ('Asignación', {
            'fields': ('paciente', 'grupo', 'estado')
        }),
        ('Configuración de Asistencia', {
            'fields': ('dias_asistencia', 'numero_terapias_semanales')
        }),
        ('Fechas', {
            'fields': (
                'fecha_inicio_asignacion',
                'fecha_fin_asignacion',
                'duracion_dias',
            )
        }),
        ('Información Adicional', {
            'fields': ('notas', 'motivo_suspension'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['finalizar_asignaciones', 'suspender_asignaciones', 'reactivar_asignaciones']
    
    def paciente_display(self, obj):
        """Enlace al paciente"""
        url = reverse('admin:procedimientos_paciente_change', args=[obj.paciente.pk])
        return format_html(
            '<a href="{}">{} {}</a>',
            url,
            obj.paciente.nombres,
            obj.paciente.apellidos
        )
    paciente_display.short_description = 'Paciente'
    
    def dias_display(self, obj):
        """Muestra los días de asistencia"""
        return obj.dias_asistencia_texto
    dias_display.short_description = 'Días de Asistencia'
    
    def estado_display(self, obj):
        """Muestra el estado con color"""
        colores = {
            'ACTIVA': 'green',
            'SUSPENDIDA': 'orange',
            'FINALIZADA': 'gray',
            'CANCELADA': 'red',
        }
        color = colores.get(obj.estado, 'black')
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_display.short_description = 'Estado'
    
    def duracion_display(self, obj):
        """Muestra la duración de la asignación"""
        dias = obj.duracion_dias
        return f"{dias} día{'s' if dias != 1 else ''}"
    duracion_display.short_description = 'Duración'
    
    def finalizar_asignaciones(self, request, queryset):
        """Finaliza asignaciones seleccionadas"""
        count = 0
        for asignacion in queryset:
            if asignacion.estado == 'ACTIVA':
                asignacion.finalizar(motivo='Finalización masiva desde admin')
                count += 1
        self.message_user(request, f'{count} asignación(es) finalizada(s).')
    finalizar_asignaciones.short_description = 'Finalizar asignaciones'
    
    def suspender_asignaciones(self, request, queryset):
        """Suspende asignaciones seleccionadas"""
        count = 0
        for asignacion in queryset:
            if asignacion.estado == 'ACTIVA':
                asignacion.suspender(motivo='Suspensión masiva desde admin')
                count += 1
        self.message_user(request, f'{count} asignación(es) suspendida(s).')
    suspender_asignaciones.short_description = 'Suspender asignaciones'
    
    def reactivar_asignaciones(self, request, queryset):
        """Reactiva asignaciones suspendidas"""
        count = 0
        for asignacion in queryset:
            if asignacion.estado == 'SUSPENDIDA':
                asignacion.reactivar()
                count += 1
        self.message_user(request, f'{count} asignación(es) reactivada(s).')
    reactivar_asignaciones.short_description = 'Reactivar asignaciones'


@admin.register(PacientePendiente)
class PacientePendienteAdmin(admin.ModelAdmin):
    """Admin para pacientes pendientes"""
    
    list_display = [
        'paciente_display',
        'prioridad_display',
        'estado_display',
        'preferencia_horario',
        'dias_display',
        'dias_esperando_display',
        'fecha_solicitud',
    ]
    
    list_filter = [
        'estado',
        'prioridad',
        'fecha_solicitud',
    ]
    
    search_fields = [
        'paciente__nombres',
        'paciente__apellidos',
        'paciente__numero_documento',
    ]
    
    readonly_fields = [
        'fecha_solicitud',
        'fecha_asignacion',
        'dias_esperando',
    ]
    
    fieldsets = (
        ('Paciente', {
            'fields': ('paciente', 'prioridad', 'estado')
        }),
        ('Preferencias', {
            'fields': ('preferencia_horario', 'dias_preferidos')
        }),
        ('Resolución', {
            'fields': ('grupo_asignado', 'fecha_asignacion'),
        }),
        ('Información Adicional', {
            'fields': ('observaciones', 'motivo_cancelacion'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('fecha_solicitud', 'dias_esperando'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['marcar_prioridad_alta', 'cancelar_solicitudes']
    
    def paciente_display(self, obj):
        """Enlace al paciente"""
        url = reverse('admin:procedimientos_paciente_change', args=[obj.paciente.pk])
        return format_html(
            '<a href="{}">{} {}</a>',
            url,
            obj.paciente.nombres,
            obj.paciente.apellidos
        )
    paciente_display.short_description = 'Paciente'
    
    def prioridad_display(self, obj):
        """Muestra la prioridad con color"""
        colores = {
            'ALTA': 'red',
            'MEDIA': 'orange',
            'BAJA': 'green',
        }
        color = colores.get(obj.prioridad, 'black')
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            color,
            obj.get_prioridad_display()
        )
    prioridad_display.short_description = 'Prioridad'
    
    def estado_display(self, obj):
        """Muestra el estado con color"""
        colores = {
            'PENDIENTE': 'orange',
            'ASIGNADO': 'green',
            'CANCELADO': 'red',
        }
        color = colores.get(obj.estado, 'black')
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_display.short_description = 'Estado'
    
    def dias_display(self, obj):
        """Muestra los días preferidos"""
        return obj.dias_preferidos_texto
    dias_display.short_description = 'Días Preferidos'
    
    def dias_esperando_display(self, obj):
        """Muestra los días esperando con color"""
        dias = obj.dias_esperando
        
        if dias > 7:
            color = 'red'
        elif dias > 3:
            color = 'orange'
        else:
            color = 'green'
        
        return format_html(
            '<span style="color:{}; font-weight:bold;">{} día{}</span>',
            color,
            dias,
            's' if dias != 1 else ''
        )
    dias_esperando_display.short_description = 'Tiempo Esperando'
    
    def marcar_prioridad_alta(self, request, queryset):
        """Marca como prioridad alta"""
        count = queryset.filter(estado='PENDIENTE').update(prioridad='ALTA')
        self.message_user(request, f'{count} paciente(s) marcado(s) como prioridad alta.')
    marcar_prioridad_alta.short_description = 'Marcar como prioridad ALTA'
    
    def cancelar_solicitudes(self, request, queryset):
        """Cancela solicitudes pendientes"""
        count = 0
        for pendiente in queryset:
            if pendiente.estado == 'PENDIENTE':
                pendiente.cancelar(motivo='Cancelación masiva desde admin')
                count += 1
        self.message_user(request, f'{count} solicitud(es) cancelada(s).')
    cancelar_solicitudes.short_description = 'Cancelar solicitudes'


@admin.register(AlertaCupo)
class AlertaCupoAdmin(admin.ModelAdmin):
    list_display = ['grupo', 'pacientes_excedentes', 'estado', 'fecha_generacion']
    list_filter = ['estado', 'fecha_generacion']
    readonly_fields = ['fecha_generacion', 'fecha_resolucion']


