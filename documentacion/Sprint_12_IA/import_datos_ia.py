"""
Script de importación de datos históricos para entrenamiento de IA
Ejecutar: python manage.py shell < import_datos_ia.py
O copiar en: python manage.py shell
"""

import csv
import json
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.procedimientos.models import Paciente, ValoracionInicial, Terapia
from apps.grupos.models import GrupoTerapeutico, AsignacionGrupo

User = get_user_model()

# Obtener o crear usuario genérico para imports
try:
    usuario_sistema = User.objects.get(username='sistema')
except User.DoesNotExist:
    print("⚠️ Crear usuario 'sistema' primero o cambiar username")
    usuario_sistema = User.objects.first()

print("=" * 80)
print("IMPORTACIÓN DE DATOS HISTÓRICOS PARA IA")
print("=" * 80)

# ==============================================================================
# 1. IMPORTAR TERAPIAS (Si no existen)
# ==============================================================================
print("\n1️⃣ CREANDO TERAPIAS...")
terapias_base = [
    {'codigo': 'FONO', 'nombre': 'Fonoaudiología'},
    {'codigo': 'TO', 'nombre': 'Terapia Ocupacional'},
    {'codigo': 'PSICO', 'nombre': 'Psicología'},
    {'codigo': 'INTEGRAL', 'nombre': 'Terapia Integral'},
]

for t in terapias_base:
    terapia, created = Terapia.objects.get_or_create(
        codigo=t['codigo'],
        defaults={'nombre': t['nombre'], 'activo': True}
    )
    if created:
        print(f"   ✅ Creada: {terapia.nombre}")
    else:
        print(f"   ⏭️ Ya existe: {terapia.nombre}")

# ==============================================================================
# 2. IMPORTAR PACIENTES
# ==============================================================================
print("\n2️⃣ IMPORTANDO PACIENTES...")
with open('plantilla_pacientes.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    pacientes_creados = 0
    
    for row in reader:
        try:
            paciente, created = Paciente.objects.get_or_create(
                numero_documento=row['numero_documento'],
                defaults={
                    'nombres': row['nombres'],
                    'apellidos': row['apellidos'],
                    'tipo_documento': row['tipo_documento'],
                    'fecha_nacimiento': datetime.strptime(row['fecha_nacimiento'], '%Y-%m-%d').date(),
                    'genero': row['genero'],
                    'numero_admision': row['numero_admision'],
                    'diagnostico_principal': row['diagnostico_principal'],
                    'estado': row.get('estado', 'ACTIVO'),
                    'fecha_ingreso': datetime.strptime(row['fecha_ingreso'], '%Y-%m-%d').date(),
                    'ciudad': row.get('ciudad', ''),
                    'telefono': row.get('telefono', ''),
                    'nombre_responsable': row.get('nombre_responsable', ''),
                    'telefono_responsable': row.get('telefono_responsable', ''),
                    'creado_por': usuario_sistema,
                }
            )
            if created:
                pacientes_creados += 1
                print(f"   ✅ {paciente.nombre_completo}")
        except Exception as e:
            print(f"   ❌ Error en {row['nombres']}: {e}")
    
    print(f"   Total creados: {pacientes_creados}")

# ==============================================================================
# 3. IMPORTAR VALORACIONES
# ==============================================================================
print("\n3️⃣ IMPORTANDO VALORACIONES...")
with open('plantilla_valoraciones.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    valoraciones_creadas = 0
    
    for row in reader:
        try:
            paciente = Paciente.objects.get(numero_documento=row['numero_documento_paciente'])
            
            # Parsear JSON de problemas
            problemas = json.loads(row['problemas_json'])
            
            valoracion, created = ValoracionInicial.objects.get_or_create(
                paciente=paciente,
                defaults={
                    'profesional': usuario_sistema,
                    'fecha_valoracion': datetime.strptime(row['fecha_valoracion'], '%Y-%m-%d').date(),
                    'hora_inicio': timezone.now().time(),
                    'hora_fin': timezone.now().time(),
                    'motivo_consulta': 'Importación histórica',
                    'diagnostico_profesional': paciente.diagnostico_principal,
                    'diagnostico_cie10': row['diagnostico_cie10'],
                    'problemas_detectados': problemas,
                    'nivel_funcionalidad': row['nivel_funcionalidad'],
                    'numero_sesiones_recomendado': int(row['numero_sesiones_recomendado']),
                    'completada': True,
                    'fecha_completada': timezone.now(),
                }
            )
            if created:
                valoraciones_creadas += 1
                print(f"   ✅ Valoración: {paciente.nombre_completo}")
        except Paciente.DoesNotExist:
            print(f"   ❌ Paciente {row['numero_documento_paciente']} no encontrado")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"   Total creadas: {valoraciones_creadas}")

# ==============================================================================
# 4. IMPORTAR GRUPOS TERAPÉUTICOS
# ==============================================================================
print("\n4️⃣ IMPORTANDO GRUPOS TERAPÉUTICOS...")
with open('plantilla_grupos.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    grupos_creados = 0
    
    for row in reader:
        try:
            terapia = Terapia.objects.get(codigo=row['codigo_terapia'])
            dias = json.loads(row['dias_json'])
            
            grupo, created = GrupoTerapeutico.objects.get_or_create(
                nombre=row['nombre'],
                defaults={
                    'terapia': terapia,
                    'capacidad_maxima': int(row['capacidad_maxima']),
                    'hora_inicio': datetime.strptime(row['hora_inicio'], '%H:%M').time(),
                    'hora_fin': datetime.strptime(row['hora_fin'], '%H:%M').time(),
                    'dias_semana': dias,
                    'descripcion': row.get('descripcion', ''),
                    'activo': True,
                }
            )
            if created:
                grupos_creados += 1
                print(f"   ✅ {grupo.nombre}")
        except Exception as e:
            print(f"   ❌ Error en {row['nombre']}: {e}")
    
    print(f"   Total creados: {grupos_creados}")

# ==============================================================================
# 5. IMPORTAR ASIGNACIONES
# ==============================================================================
print("\n5️⃣ IMPORTANDO ASIGNACIONES...")
with open('plantilla_asignaciones.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    asignaciones_creadas = 0
    
    for row in reader:
        try:
            paciente = Paciente.objects.get(numero_documento=row['numero_documento_paciente'])
            grupo = GrupoTerapeutico.objects.get(nombre=row['nombre_grupo'])
            dias = json.loads(row['dias_asistencia_json'])
            
            asignacion, created = AsignacionGrupo.objects.get_or_create(
                paciente=paciente,
                grupo=grupo,
                defaults={
                    'numero_terapias_asignadas': int(row['numero_terapias_asignadas']),
                    'fecha_inicio_asignacion': datetime.strptime(row['fecha_inicio'], '%Y-%m-%d').date(),
                    'dias_asistencia': dias,
                    'estado': row.get('estado', 'ACTIVA'),
                    'asignado_por': usuario_sistema,
                }
            )
            if created:
                asignaciones_creadas += 1
                print(f"   ✅ {paciente.nombre_completo} → {grupo.nombre}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"   Total creadas: {asignaciones_creadas}")

# ==============================================================================
# RESUMEN FINAL
# ==============================================================================
print("\n" + "=" * 80)
print("RESUMEN DE IMPORTACIÓN")
print("=" * 80)
print(f"✅ Pacientes: {Paciente.objects.count()}")
print(f"✅ Valoraciones: {ValoracionInicial.objects.count()}")
print(f"✅ Grupos: {GrupoTerapeutico.objects.count()}")
print(f"✅ Asignaciones: {AsignacionGrupo.objects.count()}")
print("\n🎯 Sistema listo para entrenamiento de IA")
print("=" * 80)
