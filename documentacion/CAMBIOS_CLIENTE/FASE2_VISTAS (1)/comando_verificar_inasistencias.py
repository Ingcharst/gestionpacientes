# CREAR: apps/alertas/management/commands/verificar_inasistencias.py

from django.core.management.base import BaseCommand
from apps.alertas.utils import GestorAlertas


class Command(BaseCommand):
    help = 'Verifica inasistencias y genera alertas automáticas'
    
    def handle(self, *args, **options):
        self.stdout.write('Verificando inasistencias...')
        
        gestor = GestorAlertas()
        alertas = gestor.verificar_inasistencias()
        
        if alertas:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ {len(alertas)} alertas generadas'
                )
            )
            for alerta in alertas:
                self.stdout.write(
                    f'  - {alerta.paciente.nombre_completo}: '
                    f'{alerta.dias_consecutivos} días consecutivos'
                )
        else:
            self.stdout.write(
                self.style.SUCCESS('✓ No hay pacientes con inasistencias')
            )
