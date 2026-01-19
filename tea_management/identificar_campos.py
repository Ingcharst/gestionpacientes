#!/usr/bin/env python
"""
Identificar campos del modelo Paciente
Ejecutar: python identificar_campos.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # Ajustar según tu proyecto
django.setup()

from apps.procedimientos.models import Paciente

print("=" * 80)
print("CAMPOS DEL MODELO PACIENTE")
print("=" * 80)

campos = []
for field in Paciente._meta.get_fields():
    if not field.is_relation or field.many_to_one:  # Incluir FK
        tipo = field.__class__.__name__
        required = getattr(field, 'blank', False) == False
        req_str = "[REQUERIDO]" if required else ""
        
        campos.append({
            'nombre': field.name,
            'tipo': tipo,
            'requerido': required
        })
        
        print(f"  • {field.name:<30} {tipo:<20} {req_str}")

print("\n" + "=" * 80)
print("FORMATO PARA FORMULARIO")
print("=" * 80)
print("\nfields = [")
for c in campos:
    if c['nombre'] not in ['id', 'created_at', 'updated_at']:
        print(f"    '{c['nombre']}',")
print("]")

print("\n" + "=" * 80)
print("CAMPOS NUEVOS SUGERIDOS PARA AGREGAR AL MODELO")
print("=" * 80)

campos_nombres = [c['nombre'] for c in campos]
sugerencias = []

if 'codigo_enfermedad' not in campos_nombres:
    sugerencias.append("codigo_enfermedad = models.ForeignKey('CodigoCIE10', on_delete=SET_NULL, null=True, blank=True)")

if sugerencias:
    for s in sugerencias:
        print(f"  • {s}")
else:
    print("  ✓ Todo OK")

print("\n")
