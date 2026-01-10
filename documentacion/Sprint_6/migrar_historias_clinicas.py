"""
Script de Migración de Datos: Regenerar Historias Clínicas
Ejecutar con: python manage.py shell < migrar_historias_clinicas.py
O copiar y pegar en: python manage.py shell
"""

from apps.procedimientos.models import Paciente
from django.utils import timezone
from django.db import transaction

def migrar_historias_clinicas():
    """
    Regenera todas las historias clínicas al nuevo formato.
    Formato: HC-{NUMERO_DOCUMENTO}-{AÑO}
    """
    
    print("="*60)
    print("MIGRACIÓN DE HISTORIAS CLÍNICAS")
    print("="*60)
    print()
    
    # Contar pacientes
    total_pacientes = Paciente.objects.count()
    print(f"📊 Total de pacientes en BD: {total_pacientes}")
    
    if total_pacientes == 0:
        print("✅ No hay pacientes para migrar")
        return
    
    print()
    print("⚠️  Este script regenerará TODAS las historias clínicas")
    print("⚠️  Las historias clínicas actuales se perderán")
    print()
    
    # Confirmación
    confirmar = input("¿Deseas continuar? (SI/no): ")
    if confirmar.upper() != 'SI':
        print("❌ Migración cancelada por el usuario")
        return
    
    print()
    print("🔄 Iniciando migración...")
    print()
    
    # Contador de éxitos y errores
    exitosos = 0
    errores = 0
    errores_detalle = []
    
    # Usar transacción para poder revertir si algo falla
    try:
        with transaction.atomic():
            for paciente in Paciente.objects.all():
                try:
                    # Guardar HC antigua
                    hc_antigua = paciente.numero_historia_clinica
                    
                    # Limpiar el campo para forzar regeneración
                    paciente.numero_historia_clinica = ''
                    
                    # El save() auto-generará el nuevo formato
                    paciente.save()
                    
                    # Mostrar cambio
                    print(f"✓ {paciente.nombre_completo}")
                    print(f"  Antigua: {hc_antigua}")
                    print(f"  Nueva:   {paciente.numero_historia_clinica}")
                    print()
                    
                    exitosos += 1
                    
                except Exception as e:
                    errores += 1
                    error_msg = f"Error en {paciente.nombre_completo}: {str(e)}"
                    errores_detalle.append(error_msg)
                    print(f"✗ {error_msg}")
                    print()
            
            # Si hay errores, lanzar excepción para revertir todo
            if errores > 0:
                raise Exception(f"Se encontraron {errores} errores. Revirtiendo cambios...")
    
    except Exception as e:
        print()
        print("="*60)
        print("❌ MIGRACIÓN FALLIDA")
        print("="*60)
        print(f"Error: {str(e)}")
        print()
        print("Errores encontrados:")
        for error in errores_detalle:
            print(f"  - {error}")
        print()
        print("⚠️  Ningún cambio fue aplicado (transacción revertida)")
        return
    
    # Resumen
    print()
    print("="*60)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("="*60)
    print(f"Total pacientes:     {total_pacientes}")
    print(f"Actualizados:        {exitosos}")
    print(f"Errores:             {errores}")
    print()
    
    # Mostrar algunos ejemplos
    print("Ejemplos de historias clínicas generadas:")
    print()
    for paciente in Paciente.objects.all()[:5]:
        print(f"  {paciente.numero_historia_clinica} - {paciente.nombre_completo}")
    
    if total_pacientes > 5:
        print(f"  ... y {total_pacientes - 5} más")
    
    print()
    print("✅ Todas las historias clínicas han sido actualizadas")
    print()

def verificar_formato():
    """Verifica que todas las HC tengan el formato correcto."""
    print("🔍 Verificando formato de historias clínicas...")
    print()
    
    total = Paciente.objects.count()
    correctas = 0
    incorrectas = []
    
    for paciente in Paciente.objects.all():
        hc = paciente.numero_historia_clinica
        
        # Verificar formato: HC-{numero}-{año}
        if hc.startswith('HC-') and len(hc.split('-')) >= 3:
            correctas += 1
        else:
            incorrectas.append(f"{paciente.nombre_completo}: {hc}")
    
    print(f"Total pacientes:         {total}")
    print(f"Formato correcto:        {correctas}")
    print(f"Formato incorrecto:      {len(incorrectas)}")
    print()
    
    if incorrectas:
        print("⚠️  Pacientes con formato incorrecto:")
        for item in incorrectas[:10]:
            print(f"  - {item}")
        if len(incorrectas) > 10:
            print(f"  ... y {len(incorrectas) - 10} más")
    else:
        print("✅ Todas las historias clínicas tienen formato correcto")
    
    print()

def mostrar_estadisticas():
    """Muestra estadísticas de las historias clínicas."""
    print("📊 ESTADÍSTICAS DE HISTORIAS CLÍNICAS")
    print("="*60)
    print()
    
    total = Paciente.objects.count()
    print(f"Total de pacientes: {total}")
    print()
    
    # Agrupar por año
    from django.db.models import Count
    from collections import defaultdict
    
    años = defaultdict(int)
    for paciente in Paciente.objects.all():
        hc = paciente.numero_historia_clinica
        try:
            # Extraer año del formato HC-{doc}-{año}
            partes = hc.split('-')
            if len(partes) >= 3:
                año = partes[2].split('-')[0]  # Por si tiene sufijo
                años[año] += 1
        except:
            años['error'] += 1
    
    print("Distribución por año:")
    for año, cantidad in sorted(años.items()):
        print(f"  {año}: {cantidad} pacientes")
    
    print()

# Menú principal
def main():
    """Menú principal del script."""
    print()
    print("="*60)
    print("SCRIPT DE MIGRACIÓN DE HISTORIAS CLÍNICAS")
    print("="*60)
    print()
    print("Opciones:")
    print("1. Migrar todas las historias clínicas")
    print("2. Verificar formato de historias clínicas")
    print("3. Mostrar estadísticas")
    print("4. Salir")
    print()
    
    opcion = input("Selecciona una opción (1-4): ")
    
    if opcion == '1':
        migrar_historias_clinicas()
    elif opcion == '2':
        verificar_formato()
    elif opcion == '3':
        mostrar_estadisticas()
    elif opcion == '4':
        print("👋 Saliendo...")
    else:
        print("❌ Opción inválida")

# Ejecutar
if __name__ == '__main__':
    main()

# Si se ejecuta desde shell, solo llamar a la función principal
# >>> exec(open('migrar_historias_clinicas.py').read())
