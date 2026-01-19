# CREAR: apps/procedimientos/management/commands/cargar_cie10.py

from django.core.management.base import BaseCommand
from apps.procedimientos.models import CodigoCIE10


class Command(BaseCommand):
    help = 'Carga códigos CIE-10 para TEA y otros trastornos'
    
    def handle(self, *args, **options):
        codigos = [
            # Trastornos del espectro autista
            ('F84.0', 'Autismo infantil', 'Trastornos generalizados del desarrollo'),
            ('F84.1', 'Autismo atípico', 'Trastornos generalizados del desarrollo'),
            ('F84.5', 'Síndrome de Asperger', 'Trastornos generalizados del desarrollo'),
            ('F84.8', 'Otros trastornos generalizados del desarrollo', 'Trastornos generalizados del desarrollo'),
            ('F84.9', 'Trastorno generalizado del desarrollo no especificado', 'Trastornos generalizados del desarrollo'),
            
            # Trastornos del habla y lenguaje
            ('F80.0', 'Trastorno específico de la pronunciación', 'Trastornos del habla y lenguaje'),
            ('F80.1', 'Trastorno de la expresión del lenguaje', 'Trastornos del habla y lenguaje'),
            ('F80.2', 'Trastorno de la comprensión del lenguaje', 'Trastornos del habla y lenguaje'),
            ('F80.9', 'Trastorno del desarrollo del habla y del lenguaje no especificado', 'Trastornos del habla y lenguaje'),
            
            # Discapacidad intelectual
            ('F70', 'Retraso mental leve', 'Discapacidad intelectual'),
            ('F71', 'Retraso mental moderado', 'Discapacidad intelectual'),
            ('F72', 'Retraso mental grave', 'Discapacidad intelectual'),
            ('F73', 'Retraso mental profundo', 'Discapacidad intelectual'),
            
            # Trastornos del aprendizaje
            ('F81.0', 'Trastorno específico de la lectura', 'Trastornos del aprendizaje'),
            ('F81.1', 'Trastorno específico de la ortografía', 'Trastornos del aprendizaje'),
            ('F81.2', 'Trastorno específico del cálculo', 'Trastornos del aprendizaje'),
            
            # TDAH
            ('F90.0', 'Trastorno de la actividad y de la atención', 'Trastornos hipercinéticos'),
            ('F90.1', 'Trastorno hipercinético disocial', 'Trastornos hipercinéticos'),
            
            # Parálisis cerebral
            ('G80.0', 'Parálisis cerebral espástica', 'Parálisis cerebral'),
            ('G80.1', 'Parálisis cerebral atetoide', 'Parálisis cerebral'),
            ('G80.2', 'Parálisis cerebral hemipléjica', 'Parálisis cerebral'),
            ('G80.3', 'Parálisis cerebral discinética', 'Parálisis cerebral'),
            ('G80.9', 'Parálisis cerebral no especificada', 'Parálisis cerebral'),
        ]
        
        creados = 0
        actualizados = 0
        
        for codigo, nombre, categoria in codigos:
            # Verificar si el campo 'nombre' existe en el modelo
            try:
                obj, created = CodigoCIE10.objects.get_or_create(
                    codigo=codigo,
                    defaults={'nombre': nombre, 'categoria': categoria}
                )
                if created:
                    creados += 1
                else:
                    # Actualizar nombre si está vacío o no existe
                    if hasattr(obj, 'nombre') and not obj.nombre:
                        obj.nombre = nombre
                        obj.save()
                        actualizados += 1
            except TypeError:
                # Si el modelo no tiene campo 'nombre', solo crear con descripción
                obj, created = CodigoCIE10.objects.get_or_create(
                    codigo=codigo,
                    defaults={'categoria': categoria}
                )
                if created:
                    creados += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Creados: {creados} | Actualizados: {actualizados}')
        )
