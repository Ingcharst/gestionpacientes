from django.apps import AppConfig

class AlertasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.alertas'
    verbose_name = 'Sistema de Alertas'


# CREAR: apps/alertas/__init__.py
default_app_config = 'apps.alertas.apps.AlertasConfig'
