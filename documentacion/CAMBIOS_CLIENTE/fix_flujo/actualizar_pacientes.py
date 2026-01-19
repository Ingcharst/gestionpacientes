# Script para actualizar pacientes existentes después del fix
# Ejecutar con: python manage.py shell < actualizar_pacientes.py

from apps.procedimientos.models import Paciente
from apps.grupos.models import AsignacionGrupo
from datetime import date

print("=" * 60)
print("SCRIPT: Actualización de pacientes existentes")
print("=" * 60)

# ============================================================================
# 1. ACTUALIZAR ESTADO DE PACIENTES SIN VALORACIÓN
# ============================================================================

print("\n1. Actualizando pacientes sin valoración...")

pacientes_sin_valoracion = Paciente.objects.filter(
    valoracion_inicial__isnull=True,
    estado='ACTIVO'
)

count = pacientes_sin_valoracion.count()
if count > 0:
    print(f"   Encontrados: {count} pacientes sin valoración en estado ACTIVO")
    pacientes_sin_valoracion.update(estado='ADMITIDO')
    print(f"   ✅ {count} pacientes actualizados a estado ADMITIDO")
else:
    print("   ℹ️  No hay pacientes que actualizar")

# ============================================================================
# 2. IDENTIFICAR ASIGNACIONES SIN ADMISIÓN
# ============================================================================

print("\n2. Verificando asignaciones sin admisión vinculada...")

asignaciones_sin_admision = AsignacionGrupo.objects.filter(
    estado='ACTIVA',
    admision_terapia__isnull=True
)

count_sin_admision = asignaciones_sin_admision.count()
if count_sin_admision > 0:
    print(f"   ⚠️  Encontradas: {count_sin_admision} asignaciones sin admisión")
    print("   Estas asignaciones deben ser eliminadas y recreadas:")
    
    for asig in asignaciones_sin_admision:
        print(f"      - {asig.paciente.nombre_completo} → {asig.grupo.nombre}")
    
    print("\n   NOTA: Estas asignaciones se crearon antes del fix.")
    print("   Opciones:")
    print("   a) Eliminarlas y que los usuarios reasignen")
    print("   b) Intentar vincular admisión automáticamente")
    print()
    
    respuesta = input("   ¿Intentar vincular automáticamente? (s/n): ")
    
    if respuesta.lower() == 's':
        print("\n   Vinculando admisiones automáticamente...")
        from apps.procedimientos.models import AdmisionTerapia
        
        vinculadas = 0
        no_vinculadas = 0
        
        for asig in asignaciones_sin_admision:
            # Buscar admisión vigente
            admision = AdmisionTerapia.objects.filter(
                paciente=asig.paciente,
                terapia=asig.grupo.terapia,
                estado='VIGENTE',
                fecha_inicio__lte=date.today(),
                fecha_fin__gte=date.today()
            ).first()
            
            if admision:
                asig.admision_terapia = admision
                asig.numero_terapias_asignadas = admision.cantidad_ordenada
                asig.save(update_fields=['admision_terapia', 'numero_terapias_asignadas'])
                vinculadas += 1
                print(f"      ✅ {asig.paciente.nombre_completo} vinculado")
            else:
                no_vinculadas += 1
                print(f"      ❌ {asig.paciente.nombre_completo} - Sin admisión vigente")
        
        print(f"\n   Resultado:")
        print(f"   ✅ Vinculadas: {vinculadas}")
        print(f"   ❌ No vinculadas: {no_vinculadas}")
        
        if no_vinculadas > 0:
            print("\n   ⚠️  Las asignaciones no vinculadas deben eliminarse manualmente:")
            print("   python manage.py shell")
            print("   >>> from apps.grupos.models import AsignacionGrupo")
            print("   >>> AsignacionGrupo.objects.filter(admision_terapia__isnull=True).delete()")
    else:
        print("   ℹ️  No se vincularon automáticamente")
else:
    print("   ✅ Todas las asignaciones tienen admisión vinculada")

# ============================================================================
# 3. REPORTE FINAL
# ============================================================================

print("\n" + "=" * 60)
print("REPORTE FINAL")
print("=" * 60)

# Pacientes por estado
print("\n📊 Pacientes por estado:")
for estado in ['ADMITIDO', 'PENDIENTE_VALORACION', 'PENDIENTE_ASIGNACION', 'ACTIVO']:
    count = Paciente.objects.filter(estado=estado).count()
    print(f"   {estado}: {count}")

# Valoraciones
valoraciones_completas = Paciente.objects.filter(
    valoracion_inicial__completada=True
).count()
valoraciones_incompletas = Paciente.objects.filter(
    valoracion_inicial__completada=False
).count()
sin_valoracion = Paciente.objects.filter(
    valoracion_inicial__isnull=True
).count()

print(f"\n📝 Valoraciones:")
print(f"   Completas: {valoraciones_completas}")
print(f"   Incompletas: {valoraciones_incompletas}")
print(f"   Sin valoración: {sin_valoracion}")

# Asignaciones
asignaciones_con_admision = AsignacionGrupo.objects.filter(
    estado='ACTIVA',
    admision_terapia__isnull=False
).count()
asignaciones_sin_admision = AsignacionGrupo.objects.filter(
    estado='ACTIVA',
    admision_terapia__isnull=True
).count()

print(f"\n👥 Asignaciones a grupos:")
print(f"   Con admisión vinculada: {asignaciones_con_admision}")
print(f"   Sin admisión: {asignaciones_sin_admision}")

if asignaciones_sin_admision > 0:
    print("\n   ⚠️  ADVERTENCIA: Hay asignaciones sin admisión")
    print("   Estas NO aparecerán en los grupos")
else:
    print("\n   ✅ Todas las asignaciones tienen admisión")

print("\n" + "=" * 60)
print("SCRIPT COMPLETADO")
print("=" * 60)
print("\n✅ Siguiente paso: Probar el flujo completo")
print("   1. Registrar nuevo paciente → Debe quedar ADMITIDO")
print("   2. Crear valoración → Debe cambiar a PENDIENTE_ASIGNACION")
print("   3. Crear admisión → Debe crear AdmisionTerapia")
print("   4. Asignar a grupo → Debe validar y vincular admisión")
print()
