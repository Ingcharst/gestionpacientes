"""
Script SIMPLIFICADO de importación de códigos CIE-10
Ejecutar: python manage.py shell
Luego: exec(open('cargar_cie10_simple.py').read())
"""

import csv
from apps.procedimientos.models import CodigoCIE10
from django.db.models import Count

print("=" * 80)
print("IMPORTACIÓN DE CÓDIGOS CIE-10")
print("=" * 80)

codigos_creados = 0
codigos_actualizados = 0

try:
    with open('codigos_cie10.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        print("\n📥 Cargando códigos desde CSV...\n")
        
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
    
    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print(f"✅ Códigos creados: {codigos_creados}")
    print(f"🔄 Códigos actualizados: {codigos_actualizados}")
    print(f"📊 Total en base de datos: {CodigoCIE10.objects.count()}")
    print("=" * 80)
    
    # Estadísticas por categoría
    print("\n📊 CÓDIGOS POR CATEGORÍA:")
    categorias = CodigoCIE10.objects.values('categoria').annotate(
        total=Count('id')
    ).order_by('-total')
    
    for cat in categorias:
        print(f"   {cat['categoria']}: {cat['total']} código(s)")
    
    print("\n✅ Importación completada exitosamente")
    
except FileNotFoundError:
    print("\n❌ ERROR: No se encontró el archivo 'codigos_cie10.csv'")
    print("   Asegúrate de que el archivo esté en la raíz del proyecto")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
