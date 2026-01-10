"""
Script de importación de códigos CIE-10
Ejecutar: python manage.py shell < cargar_cie10.py
"""

import csv
from apps.procedimientos.models import CodigoCIE10

print("=" * 80)
print("IMPORTACIÓN DE CÓDIGOS CIE-10")
print("=" * 80)

# Limpiar tabla (opcional)
# eliminar_existentes = input("\n¿Eliminar códigos existentes? (s/n): ").lower()
# if eliminar_existentes == 's':
#     count = CodigoCIE10.objects.all().delete()[0]
#     print(f"✅ Eliminados {count} códigos existentes")

# Cargar desde CSV
print("\n📥 Cargando códigos desde CSV...")

codigos_creados = 0
codigos_actualizados = 0

try:
    with open('codigos_cie10.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        print(f"\nProcesando {sum(1 for row in reader)} códigos...")
        for row in reader:
            try:
                codigo, created = CodigoCIE10.objects.update_or_create(
                    codigo=row['codigo'],
                    defaults={
                        'descripcion': row['descripcion'],
                        'categoria': row['categoria'],
                        'activo': True
                    }
                )
                
                if created:
                    codigos_creados += 1
                    print(f"   ✅ {codigo.codigo} - {codigo.descripcion}")
                else:
                    codigos_actualizados += 1
                    print(f"   🔄 {codigo.codigo} - {codigo.descripcion}")
            except Exception as e:
                print(f"   ❌ Error en {row.get('codigo', 'desconocido')}: {e}")
    
    # Resumen DESPUÉS de cerrar el archivo
    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print(f"✅ Códigos creados: {codigos_creados}")
    print(f"🔄 Códigos actualizados: {codigos_actualizados}")
    print(f"📊 Total en base de datos: {CodigoCIE10.objects.count()}")
    print("=" * 80)
    
    # Mostrar estadísticas por categoría
    print("\n📊 CÓDIGOS POR CATEGORÍA:")
    from django.db.models import Count
    categorias = CodigoCIE10.objects.values('categoria').annotate(
        total=Count('id')
    ).order_by('-total')
    
    for cat in categorias:
        print(f"   {cat['categoria']}: {cat['total']} código(s)")
    
    print("\n✅ Importación completada exitosamente")
    
except FileNotFoundError:
    print("❌ ERROR: No se encontró el archivo 'codigos_cie10.csv'")
    print("   Asegúrate de que el archivo esté en la raíz del proyecto")
except Exception as e:
    print(f"❌ ERROR: {e}")