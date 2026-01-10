"""
Señales para automatizar procesos de asignación y actualización de grupos.
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import AsignacionGrupo, GrupoTerapeutico, PacientePendiente


@receiver(post_save, sender=AsignacionGrupo)
def actualizar_contador_grupo_al_crear(sender, instance, created, **kwargs):
    """
    Actualiza el contador de pacientes del grupo cuando se crea o modifica una asignación.
    """
    if created or instance.estado == 'ACTIVA':
        # Actualizar contador del grupo
        instance.grupo.actualizar_contador_pacientes()
        
        # Actualizar estado del paciente
        if instance.estado == 'ACTIVA':
            paciente = instance.paciente
            paciente.tiene_grupo_asignado = True
            paciente.grupo_actual = instance.grupo
            paciente.estado_asignacion = 'ASIGNADO'
            paciente.save(update_fields=['tiene_grupo_asignado', 'grupo_actual', 'estado_asignacion'])


@receiver(post_delete, sender=AsignacionGrupo)
def actualizar_contador_grupo_al_eliminar(sender, instance, **kwargs):
    """
    Actualiza el contador de pacientes del grupo cuando se elimina una asignación.
    """
    # Actualizar contador del grupo
    instance.grupo.actualizar_contador_pacientes()
    
    # Actualizar estado del paciente si era su única asignación activa
    paciente = instance.paciente
    asignaciones_activas = AsignacionGrupo.objects.filter(
        paciente=paciente,
        estado='ACTIVA'
    ).exclude(pk=instance.pk)
    
    if not asignaciones_activas.exists():
        paciente.tiene_grupo_asignado = False
        paciente.grupo_actual = None
        paciente.estado_asignacion = 'SIN_ASIGNAR'
        paciente.save(update_fields=['tiene_grupo_asignado', 'grupo_actual', 'estado_asignacion'])


@receiver(pre_save, sender=AsignacionGrupo)
def manejar_cambio_estado_asignacion(sender, instance, **kwargs):
    """
    Maneja cambios de estado en las asignaciones y actualiza el paciente.
    """
    if instance.pk:  # Solo si ya existe (no es nuevo)
        try:
            asignacion_anterior = AsignacionGrupo.objects.get(pk=instance.pk)
            
            # Si cambió de ACTIVA a otro estado
            if asignacion_anterior.estado == 'ACTIVA' and instance.estado != 'ACTIVA':
                # Verificar si el paciente tiene otras asignaciones activas
                otras_activas = AsignacionGrupo.objects.filter(
                    paciente=instance.paciente,
                    estado='ACTIVA'
                ).exclude(pk=instance.pk).exists()
                
                if not otras_activas:
                    # Marcar como pendiente si no tiene otras asignaciones
                    instance.paciente.tiene_grupo_asignado = False
                    instance.paciente.grupo_actual = None
                    instance.paciente.estado_asignacion = 'EN_ESPERA'
                    instance.paciente.save(update_fields=['tiene_grupo_asignado', 'grupo_actual', 'estado_asignacion'])
        
        except AsignacionGrupo.DoesNotExist:
            pass


@receiver(post_save, sender=PacientePendiente)
def actualizar_estado_paciente_pendiente(sender, instance, created, **kwargs):
    """
    Actualiza el estado del paciente cuando se marca como pendiente.
    """
    if created and instance.estado == 'PENDIENTE':
        paciente = instance.paciente
        if not paciente.tiene_grupo_asignado:
            paciente.estado_asignacion = 'EN_ESPERA'
            paciente.save(update_fields=['estado_asignacion'])


@receiver(post_save, sender=PacientePendiente)
def notificar_paciente_pendiente(sender, instance, created, **kwargs):
    """
    Genera notificación cuando un paciente queda pendiente.
    En producción, aquí se enviaría un email o notificación al sistema.
    """
    if created and instance.estado == 'PENDIENTE':
        # TODO: Implementar sistema de notificaciones
        # Por ahora solo se registra en logs
        import logging
        logger = logging.getLogger('grupos')
        logger.warning(
            f"ALERTA: Paciente {instance.paciente.nombres} {instance.paciente.apellidos} "
            f"queda pendiente de asignación. Prioridad: {instance.get_prioridad_display()}"
        )
