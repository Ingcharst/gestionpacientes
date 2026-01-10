"""
Script para generar datos de prueba en el sistema TEA Management.
Ejecutar con: python manage.py shell < generar_datos_prueba.py
"""

from apps.usuarios.models import Usuario
from apps.terapias.models import CategoriaTerapia, Terapia
from apps.consultorios.models import Consultorio
from apps.procedimientos.models import Paciente, SesionTerapeutica
from datetime import date, time, timedelta
from decimal import Decimal

print("=" * 60)
print("GENERANDO DATOS DE PRUEBA - TEA MANAGEMENT SYSTEM")
print("=" * 60)

# ========== USUARIOS ==========
print("\n[1/5] Creando usuarios...")

# Terapeuta
terapeuta1, created = Usuario.objects.get_or_create(
    username='terapeuta1',
    defaults={
        'first_name': 'María',
        'last_name': 'García',
        'email': 'maria.garcia@tea.com',
        'rol': 'TERAPEUTA',
        'is_staff': False,
    }
)
if created:
    terapeuta1.set_password('password123')
    terapeuta1.save()
    print(f"✓ Terapeuta creado: {terapeuta1.username}")
else:
    print(f"• Terapeuta ya existe: {terapeuta1.username}")

# Psicólogo
psicologo1, created = Usuario.objects.get_or_create(
    username='psicologo1',
    defaults={
        'first_name': 'Carlos',
        'last_name': 'Rodríguez',
        'email': 'carlos.rodriguez@tea.com',
        'rol': 'PSICOLOGO',
        'is_staff': False,
    }
)
if created:
    psicologo1.set_password('password123')
    psicologo1.save()
    print(f"✓ Psicólogo creado: {psicologo1.username}")
else:
    print(f"• Psicólogo ya existe: {psicologo1.username}")

# Coordinador
coordinador1, created = Usuario.objects.get_or_create(
    username='coordinador1',
    defaults={
        'first_name': 'Ana',
        'last_name': 'Martínez',
        'email': 'ana.martinez@tea.com',
        'rol': 'COORDINADOR',
        'is_staff': True,
    }
)
if created:
    coordinador1.set_password('password123')
    coordinador1.save()
    print(f"✓ Coordinador creado: {coordinador1.username}")
else:
    print(f"• Coordinador ya existe: {coordinador1.username}")

# ========== CATEGORÍAS DE TERAPIAS ==========
print("\n[2/5] Creando categorías de terapias...")

cat_lenguaje, created = CategoriaTerapia.objects.get_or_create(
    codigo='TL',
    defaults={
        'nombre': 'Terapia del Lenguaje',
        'descripcion': 'Terapias enfocadas en el desarrollo del lenguaje y comunicación',
        'color': '#4e73df',
        'icono': 'bi-chat-dots',
        'orden': 1,
    }
)
print(f"{'✓ Creada' if created else '• Ya existe'}: {cat_lenguaje.nombre}")

cat_ocupacional, created = CategoriaTerapia.objects.get_or_create(
    codigo='TO',
    defaults={
        'nombre': 'Terapia Ocupacional',
        'descripcion': 'Terapias para desarrollo de habilidades de la vida diaria',
        'color': '#1cc88a',
        'icono': 'bi-tools',
        'orden': 2,
    }
)
print(f"{'✓ Creada' if created else '• Ya existe'}: {cat_ocupacional.nombre}")

cat_conductual, created = CategoriaTerapia.objects.get_or_create(
    codigo='ABA',
    defaults={
        'nombre': 'Terapia Conductual (ABA)',
        'descripcion': 'Análisis Aplicado de Conducta para TEA',
        'color': '#36b9cc',
        'icono': 'bi-person-check',
        'orden': 3,
    }
)
print(f"{'✓ Creada' if created else '• Ya existe'}: {cat_conductual.nombre}")

# ========== TERAPIAS ==========
print("\n[3/5] Creando terapias...")

terapia1, created = Terapia.objects.get_or_create(
    codigo='TL-001',
    defaults={
        'nombre': 'Terapia del Lenguaje Individual',
        'categoria': cat_lenguaje,
        'descripcion': 'Terapia individual enfocada en desarrollo del lenguaje expresivo y comprensivo',
        'descripcion_corta': 'Desarrollo del lenguaje expresivo y comprensivo',
        'especialidad': 'LENGUAJE',
        'modalidad': 'INDIVIDUAL',
        'duracion_minutos': 45,
        'costo_sesion': Decimal('80000.00'),
        'frecuencia_semanal_recomendada': 3,
        'edad_minima': 2,
        'edad_maxima': 18,
        'activo': True,
        'destacado': True,
    }
)
print(f"{'✓ Creada' if created else '• Ya existe'}: {terapia1.nombre}")

terapia2, created = Terapia.objects.get_or_create(
    codigo='TO-001',
    defaults={
        'nombre': 'Terapia Ocupacional',
        'categoria': cat_ocupacional,
        'descripcion': 'Desarrollo de habilidades motoras finas y gruesas, autonomía personal',
        'descripcion_corta': 'Desarrollo de habilidades motoras y autonomía',
        'especialidad': 'OCUPACIONAL',
        'modalidad': 'INDIVIDUAL',
        'duracion_minutos': 60,
        'costo_sesion': Decimal('90000.00'),
        'frecuencia_semanal_recomendada': 2,
        'edad_minima': 3,
        'edad_maxima': 15,
        'activo': True,
        'destacado': True,
    }
)
print(f"{'✓ Creada' if created else '• Ya existe'}: {terapia2.nombre}")

terapia3, created = Terapia.objects.get_or_create(
    codigo='ABA-001',
    defaults={
        'nombre': 'Terapia ABA Intensiva',
        'categoria': cat_conductual,
        'descripcion': 'Análisis Aplicado de Conducta intensivo para modificación conductual',
        'descripcion_corta': 'ABA intensivo para modificación conductual',
        'especialidad': 'CONDUCTUAL',
        'modalidad': 'INDIVIDUAL',
        'duracion_minutos': 90,
        'costo_sesion': Decimal('120000.00'),
        'frecuencia_semanal_recomendada': 5,
        'edad_minima': 2,
        'edad_maxima': 12,
        'activo': True,
        'destacado': True,
    }
)
print(f"{'✓ Creada' if created else '• Ya existe'}: {terapia3.nombre}")

# ========== CONSULTORIOS ==========
print("\n[4/5] Creando consultorios...")

consultorio1, created = Consultorio.objects.get_or_create(
    codigo='C1-101',
    defaults={
        'nombre': 'Consultorio Lenguaje 1',
        'tipo': 'LENGUAJE',
        'piso': 1,
        'numero': '101',
        'capacidad': 2,
        'area_metros': Decimal('15.00'),
        'estado': 'DISPONIBLE',
        'tiene_ventana': True,
        'tiene_aire_acondicionado': True,
        'accesible_silla_ruedas': True,
        'activo': True,
    }
)
print(f"{'✓ Creado' if created else '• Ya existe'}: {consultorio1.nombre}")

consultorio2, created = Consultorio.objects.get_or_create(
    codigo='C1-102',
    defaults={
        'nombre': 'Sala Terapia Ocupacional',
        'tipo': 'TERAPIA_OCUPACIONAL',
        'piso': 1,
        'numero': '102',
        'capacidad': 3,
        'area_metros': Decimal('25.00'),
        'estado': 'DISPONIBLE',
        'tiene_ventana': True,
        'tiene_aire_acondicionado': True,
        'accesible_silla_ruedas': True,
        'activo': True,
    }
)
print(f"{'✓ Creado' if created else '• Ya existe'}: {consultorio2.nombre}")

consultorio3, created = Consultorio.objects.get_or_create(
    codigo='C2-201',
    defaults={
        'nombre': 'Sala ABA - Integración Sensorial',
        'tipo': 'INTEGRACION_SENSORIAL',
        'piso': 2,
        'numero': '201',
        'capacidad': 4,
        'area_metros': Decimal('35.00'),
        'estado': 'DISPONIBLE',
        'tiene_ventana': True,
        'tiene_aire_acondicionado': True,
        'accesible_silla_ruedas': False,
        'activo': True,
    }
)
print(f"{'✓ Creado' if created else '• Ya existe'}: {consultorio3.nombre}")

# ========== PACIENTES ==========
print("\n[5/5] Creando pacientes...")

admin_user = Usuario.objects.filter(is_superuser=True).first()
if not admin_user:
    admin_user = coordinador1

paciente1, created = Paciente.objects.get_or_create(
    numero_documento='1234567890',
    defaults={
        'nombres': 'Juan',
        'apellidos': 'Pérez Gómez',
        'tipo_documento': 'TI',
        'fecha_nacimiento': date(2015, 6, 15),
        'genero': 'M',
        'telefono': '3001234567',
        'nombre_responsable': 'Ana Gómez',
        'parentesco_responsable': 'Madre',
        'telefono_responsable': '3007654321',
        'diagnostico_principal': 'TEA Nivel 2 - Trastorno del Espectro Autista',
        'numero_historia_clinica': 'HC-2024-001',
        'estado': 'ACTIVO',
        'creado_por': admin_user,
    }
)
print(f"{'✓ Creado' if created else '• Ya existe'}: {paciente1.nombre_completo}")

paciente2, created = Paciente.objects.get_or_create(
    numero_documento='9876543210',
    defaults={
        'nombres': 'María',
        'apellidos': 'López Sánchez',
        'tipo_documento': 'TI',
        'fecha_nacimiento': date(2016, 3, 20),
        'genero': 'F',
        'telefono': '3009876543',
        'nombre_responsable': 'Pedro López',
        'parentesco_responsable': 'Padre',
        'telefono_responsable': '3001237890',
        'diagnostico_principal': 'TEA Nivel 1 - Asperger',
        'numero_historia_clinica': 'HC-2024-002',
        'estado': 'ACTIVO',
        'creado_por': admin_user,
    }
)
print(f"{'✓ Creado' if created else '• Ya existe'}: {paciente2.nombre_completo}")

paciente3, created = Paciente.objects.get_or_create(
    numero_documento='5556667778',
    defaults={
        'nombres': 'Sofía',
        'apellidos': 'Ramírez Torres',
        'tipo_documento': 'RC',
        'fecha_nacimiento': date(2018, 9, 10),
        'genero': 'F',
        'telefono': '3005556677',
        'nombre_responsable': 'Laura Torres',
        'parentesco_responsable': 'Madre',
        'telefono_responsable': '3008889900',
        'diagnostico_principal': 'TEA Nivel 3 - Requiere apoyo sustancial',
        'alergias': 'Ninguna conocida',
        'numero_historia_clinica': 'HC-2024-003',
        'estado': 'ACTIVO',
        'creado_por': admin_user,
    }
)
print(f"{'✓ Creado' if created else '• Ya existe'}: {paciente3.nombre_completo}")

# ========== SESIONES DE HOY ==========
print("\n[BONUS] Creando sesiones para hoy...")

hoy = date.today()

sesion1, created = SesionTerapeutica.objects.get_or_create(
    numero_sesion='S-2024-001',
    defaults={
        'paciente': paciente1,
        'terapia': terapia1,
        'terapeuta': terapeuta1,
        'consultorio': consultorio1,
        'fecha': hoy,
        'hora_inicio': time(9, 0),
        'hora_fin': time(9, 45),
        'estado': 'PROGRAMADA',
        'creado_por': admin_user,
    }
)
print(f"{'✓ Creada' if created else '• Ya existe'}: Sesión {sesion1.numero_sesion}")

sesion2, created = SesionTerapeutica.objects.get_or_create(
    numero_sesion='S-2024-002',
    defaults={
        'paciente': paciente2,
        'terapia': terapia2,
        'terapeuta': psicologo1,
        'consultorio': consultorio2,
        'fecha': hoy,
        'hora_inicio': time(10, 0),
        'hora_fin': time(11, 0),
        'estado': 'PROGRAMADA',
        'creado_por': admin_user,
    }
)
print(f"{'✓ Creada' if created else '• Ya existe'}: Sesión {sesion2.numero_sesion}")

print("\n" + "=" * 60)
print("✅ DATOS DE PRUEBA GENERADOS EXITOSAMENTE")
print("=" * 60)
print("\n📋 RESUMEN:")
print(f"• Usuarios: {Usuario.objects.count()}")
print(f"• Categorías: {CategoriaTerapia.objects.count()}")
print(f"• Terapias: {Terapia.objects.count()}")
print(f"• Consultorios: {Consultorio.objects.count()}")
print(f"• Pacientes: {Paciente.objects.count()}")
print(f"• Sesiones: {SesionTerapeutica.objects.count()}")

print("\n🔑 CREDENCIALES:")
print("  Usuario: terapeuta1 / Contraseña: password123")
print("  Usuario: psicologo1 / Contraseña: password123")
print("  Usuario: coordinador1 / Contraseña: password123")
print("\n🚀 ¡Listo para usar el sistema!")
