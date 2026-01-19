# CREAR: apps/alertas/utils.py

from django.utils import timezone
from django.db.models import Q
from apps.grupos.models import AsignacionGrupo
from .models import AlertaInasistencia, ConfiguracionAlerta


class GestorAlertas:
    """Gestión de alertas de inasistencia"""
    
    def verificar_inasistencias(self):
        """
        Verifica pacientes con 3+ inasistencias consecutivas
        Genera alertas y envía SMS
        """
        config = ConfiguracionAlerta.get_config()
        dias_limite = config.dias_inasistencia_alerta
        
        # Buscar asignaciones con inasistencias >= límite
        asignaciones_alerta = AsignacionGrupo.objects.filter(
            estado='ACTIVA',
            admision_terapia__estado='VIGENTE',
            dias_inasistencias_consecutivas__gte=dias_limite,
            alerta_inasistencia_enviada=False
        ).select_related('paciente', 'grupo', 'admision_terapia')
        
        alertas_creadas = []
        
        for asignacion in asignaciones_alerta:
            # Crear alerta
            alerta = AlertaInasistencia.objects.create(
                paciente=asignacion.paciente,
                dias_consecutivos=asignacion.dias_inasistencias_consecutivas,
                fecha_ultima_inasistencia=timezone.now().date(),
                telefono_destino=asignacion.paciente.acudiente_telefono
            )
            
            # Enviar SMS
            self._enviar_sms(alerta, config)
            
            # Marcar como enviada
            asignacion.alerta_inasistencia_enviada = True
            asignacion.save()
            
            alertas_creadas.append(alerta)
        
        return alertas_creadas
    
    def _enviar_sms(self, alerta, config):
        """Envía SMS al acudiente"""
        try:
            mensaje = config.mensaje_sms_template.format(
                nombre=alerta.paciente.nombre_completo,
                dias=alerta.dias_consecutivos,
                telefono_ips=config.telefono_ips
            )
            
            # IMPLEMENTAR: Integración con proveedor SMS
            # Ejemplo: Twilio, AWS SNS, etc.
            # Por ahora solo marcar como enviado
            
            alerta.sms_enviado = True
            alerta.fecha_envio_sms = timezone.now()
            alerta.estado = 'NOTIFICADA'
            alerta.save()
            
            return True
        except Exception as e:
            print(f"Error enviando SMS: {e}")
            return False
    
    def obtener_alertas_pendientes(self):
        """Obtiene alertas pendientes de atención"""
        return AlertaInasistencia.objects.filter(
            estado__in=['PENDIENTE', 'NOTIFICADA']
        ).select_related('paciente').order_by('-fecha_generacion')
    
    def marcar_atendida(self, alerta_id, usuario, observaciones=''):
        """Marca alerta como atendida"""
        alerta = AlertaInasistencia.objects.get(pk=alerta_id)
        alerta.estado = 'ATENDIDA'
        alerta.atendida_por = usuario
        alerta.fecha_atencion = timezone.now()
        alerta.observaciones = observaciones
        alerta.save()
        
        # Resetear contador en asignación
        asignaciones = AsignacionGrupo.objects.filter(
            paciente=alerta.paciente,
            estado='ACTIVA'
        )
        asignaciones.update(
            dias_inasistencias_consecutivas=0,
            alerta_inasistencia_enviada=False
        )
        
        return alerta


# CREAR: apps/alertas/tasks.py (para Celery)

from celery import shared_task
from .utils import GestorAlertas

@shared_task
def verificar_inasistencias_diarias():
    """
    Tarea diaria: verificar inasistencias
    Ejecutar: 0 20 * * * (8 PM todos los días)
    """
    gestor = GestorAlertas()
    alertas = gestor.verificar_inasistencias()
    return f"Creadas {len(alertas)} alertas"
