# SCRIPT DE DIAGNÓSTICO - SPRINT 1
# Ejecutar: python manage.py shell
# Copiar y pegar este código completo

print("=" * 80)
print("DIAGNÓSTICO SPRINT 1")
print("=" * 80)

# 1. VERIFICAR MODELO
print("\n1. MODELO PACIENTE:")
try:
    from apps.procedimientos.models import Paciente
    campo = Paciente._meta.get_field('numero_admision')
    print(f"   ✅ Campo numero_admision existe: {campo}")
    print(f"   ✅ Tipo: {campo.get_internal_type()}")
    print(f"   ✅ Max length: {campo.max_length}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# 2. VERIFICAR ESTADOS
print("\n2. ESTADOS DEL PACIENTE:")
try:
    print(f"   Estados disponibles: {[e[0] for e in Paciente.Estado.choices]}")
    if 'ADMITIDO' in [e[0] for e in Paciente.Estado.choices]:
        print("   ✅ Estado ADMITIDO existe")
    else:
        print("   ❌ Falta estado ADMITIDO")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# 3. VERIFICAR FORMULARIO
print("\n3. FORMULARIO ADMISION:")
try:
    from apps.procedimientos.forms import AdmisionPacienteForm
    form = AdmisionPacienteForm()
    if 'numero_admision' in form.fields:
        print("   ✅ Campo numero_admision en formulario")
    else:
        print("   ❌ Campo numero_admision NO está en formulario")
        print(f"   Campos actuales: {list(form.fields.keys())}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# 4. VERIFICAR VISTAS
print("\n4. VISTAS:")
try:
    from apps.procedimientos import views
    if hasattr(views, 'admision_paciente'):
        print("   ✅ Vista admision_paciente existe")
    else:
        print("   ❌ Vista admision_paciente NO existe")
    
    if hasattr(views, 'crear_valoracion_inicial'):
        print("   ✅ Vista crear_valoracion_inicial existe")
    else:
        print("   ❌ Vista crear_valoracion_inicial NO existe")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# 5. VERIFICAR MODELO VALORACION
print("\n5. MODELO VALORACION:")
try:
    from apps.procedimientos.models import ValoracionInicial
    print("   ✅ Modelo ValoracionInicial existe")
    print(f"   Campos: {[f.name for f in ValoracionInicial._meta.get_fields()][:10]}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# 6. VERIFICAR URLs
print("\n6. URLs:")
try:
    from django.urls import reverse
    urls = [
        'procedimientos:admision_paciente',
        'procedimientos:pacientes_pendientes_valoracion',
        'procedimientos:pacientes_pendientes_asignacion',
    ]
    for url in urls:
        try:
            reverse(url)
            print(f"   ✅ {url}")
        except:
            print(f"   ❌ {url} NO configurada")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

print("\n" + "=" * 80)
print("RESUMEN:")
print("Si ves ❌, revisa ese punto en el CHECKLIST_VERIFICACION.txt")
print("=" * 80)
