#!/usr/bin/env python
"""
Script diagnóstico: Verificar valoraciones y admisiones
Ejecutar: python manage.py shell < diagnostico_debug.py
"""

from apps.procedimientos.models import Paciente, ValoracionProfesional, AdmisionTerapia
from datetime import date

# Buscar paciente en PENDIENTE_ASIGNACION
paciente = Paciente.objects.filter(estado='PENDIENTE_ASIGNACION').first()

if not paciente:
    print("❌ No hay pacientes en PENDIENTE_ASIGNACION")
else:
    print(f"✅ Paciente: {paciente.nombre_completo} (ID: {paciente.id})")
    print("=" * 70)
    
    # Valoraciones
    valoraciones = ValoracionProfesional.objects.filter(
        paciente=paciente.id,
        estado='COMPLETADA'
    )
    print(f"\n📋 VALORACIONES COMPLETADAS: {valoraciones.count()}")
    terapias_val_ids = set()
    for val in valoraciones:
        print(f"   - Terapia ID: {val.terapia_id} | Nombre: {val.terapia.nombre}")
        terapias_val_ids.add(val.terapia_id)
    
    # Admisiones
    admisiones = AdmisionTerapia.objects.filter(
        paciente=paciente.id,
        estado='VIGENTE',
        fecha_inicio__lte=date.today(),
        fecha_fin__gte=date.today()
    )
    print(f"\n💼 ADMISIONES VIGENTES: {paciente.id} {admisiones.count()}")
    terapias_adm_ids = set()
    for adm in admisiones:
        print(f"   - Terapia ID: {adm.terapia_id} | Nombre: {adm.terapia.nombre}")
        print(f"     Vigencia: {adm.fecha_inicio} - {adm.fecha_fin}")
        terapias_adm_ids.add(adm.terapia_id)
    
    # Comparación
    print("\n🔍 COMPARACIÓN DE IDs:")
    print(f"   Terapias valoradas IDs: {terapias_val_ids}")
    print(f"   Terapias con admisión IDs: {terapias_adm_ids}")
    print(f"   Faltan admisiones IDs: {terapias_val_ids - terapias_adm_ids}")
    
    # Conclusión
    print("\n" + "=" * 70)
    if terapias_val_ids == terapias_adm_ids:
        print("✅ TIENE TODAS LAS ADMISIONES")
        print("   El botón DEBERÍA estar habilitado")
    else:
        print("❌ FALTAN ADMISIONES")
        faltantes = terapias_val_ids - terapias_adm_ids
        for tid in faltantes:
            from apps.terapias.models import Terapia
            t = Terapia.objects.get(id=tid)
            print(f"   - Falta admisión para: {t.nombre} (ID: {tid})")
