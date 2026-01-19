# AGREGAR A: apps/procedimientos/admin.py

from django.contrib import admin
from .models import (CodigoCIE10, ValoracionProfesional, 
                     AdmisionTerapia, AsistenciaSesion)

# Si CodigoCIE10 no está registrado:
@admin.register(CodigoCIE10)
class CodigoCIE10Admin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'categoria']
    list_filter = ['categoria']
    search_fields = ['codigo', 'nombre', 'descripcion']

@admin.register(ValoracionProfesional)
class ValoracionProfesionalAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'terapeuta', 'terapia', 'fecha_valoracion', 'estado']
    list_filter = ['estado', 'terapia', 'fecha_valoracion']
    search_fields = ['paciente__nombre', 'terapeuta__username']
    readonly_fields = ['fecha_valoracion']

@admin.register(AdmisionTerapia)
class AdmisionTerapiaAdmin(admin.ModelAdmin):
    list_display = ['numero_admision', 'paciente', 'terapia', 'fecha_inicio', 
                    'cantidad_ordenada', 'cantidad_realizada', 'estado']
    list_filter = ['estado', 'terapia', 'fecha_inicio']
    search_fields = ['numero_admision', 'paciente__nombre']
    readonly_fields = ['fecha_creacion', 'progreso_porcentaje']

@admin.register(AsistenciaSesion)
class AsistenciaSesionAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'paciente', 'grupo', 'asistio', 'justificada']
    list_filter = ['asistio', 'justificada', 'fecha', 'grupo']
    search_fields = ['paciente__nombre']
    readonly_fields = ['fecha_registro']


# ============================================
# AGREGAR A: apps/grupos/admin.py

from .models import AlertaCupo

@admin.register(AlertaCupo)
class AlertaCupoAdmin(admin.ModelAdmin):
    list_display = ['grupo', 'pacientes_excedentes', 'estado', 'fecha_generacion']
    list_filter = ['estado', 'fecha_generacion']
    readonly_fields = ['fecha_generacion', 'fecha_resolucion']


# ============================================
# CREAR: apps/alertas/admin.py

from django.contrib import admin
from .models import AlertaInasistencia, ConfiguracionAlerta

@admin.register(AlertaInasistencia)
class AlertaInasistenciaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'dias_consecutivos', 'estado', 'sms_enviado', 'fecha_generacion']
    list_filter = ['estado', 'sms_enviado', 'fecha_generacion']
    search_fields = ['paciente__nombre']
    readonly_fields = ['fecha_generacion', 'fecha_envio_sms']

@admin.register(ConfiguracionAlerta)
class ConfiguracionAlertaAdmin(admin.ModelAdmin):
    list_display = ['dias_inasistencia_alerta', 'telefono_ips', 'activo']
