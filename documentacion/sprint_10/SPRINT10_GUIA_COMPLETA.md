# ============================================================================
# 🚀 SPRINT 1: ADMISIÓN Y VALORACIÓN INICIAL
# Guía Completa de Implementación
# ============================================================================

## 📋 RESUMEN EJECUTIVO

Sprint 1 implementa el nuevo flujo de admisión y valoración de pacientes:

```
ADMISIÓN → VALORACIÓN INICIAL → PENDIENTE ASIGNACIÓN → ASIGNACIÓN A GRUPOS
```

### ✅ FUNCIONALIDADES IMPLEMENTADAS

1. **Admisión de Pacientes**
   - Número de admisión manual (formato: ADM-YYYYMMDD-####)
   - Captura de firma digital del acudiente
   - Historia clínica opcional (se genera automáticamente)
   - Nuevos estados de paciente

2. **Valoración Inicial por Profesional**
   - Registro detallado de problemas detectados
   - Evaluación por áreas (lenguaje, movilidad, cognitivo, etc.)
   - Recomendaciones de terapias
   - Diagnóstico profesional

3. **Gestión de Estados**
   - ADMITIDO: Paciente recién ingresado
   - PENDIENTE_VALORACION: En espera de evaluación
   - PENDIENTE_ASIGNACION: Valorado, listo para asignar grupos
   - ACTIVO: En tratamiento
   - Otros estados existentes...

---

## 📁 ARCHIVOS CREADOS/MODIFICADOS

| Archivo | Tipo | Descripción |
|---------|------|-------------|
| SPRINT1_MODIFICACIONES_MODELO_PACIENTE.py | Referencia | Cambios al modelo Paciente |
| SPRINT1_MODELO_VALORACION_INICIAL.py | Código Nuevo | Modelo completo ValoracionInicial |
| SPRINT1_FORMULARIOS.py | Código Nuevo | 3 formularios nuevos |
| SPRINT1_VISTAS.py | Código Nuevo | 8 vistas nuevas |
| SPRINT1_URLS.py | Referencia | URLs a agregar |

---

## 🔧 INSTALACIÓN PASO A PASO

### PASO 1: MODIFICAR MODELO PACIENTE

**Archivo:** `apps/procedimientos/models.py`

#### 1.1. Actualizar clase Estado (línea ~26)

```python
class Estado(models.TextChoices):
    # NUEVOS ESTADOS
    ADMITIDO = 'ADMITIDO', _('Admitido - Sin Valorar')
    PENDIENTE_VALORACION = 'PENDIENTE_VALORACION', _('Pendiente Valoración')
    PENDIENTE_ASIGNACION = 'PENDIENTE_ASIGNACION', _('Pendiente Asignación Terapias')
    
    # ESTADOS EXISTENTES
    ACTIVO = 'ACTIVO', _('Activo en Tratamiento')
    INACTIVO = 'INACTIVO', _('Inactivo')
    SUSPENDIDO = 'SUSPENDIDO', _('Suspendido')
    DADO_ALTA = 'DADO_ALTA', _('Dado de Alta')
```

#### 1.2. Agregar nuevos campos DESPUÉS de numero_historia_clinica (línea ~166)

```python
# ✅ NUEVO: Número de admisión
numero_admision = models.CharField(
    max_length=50,
    unique=True,
    verbose_name='Número de Admisión',
    help_text='Número de admisión del paciente (ingresado manualmente)'
)

# ✅ NUEVO: Firma digital del acudiente
firma_acudiente = models.TextField(
    blank=True,
    verbose_name='Firma Digital Acudiente',
    help_text='Firma del acudiente en formato base64'
)

fecha_firma_acudiente = models.DateTimeField(
    null=True,
    blank=True,
    verbose_name='Fecha y Hora de Firma'
)

ip_firma = models.GenericIPAddressField(
    null=True,
    blank=True,
    verbose_name='IP donde se firmó'
)
```

#### 1.3. Cambiar estado por defecto (línea ~184)

```python
estado = models.CharField(
    max_length=30,  # ✅ Aumentar de 20 a 30
    choices=Estado.choices,
    default=Estado.ADMITIDO,  # ✅ Cambiar de ACTIVO a ADMITIDO
    verbose_name='Estado'
)
```

---

### PASO 2: AGREGAR MODELO VALORACION INICIAL

**Archivo:** `apps/procedimientos/models.py`

Copiar TODO el contenido de `SPRINT1_MODELO_VALORACION_INICIAL.py`
y pegarlo AL FINAL del archivo, antes de cerrar.

**Ubicación:** Después del último modelo existente (EvolucionPaciente)

---

### PASO 3: AGREGAR FORMULARIOS

**Archivo:** `apps/procedimientos/forms.py`

Copiar TODO el contenido de `SPRINT1_FORMULARIOS.py`
y pegarlo AL FINAL del archivo.

Se agregan 3 formularios:
- AdmisionPacienteForm
- ValoracionInicialForm
- ProblemaDetectadoForm

---

### PASO 4: AGREGAR VISTAS

**Archivo:** `apps/procedimientos/views.py`

Copiar TODO el contenido de `SPRINT1_VISTAS.py`
y pegarlo AL FINAL del archivo.

Se agregan 8 vistas:
- admision_paciente
- pacientes_pendientes_valoracion
- crear_valoracion_inicial
- ver_valoracion_inicial
- editar_valoracion_inicial
- completar_valoracion
- pacientes_pendientes_asignacion

---

### PASO 5: AGREGAR URLs

**Archivo:** `apps/procedimientos/urls.py`

Agregar estas líneas dentro de `urlpatterns`:

```python
# SPRINT 1: ADMISIÓN Y VALORACIÓN
path('admision/', views.admision_paciente, name='admision_paciente'),
path('pacientes/pendientes-valoracion/', views.pacientes_pendientes_valoracion, name='pacientes_pendientes_valoracion'),
path('pacientes/<int:paciente_id>/valoracion/crear/', views.crear_valoracion_inicial, name='crear_valoracion_inicial'),
path('pacientes/<int:paciente_id>/valoracion/', views.ver_valoracion_inicial, name='ver_valoracion_inicial'),
path('pacientes/<int:paciente_id>/valoracion/editar/', views.editar_valoracion_inicial, name='editar_valoracion_inicial'),
path('valoracion/<int:valoracion_id>/completar/', views.completar_valoracion, name='completar_valoracion'),
path('pacientes/pendientes-asignacion/', views.pacientes_pendientes_asignacion, name='pacientes_pendientes_asignacion'),
```

---

### PASO 6: CREAR MIGRACIONES

```bash
# Crear archivo de migración
python manage.py makemigrations

# Aplicar migración
python manage.py migrate
```

**IMPORTANTE:** Habrá cambios en el modelo Paciente que afectarán registros existentes.

#### Opciones para manejar datos existentes:

**Opción A: Generar valores por defecto (Recomendado para pruebas)**
```python
# Django preguntará por valores por defecto para:
# - numero_admision: Sugerir 'ADM-LEGACY-0001', 'ADM-LEGACY-0002', etc.
```

**Opción B: Script de migración de datos**
Crear script para asignar números de admisión a pacientes existentes.

---

### PASO 7: CREAR TEMPLATES (Opcional - Básicos incluidos)

Crear directorio: `templates/procedimientos/`

Templates mínimos necesarios:
1. `admision_paciente.html` - Formulario de admisión con firma
2. `pacientes_pendientes_valoracion.html` - Lista de pacientes
3. `crear_valoracion_inicial.html` - Formulario de valoración
4. `ver_valoracion_inicial.html` - Vista de valoración
5. `pacientes_pendientes_asignacion.html` - Lista para asignar

**Nota:** Los templates se entregarán en siguiente archivo.

---

## 🎯 FLUJO COMPLETO IMPLEMENTADO

```
1. Usuario crea ADMISIÓN
   ├─ Ingresa datos del paciente
   ├─ Captura firma digital del acudiente
   ├─ Asigna número de admisión: ADM-20251124-0001
   └─ Estado: ADMITIDO

2. Profesional ve lista de "Pendientes de Valoración"
   └─ Accede al paciente admitido

3. Profesional crea VALORACIÓN INICIAL
   ├─ Evalúa al paciente
   ├─ Registra problemas detectados
   ├─ Recomienda terapias
   └─ Marca como COMPLETADA
       └─ Estado cambia automáticamente a: PENDIENTE_ASIGNACION

4. Asesor ve lista de "Pendientes de Asignación"
   ├─ Ve recomendaciones del profesional
   └─ Listo para asignar a grupos (Sprint 2)
```

---

## ✅ VERIFICACIÓN POST-INSTALACIÓN

### 1. Verificar Modelos
```python
python manage.py shell

from apps.procedimientos.models import Paciente, ValoracionInicial

# Verificar estados
print(Paciente.Estado.choices)
# Debe mostrar: ADMITIDO, PENDIENTE_VALORACION, PENDIENTE_ASIGNACION...

# Verificar modelo ValoracionInicial existe
print(ValoracionInicial._meta.fields)
```

### 2. Verificar URLs
```bash
python manage.py show_urls | grep admision
python manage.py show_urls | grep valoracion
```

### 3. Probar Flujo Completo

**A. Admitir Paciente:**
1. Ir a: `http://localhost:8000/procedimientos/admision/`
2. Llenar formulario
3. (Opcional) Firmar con periférico
4. Guardar
5. ✅ Debe crear paciente con estado ADMITIDO

**B. Crear Valoración:**
1. Ir a lista de pendientes de valoración
2. Seleccionar paciente
3. Llenar formulario de valoración
4. Marcar como completada
5. ✅ Paciente debe cambiar a PENDIENTE_ASIGNACION

**C. Ver Lista para Asignación:**
1. Ir a: `http://localhost:8000/procedimientos/pacientes/pendientes-asignacion/`
2. ✅ Debe mostrar el paciente valorado

---

## 🐛 PROBLEMAS COMUNES

### Error: "numero_admision cannot be null"
**Solución:** Pacientes existentes no tienen número de admisión.
```python
# Migración de datos (ejecutar en shell)
from apps.procedimientos.models import Paciente
for i, p in enumerate(Paciente.objects.filter(numero_admision__isnull=True), 1):
    p.numero_admision = f"ADM-LEGACY-{i:04d}"
    p.save()
```

### Error: "estado value too long"
**Solución:** Aumentar max_length del campo estado a 30.

### ImportError al migrar
**Solución:** Verificar que todos los imports estén en models.py:
```python
from django.db import models
from django.utils.translation import gettext_lazy as _
import random
```

---

## 📊 ESTADÍSTICAS DEL SPRINT 1

| Métrica | Cantidad |
|---------|----------|
| Modelos Nuevos | 1 (ValoracionInicial) |
| Modelos Modificados | 1 (Paciente) |
| Campos Nuevos en Paciente | 3 |
| Estados Nuevos | 3 |
| Formularios Nuevos | 3 |
| Vistas Nuevas | 8 |
| URLs Nuevas | 7 |
| Templates Requeridos | 5 |

---

## 🎯 PRÓXIMOS PASOS (SPRINT 2)

Sprint 2 implementará:
- Asignación de pacientes a MÚLTIPLES grupos
- Número de terapias por asignación
- Vista del asesor para asignación

---

## 📞 SOPORTE

Si encuentras problemas:
1. Revisar logs: `python manage.py runserver`
2. Verificar migraciones: `python manage.py showmigrations`
3. Verificar estructura de BD

---

**Sprint 1 - COMPLETO** ✅  
**Tiempo estimado de instalación:** 30-45 minutos  
**Nivel de dificultad:** Medio
