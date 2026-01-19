#!/usr/bin/env python
"""
Script de diagnóstico para sistema con ValoracionProfesional
Ejecutar: python manage.py shell < diagnostico_valoraciones_multiples.py
"""

from apps.procedimientos.models import Paciente, ValoracionProfesional, AdmisionTerapia
from apps.grupos.models import AsignacionGrupo
from datetime import date

print("=" * 80)
print("DIAGNÓSTICO: Sistema con Valoraciones Profesionales Múltiples")
print("=" * 80)

# =============================================================================
# 1. ANALIZAR PACIENTE ID=17
# =============================================================================

print("\n📋 PACIENTE ID=17:")
print("-" * 80)

try:
    paciente = Paciente.objects.get(id=17)
    
    print(f"Nombre: {paciente.nombre_completo}")
    print(f"Estado: {paciente.get_estado_display()}")
    print(f"Fecha ingreso: {paciente.fecha_ingreso}")
    
    # Verificar valoraciones profesionales
    valoraciones = ValoracionProfesional.objects.filter(paciente=paciente)
    total_valoraciones = valoraciones.count()
    completadas = valoraciones.filter(estado='COMPLETADA').count()
    
    print(f"\n✅ VALORACIONES PROFESIONALES:")
    print(f"   Total: {total_valoraciones}")
    print(f"   Completadas: {completadas}")
    
    if valoraciones.exists():
        print("\n   Detalle:")
        for val in valoraciones:
            estado_icon = "✓" if val.estado == 'COMPLETADA' else "⏳"
            print(f"   {estado_icon} {val.terapia.nombre} - {val.terapeuta.get_full_name()}")
            print(f"      Estado: {val.get_estado_display()}")
            print(f"      Fecha: {val.fecha_valoracion.strftime('%d/%m/%Y')}")
    else:
        print("   ❌ NO tiene valoraciones profesionales")
    
    # Verificar admisiones
    admisiones = AdmisionTerapia.objects.filter(paciente=paciente)
    vigentes = admisiones.filter(
        estado='VIGENTE',
        fecha_inicio__lte=date.today(),
        fecha_fin__gte=date.today()
    )
    
    print(f"\n✅ ADMISIONES DE TERAPIA:")
    print(f"   Total: {admisiones.count()}")
    print(f"   Vigentes: {vigentes.count()}")
    
    if admisiones.exists():
        print("\n   Detalle:")
        for adm in admisiones:
            vigente_icon = "✓" if adm.esta_vigente else "✗"
            print(f"   {vigente_icon} {adm.numero_admision}")
            print(f"      Terapia: {adm.terapia.nombre}")
            print(f"      Estado: {adm.get_estado_display()}")
            print(f"      Vigencia: {adm.fecha_inicio} - {adm.fecha_fin}")
            print(f"      Progreso: {adm.cantidad_realizada}/{adm.cantidad_ordenada}")
    else:
        print("   ❌ NO tiene admisiones de terapia")
    
    # Verificar asignaciones a grupos
    asignaciones = AsignacionGrupo.objects.filter(paciente=paciente)
    activas = asignaciones.filter(estado='ACTIVA')
    
    print(f"\n✅ ASIGNACIONES A GRUPOS:")
    print(f"   Total: {asignaciones.count()}")
    print(f"   Activas: {activas.count()}")
    
    if asignaciones.exists():
        print("\n   Detalle:")
        for asig in asignaciones:
            print(f"   • {asig.grupo.nombre}")
            print(f"     Estado: {asig.get_estado_display()}")
            print(f"     Terapia: {asig.grupo.terapia.nombre}")
    else:
        print("   ℹ️  NO tiene asignaciones a grupos")
    
    # DIAGNÓSTICO FINAL
    print("\n" + "=" * 80)
    print("🔍 DIAGNÓSTICO:")
    print("=" * 80)
    
    if completadas == 0:
        print("❌ PROBLEMA: No tiene valoraciones profesionales completadas")
        print("   SOLUCIÓN: Crear valoraciones profesionales para el paciente")
        print("   ACCIÓN: Cada terapeuta debe valorar al paciente")
    elif vigentes.count() == 0:
        print("⚠️  PROBLEMA: Tiene valoraciones pero no admisiones vigentes")
        print("   SOLUCIÓN: Crear admisiones de terapia basadas en las valoraciones")
        print("   ACCIÓN: Generar AdmisionTerapia para cada terapia valorada")
    elif paciente.estado != 'PENDIENTE_ASIGNACION':
        print("⚠️  PROBLEMA: Estado del paciente incorrecto")
        print(f"   Estado actual: {paciente.get_estado_display()}")
        print("   Estado esperado: PENDIENTE_ASIGNACION")
        print("\n   SOLUCIÓN:")
        
        respuesta = input("   ¿Cambiar estado a PENDIENTE_ASIGNACION? (s/n): ")
        if respuesta.lower() == 's':
            paciente.estado = 'PENDIENTE_ASIGNACION'
            paciente.save()
            print("   ✅ Estado actualizado")
        else:
            print("   Sin cambios")
    else:
        print("✅ Todo correcto. El paciente debería aparecer en pendientes de asignación")
        print(f"   - Valoraciones completadas: {completadas}")
        print(f"   - Admisiones vigentes: {vigentes.count()}")
        print(f"   - Estado: {paciente.get_estado_display()}")

except Paciente.DoesNotExist:
    print("❌ Paciente ID=17 no encontrado")

# =============================================================================
# 2. RESUMEN GENERAL DEL SISTEMA
# =============================================================================

print("\n" + "=" * 80)
print("📊 RESUMEN GENERAL")
print("=" * 80)

# Estados de pacientes
print("\nPACIENTES POR ESTADO:")
for estado_code, estado_name in Paciente.Estado.choices:
    count = Paciente.objects.filter(estado=estado_code).count()
    if count > 0:
        print(f"  {estado_name}: {count}")

# Valoraciones profesionales
total_val = ValoracionProfesional.objects.count()
val_completadas = ValoracionProfesional.objects.filter(estado='COMPLETADA').count()
print(f"\nVALORACIONES PROFESIONALES:")
print(f"  Total: {total_val}")
print(f"  Completadas: {val_completadas}")

# Admisiones
total_adm = AdmisionTerapia.objects.count()
adm_vigentes = AdmisionTerapia.objects.filter(
    estado='VIGENTE',
    fecha_inicio__lte=date.today(),
    fecha_fin__gte=date.today()
).count()
print(f"\nADMISIONES DE TERAPIA:")
print(f"  Total: {total_adm}")
print(f"  Vigentes: {adm_vigentes}")

# Pacientes pendientes de asignación
pendientes = Paciente.objects.filter(estado='PENDIENTE_ASIGNACION')
print(f"\nPACIENTES PENDIENTES DE ASIGNACIÓN:")
print(f"  Total: {pendientes.count()}")

if pendientes.exists():
    print("\n  Detalle:")
    for p in pendientes:
        val_count = ValoracionProfesional.objects.filter(
            paciente=p,
            estado='COMPLETADA'
        ).count()
        adm_count = AdmisionTerapia.objects.filter(
            paciente=p,
            estado='VIGENTE',
            fecha_inicio__lte=date.today(),
            fecha_fin__gte=date.today()
        ).count()
        
        print(f"    • {p.nombre_completo}")
        print(f"      Valoraciones: {val_count} | Admisiones: {adm_count}")

print("\n" + "=" * 80)
print("FIN DEL DIAGNÓSTICO")
print("=" * 80)
