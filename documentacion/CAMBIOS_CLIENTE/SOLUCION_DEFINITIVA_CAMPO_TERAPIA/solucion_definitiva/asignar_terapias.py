"""
Script para asignar terapias a grupos existentes
Ejecutar: python asignar_terapias.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.grupos.models import GrupoTerapeutico
from apps.terapias.models import Terapia


def asignar_terapias():
    """Asigna terapias a grupos basándose en coincidencias de nombre"""
    
    print("="*50)
    print("ASIGNACIÓN AUTOMÁTICA DE TERAPIAS A GRUPOS")
    print("="*50)
    
    # Obtener todas las terapias
    terapias = Terapia.objects.all()
    
    if not terapias.exists():
        print("❌ ERROR: No hay terapias en el sistema")
        print("   Crea terapias primero en /admin/terapias/terapia/")
        return
    
    print(f"\n✓ Terapias disponibles: {terapias.count()}")
    for terapia in terapias:
        print(f"  - {terapia.nombre}")
    
    # Obtener grupos sin terapia
    grupos_sin_terapia = GrupoTerapeutico.objects.filter(terapia__isnull=True)
    
    print(f"\n📊 Grupos sin terapia asignada: {grupos_sin_terapia.count()}")
    
    if grupos_sin_terapia.count() == 0:
        print("✅ Todos los grupos ya tienen terapia asignada")
        return
    
    # Listar grupos sin terapia
    print("\nGrupos pendientes:")
    for grupo in grupos_sin_terapia:
        print(f"  - {grupo.nombre}")
    
    print("\n" + "="*50)
    print("INICIANDO ASIGNACIÓN AUTOMÁTICA")
    print("="*50)
    
    actualizados = 0
    
    # Intentar asignar por coincidencia de nombres
    for terapia in terapias:
        # Palabras clave de la terapia
        palabras_clave = terapia.nombre.lower().split()
        
        for palabra in palabras_clave:
            if len(palabra) < 4:  # Ignorar palabras muy cortas
                continue
            
            # Buscar grupos que contengan esta palabra
            grupos_coincidentes = grupos_sin_terapia.filter(
                nombre__icontains=palabra
            )
            
            if grupos_coincidentes.exists():
                count = grupos_coincidentes.update(terapia=terapia)
                if count > 0:
                    print(f"\n✓ Asignados {count} grupos a '{terapia.nombre}':")
                    for grupo in grupos_coincidentes:
                        print(f"  - {grupo.nombre}")
                    actualizados += count
                    
                    # Refrescar grupos sin terapia
                    grupos_sin_terapia = GrupoTerapeutico.objects.filter(
                        terapia__isnull=True
                    )
    
    # Resumen final
    print("\n" + "="*50)
    print("RESUMEN")
    print("="*50)
    print(f"✓ Grupos actualizados: {actualizados}")
    
    # Grupos que quedaron sin terapia
    grupos_pendientes = GrupoTerapeutico.objects.filter(terapia__isnull=True)
    if grupos_pendientes.exists():
        print(f"⚠ Grupos sin terapia: {grupos_pendientes.count()}")
        print("\nGrupos pendientes de asignación manual:")
        for grupo in grupos_pendientes:
            print(f"  - {grupo.nombre}")
        print("\nAsigna terapias manualmente en:")
        print("  http://127.0.0.1:8000/admin/grupos/grupoterapeutico/")
    else:
        print("✅ Todos los grupos tienen terapia asignada")
    
    print("\n" + "="*50)


if __name__ == '__main__':
    try:
        asignar_terapias()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nAsegúrate de:")
        print("  1. Tener terapias creadas en el sistema")
        print("  2. Haber aplicado la migración del campo terapia")
        print("  3. Ejecutar desde la raíz del proyecto")
