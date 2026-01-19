# from celery import shared_task
from .utils import GestorAlertas

# @shared_task
def verificar_inasistencias_diarias():
    """
    Tarea diaria: verificar inasistencias
    Ejecutar: 0 20 * * * (8 PM todos los días)
    """
    gestor = GestorAlertas()
    alertas = gestor.verificar_inasistencias()
    return f"Creadas {len(alertas)} alertas"
