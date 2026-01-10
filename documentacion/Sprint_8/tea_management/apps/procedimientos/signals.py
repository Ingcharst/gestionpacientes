"""
Signals para el módulo de procedimientos.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.procedimientos.models import SesionTerapeutica, Procedimiento


@receiver(post_save, sender=SesionTerapeutica)
def crear_evolucion_automatica(sender, instance, created, **kwargs):
    """
    Crear automáticamente una evolución cuando se completa una sesión.
    """
    if not created and instance.estado == 'COMPLETADA':
        # Aquí se podría crear automáticamente una evolución básica
        # o enviar notificaciones
        pass


@receiver(post_save, sender=Procedimiento)
def notificar_procedimiento_completado(sender, instance, created, **kwargs):
    """
    Notificar cuando un procedimiento se completa.
    """
    if not created and instance.estado == 'COMPLETADO':
        # Aquí se podría enviar notificación por email o SMS
        pass
