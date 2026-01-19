from django.contrib import admin
from .models import AlertaInasistencia, ConfiguracionAlerta

# Register your models here.

@admin.register(AlertaInasistencia)
class AlertaInasistenciaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'dias_consecutivos', 'estado', 'sms_enviado', 'fecha_generacion']
    list_filter = ['estado', 'sms_enviado', 'fecha_generacion']
    search_fields = ['paciente__nombre']
    readonly_fields = ['fecha_generacion', 'fecha_envio_sms']

@admin.register(ConfiguracionAlerta)
class ConfiguracionAlertaAdmin(admin.ModelAdmin):
    list_display = ['dias_inasistencia_alerta', 'telefono_ips', 'activo']




