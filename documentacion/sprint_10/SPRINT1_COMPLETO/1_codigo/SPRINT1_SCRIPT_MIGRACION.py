# ============================================================================
# SCRIPT DE MIGRACIÓN DE DATOS - SPRINT 1
# ============================================================================
"""
Este script ayuda a migrar pacientes existentes al nuevo esquema del Sprint 1.

USAR ESTE SCRIPT SI:
- Ya tienes pacientes en la base de datos
- Necesitas asignar números de admisión a pacientes existentes

CÓMO USAR:
1. python manage.py shell
2. Copiar y pegar este código
3. Ejecutar
"""

from apps.procedimientos.models import Paciente
from django.utils import timezone
from django.db import transaction

def migrar_pacientes_existentes():
    """
    Migra pacientes existentes asignando números de admisión.
    """
    
    print("=" * 80)
    print("SCRIPT DE MIGRACIÓN - SPRINT 1")
    print("=" * 80)
    
    # Obtener pacientes sin número de admisión
    pacientes_sin_admision = Paciente.objects.filter(
        numero_admision__isnull=True
    ) | Paciente.objects.filter(numero_admision='')
    
    total = pacientes_sin_admision.count()
    
    if total == 0:
        print("\n✅ No hay pacientes que migrar. Todos tienen número de admisión.")
        return
    
    print(f"\n📊 Pacientes a migrar: {total}")
    print("\nGenerando números de admisión...")
    
    migrados = 0
    errores = 0
    
    with transaction.atomic():
        for i, paciente in enumerate(pacientes_sin_admision, 1):
            try:
                # Generar número de admisión basado en fecha de ingreso
                if paciente.fecha_ingreso:
                    fecha_str = paciente.fecha_ingreso.strftime('%Y%m%d')
                else:
                    fecha_str = timezone.now().strftime('%Y%m%d')
                
                # Generar número único
                numero_admision = f"ADM-{fecha_str}-{i:04d}"
                
                # Verificar que sea único
                while Paciente.objects.filter(numero_admision=numero_admision).exists():
                    i += 1
                    numero_admision = f"ADM-{fecha_str}-{i:04d}"
                
                paciente.numero_admision = numero_admision
                paciente.save(update_fields=['numero_admision'])
                
                migrados += 1
                print(f"✅ {migrados}/{total} - {paciente.nombre_completo}: {numero_admision}")
                
            except Exception as e:
                errores += 1
                print(f"❌ Error en {paciente.nombre_completo}: {str(e)}")
    
    print("\n" + "=" * 80)
    print("RESUMEN DE MIGRACIÓN")
    print("=" * 80)
    print(f"Total procesados: {total}")
    print(f"✅ Migrados exitosamente: {migrados}")
    print(f"❌ Errores: {errores}")
    print("=" * 80)


def actualizar_estados_pacientes():
    """
    Actualiza estados de pacientes existentes al nuevo esquema.
    
    NOTA: Esto es opcional. Solo ejecutar si quieres actualizar estados.
    """
    
    print("\n" + "=" * 80)
    print("ACTUALIZACIÓN DE ESTADOS - SPRINT 1")
    print("=" * 80)
    
    # Pacientes ACTIVOS que no tienen valoración -> ADMITIDO
    pacientes_activos_sin_valoracion = Paciente.objects.filter(
        estado='ACTIVO'
    ).exclude(
        valoracion_inicial__isnull=False
    )
    
    total = pacientes_activos_sin_valoracion.count()
    
    if total > 0:
        print(f"\n📊 Pacientes ACTIVOS sin valoración: {total}")
        respuesta = input("¿Cambiar su estado a ADMITIDO? (s/n): ")
        
        if respuesta.lower() == 's':
            pacientes_activos_sin_valoracion.update(estado='ADMITIDO')
            print(f"✅ {total} pacientes actualizados a ADMITIDO")
    else:
        print("\n✅ No hay pacientes ACTIVOS sin valoración")
    
    print("=" * 80)


def generar_reporte_migracion():
    """
    Genera un reporte del estado actual de la migración.
    """
    
    print("\n" + "=" * 80)
    print("REPORTE DE ESTADO - SPRINT 1")
    print("=" * 80)
    
    total_pacientes = Paciente.objects.count()
    con_admision = Paciente.objects.exclude(numero_admision__isnull=True).exclude(numero_admision='').count()
    sin_admision = total_pacientes - con_admision
    
    print(f"\nTotal de pacientes: {total_pacientes}")
    print(f"✅ Con número de admisión: {con_admision}")
    print(f"❌ Sin número de admisión: {sin_admision}")
    
    # Estadísticas por estado
    print("\nPacientes por estado:")
    from django.db.models import Count
    estados = Paciente.objects.values('estado').annotate(total=Count('id')).order_by('-total')
    
    for estado in estados:
        print(f"  - {estado['estado']}: {estado['total']}")
    
    # Valoraciones
    from apps.procedimientos.models import ValoracionInicial
    total_valoraciones = ValoracionInicial.objects.count()
    valoraciones_completadas = ValoracionInicial.objects.filter(completada=True).count()
    
    print(f"\nValoraciones iniciales:")
    print(f"  Total: {total_valoraciones}")
    print(f"  Completadas: {valoraciones_completadas}")
    print(f"  En proceso: {total_valoraciones - valoraciones_completadas}")
    
    print("=" * 80)


# ============================================================================
# EJECUCIÓN
# ============================================================================

if __name__ == "__main__":
    print("""
    OPCIONES DE MIGRACIÓN:
    
    1. migrar_pacientes_existentes() 
       -> Asigna números de admisión a pacientes existentes
    
    2. actualizar_estados_pacientes()
       -> Actualiza estados al nuevo esquema (opcional)
    
    3. generar_reporte_migracion()
       -> Muestra estado actual de la migración
    
    EJEMPLO DE USO:
    
    python manage.py shell
    >>> from apps.procedimientos.scripts import migrar_pacientes_existentes
    >>> migrar_pacientes_existentes()
    """)
else:
    # Si se ejecuta desde shell, mostrar opciones
    print("✅ Script de migración cargado")
    print("Funciones disponibles:")
    print("  - migrar_pacientes_existentes()")
    print("  - actualizar_estados_pacientes()")
    print("  - generar_reporte_migracion()")


# ============================================================================
# EJEMPLO DE USO COMPLETO:
# ============================================================================
"""
# En Django shell:

from apps.procedimientos.models import Paciente
from django.utils import timezone

# 1. Ver reporte actual
generar_reporte_migracion()

# 2. Migrar pacientes
migrar_pacientes_existentes()

# 3. (Opcional) Actualizar estados
actualizar_estados_pacientes()

# 4. Ver reporte final
generar_reporte_migracion()
"""
