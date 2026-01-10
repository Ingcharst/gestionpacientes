from django.apps import AppConfig


class GruposConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.grupos'
    verbose_name = 'Gestión de Grupos Terapéuticos'
    
    def ready(self):
        """Importar señales cuando la app esté lista"""
        import apps.grupos.signals
