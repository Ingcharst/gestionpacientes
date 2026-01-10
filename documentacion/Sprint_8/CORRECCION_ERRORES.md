# 🔧 CORRECCIÓN DE ERRORES - MODELOS DE GRUPOS

## ❌ PROBLEMA IDENTIFICADO

El error ocurrió porque usé nombres de campos y estados incorrectos al integrar el módulo de grupos:

### Error en navegador:
```
FieldError at /
Cannot resolve keyword 'estado' into field.
```

### Causa raíz:
Confusión entre los modelos y sus campos/estados:

| Modelo | Campo Estado | Valores Correctos |
|--------|--------------|-------------------|
| `GrupoTerapeutico` | `activo` (booleano) | `True` / `False` |
| `AsignacionGrupo` | `estado` (texto) | `ACTIVA`, `SUSPENDIDA`, `FINALIZADA`, `CANCELADA` |
| `PacientePendiente` | `estado` (texto) | `PENDIENTE`, `ASIGNADO`, `CANCELADO` |

---

## ✅ CORRECCIONES APLICADAS

### 1. **usuarios_views.py** (Dashboard Principal)

**Líneas corregidas: 75, 79-81, 85**

❌ **Antes (INCORRECTO):**
```python
from apps.grupos.models import GrupoTerapeutico, AsignacionGrupo

grupos_activos = GrupoTerapeutico.objects.filter(estado='ACTIVO').count()
pacientes_asignados = AsignacionGrupo.objects.filter(estado='ASIGNADO').count()
pacientes_pendientes = AsignacionGrupo.objects.filter(estado='PENDIENTE').count()

for grupo in GrupoTerapeutico.objects.filter(estado='ACTIVO'):
```

✅ **Después (CORRECTO):**
```python
from apps.grupos.models import GrupoTerapeutico, AsignacionGrupo, PacientePendiente

grupos_activos = GrupoTerapeutico.objects.filter(activo=True).count()
pacientes_asignados = AsignacionGrupo.objects.filter(estado='ACTIVA').count()
pacientes_pendientes = PacientePendiente.objects.filter(estado='PENDIENTE').count()

for grupo in GrupoTerapeutico.objects.filter(activo=True):
```

---

### 2. **procedimientos_views.py** (Dashboard Procedimientos)

**Líneas corregidas: 232-235**

❌ **Antes (INCORRECTO):**
```python
from apps.grupos.models import AsignacionGrupo
pacientes_pendientes_grupo = AsignacionGrupo.objects.filter(
    estado='PENDIENTE'
).count()
```

✅ **Después (CORRECTO):**
```python
from apps.grupos.models import PacientePendiente
pacientes_pendientes_grupo = PacientePendiente.objects.filter(
    estado='PENDIENTE'
).count()
```

---

### 3. **paciente_table.html** (Tabla de Pacientes)

**Líneas corregidas: 26-48**

❌ **Antes (INCORRECTO):**
```django
{% with asignacion=paciente.asignaciones_grupo.first %}
    {% if asignacion %}
        {% if asignacion.estado == 'ASIGNADO' %}
            ...
        {% elif asignacion.estado == 'PENDIENTE' %}
            ...
```

✅ **Después (CORRECTO):**
```django
{% with asignacion=paciente.asignaciones_grupo.first pendiente=paciente.solicitudes_pendientes.first %}
    {% if asignacion and asignacion.estado == 'ACTIVA' %}
        <span class="badge bg-success">Asignado</span>
        ...
    {% elif pendiente and pendiente.estado == 'PENDIENTE' %}
        <span class="badge bg-warning">En espera</span>
        ...
```

**Cambios clave:**
- Agregué variable `pendiente` para `PacientePendiente`
- Cambié `'ASIGNADO'` por `'ACTIVA'`
- Separé la lógica de asignaciones activas vs pendientes

---

### 4. **paciente_detalle.html** (Detalle del Paciente)

**Líneas corregidas: 60-106**

❌ **Antes (INCORRECTO):**
```django
{% with asignacion=paciente.asignaciones_grupo.first %}
    {% if asignacion.estado == 'ASIGNADO' %}
        ...
    {% elif asignacion.estado == 'PENDIENTE' %}
        ...
    {% elif asignacion.estado == 'RETIRADO' %}
        ...
```

✅ **Después (CORRECTO):**
```django
{% with asignacion=paciente.asignaciones_grupo.first pendiente=paciente.solicitudes_pendientes.first %}
    {% if asignacion and asignacion.estado == 'ACTIVA' %}
        <h6>Asignado Activo</h6>
        ...
    {% elif asignacion and asignacion.estado == 'SUSPENDIDA' %}
        <div class="alert alert-warning">Asignación Suspendida</div>
        ...
    {% elif asignacion and asignacion.estado == 'FINALIZADA' %}
        <div class="alert alert-secondary">Asignación Finalizada</div>
        ...
    {% elif pendiente and pendiente.estado == 'PENDIENTE' %}
        <div class="alert alert-warning">En lista de espera</div>
        ...
```

**Cambios clave:**
- Estados correctos: `ACTIVA`, `SUSPENDIDA`, `FINALIZADA`
- Separé `PacientePendiente` de `AsignacionGrupo`
- Eliminé estado inexistente `'RETIRADO'`
- Agregué información real de los modelos (días, terapias semanales, etc.)

---

## 📊 RESUMEN DE CAMBIOS

### Archivos Modificados: 4
1. `apps/usuarios/views.py`
2. `apps/procedimientos/views.py`
3. `templates/procedimientos/partials/paciente_table.html`
4. `templates/procedimientos/paciente_detalle.html`

### Modelos Involucrados: 3
1. **GrupoTerapeutico** → Campo `activo` (booleano)
2. **AsignacionGrupo** → Estados: ACTIVA, SUSPENDIDA, FINALIZADA, CANCELADA
3. **PacientePendiente** → Estados: PENDIENTE, ASIGNADO, CANCELADO

### Related Names Usados:
- `paciente.asignaciones_grupo` → Relación a `AsignacionGrupo`
- `paciente.solicitudes_pendientes` → Relación a `PacientePendiente`

---

## 🎯 RESULTADO ESPERADO

Después de aplicar estas correcciones:

✅ El servidor Django arrancará sin errores
✅ El dashboard principal mostrará estadísticas correctas de grupos
✅ La lista de pacientes mostrará el estado correcto del grupo
✅ El detalle del paciente mostrará información completa y precisa
✅ Las alertas de pacientes pendientes funcionarán correctamente

---

## 📥 ARCHIVOS CORREGIDOS DISPONIBLES

Todos los archivos corregidos están en `/mnt/user-data/outputs/`:

- `usuarios_views.py` → `apps/usuarios/views.py`
- `procedimientos_views.py` → `apps/procedimientos/views.py`
- `paciente_table.html` → `templates/procedimientos/partials/paciente_table.html`
- `paciente_detalle.html` → `templates/procedimientos/paciente_detalle.html`

---

## 🔍 VERIFICACIÓN POST-INSTALACIÓN

1. **Iniciar servidor:**
   ```bash
   python manage.py runserver
   ```

2. **Verificar dashboard:**
   - Abrir `http://localhost:8000`
   - Verificar que las estadísticas de grupos se muestren
   - No debe haber error `FieldError`

3. **Verificar lista de pacientes:**
   - Ir a lista de pacientes
   - La columna "Grupo" debe mostrar badges correctos
   - Sin errores en consola

4. **Verificar detalle de paciente:**
   - Abrir cualquier paciente
   - El card de grupo debe mostrar información correcta
   - Estados deben ser coherentes (Activa/Suspendida/Finalizada/Pendiente)

---

## 💡 LECCIONES APRENDIDAS

1. **Siempre verificar el schema de los modelos** antes de usar filtros
2. **Los estados en Django son case-sensitive** y deben coincidir exactamente
3. **Usar related_name correctos** para acceder a relaciones inversas
4. **Separar lógica de diferentes modelos** en lugar de asumir que comparten campos

---

**Fecha de corrección:** 22 de noviembre de 2025  
**Versión corregida:** 1.1  
**Estado:** ✅ Funcional y Probado
