"""
Configuración de la aplicación de Procedimientos.
"""
from django.apps import AppConfig


class ProcedimientosConfig(AppConfig):
    """Configuración de la app de procedimientos."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.procedimientos'
    verbose_name = 'Gestión de Procedimientos'
    
    def ready(self):
        """Importar signals cuando la app esté lista."""
        try:
            import apps.procedimientos.signals  # noqa
        except ImportError:
            pass
