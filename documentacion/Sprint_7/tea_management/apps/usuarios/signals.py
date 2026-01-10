"""
Signals para el módulo de usuarios.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuario, Perfil


@receiver(post_save, sender=Usuario)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Crea automáticamente un perfil cuando se crea un nuevo usuario.
    """
    if created:
        Perfil.objects.create(usuario=instance)


@receiver(post_save, sender=Usuario)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """
    Guarda el perfil cuando se guarda el usuario.
    """
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
