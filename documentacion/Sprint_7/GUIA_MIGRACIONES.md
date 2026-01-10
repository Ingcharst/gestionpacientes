# 📋 GUÍA DE MIGRACIONES - SPRINT 7

## 🎯 Migraciones Esperadas

Al ejecutar `python manage.py makemigrations grupos`, deberías ver:

```
Migrations for 'grupos':
  grupos/migrations/0001_initial.py
    - Create model GrupoTerapeutico
    - Create model AsignacionGrupo
    - Create model PacientePendiente
    - Create index grupos_grupoterapeutico_activo_hora_inicio_idx on field(s) activo, hora_inicio of model grupoterapeutico
    - Create index grupos_grupoterapeutico_capacidad_maxima_pacientes_actuales_idx on field(s) capacidad_maxima, pacientes_actuales of model grupoterapeutico
    - Create index grupos_asignaciongrupo_estado_fecha_inicio_asignacion_idx on field(s) estado, fecha_inicio_asignacion of model asignaciongrupo
    - Create index grupos_asignaciongrupo_paciente_estado_idx on field(s) paciente, estado of model asignaciongrupo
    - Create index grupos_asignaciongrupo_grupo_estado_idx on field(s) grupo, estado of model asignaciongrupo
    - Create index grupos_pacientependiente_estado_prioridad_fecha_solicitud_idx on field(s) estado, prioridad, fecha_solicitud of model pacientependiente
    - Create index grupos_pacientependiente_paciente_estado_idx on field(s) paciente, estado of model pacientependiente
    - Alter unique_together for asignaciongrupo (1 constraint(s))
```

---

## 📊 Estructura de Base de Datos

### Tablas Creadas:

#### 1. `grupos_grupoterapeutico`
```sql
- id (AutoField, PK)
- nombre (CharField, 100, unique)
- descripcion (TextField, blank)
- hora_inicio (TimeField)
- hora_fin (TimeField)
- dias_disponibles (JSONField)
- capacidad_maxima (PositiveIntegerField)
- pacientes_actuales (PositiveIntegerField, default=0)
- activo (BooleanField, default=True)
- fecha_creacion (DateTimeField, auto_now_add)
- fecha_actualizacion (DateTimeField, auto_now)
- notas (TextField, blank)
```

**Índices:**
- `activo + hora_inicio`
- `capacidad_maxima + pacientes_actuales`

---

#### 2. `grupos_asignaciongrupo`
```sql
- id (AutoField, PK)
- paciente_id (ForeignKey → procedimientos_paciente)
- grupo_id (ForeignKey → grupos_grupoterapeutico)
- dias_asistencia (JSONField)
- numero_terapias_semanales (PositiveIntegerField)
- fecha_inicio_asignacion (DateField)
- fecha_fin_asignacion (DateField, null, blank)
- estado (CharField, 20, choices)
- fecha_creacion (DateTimeField, auto_now_add)
- fecha_actualizacion (DateTimeField, auto_now)
- notas (TextField, blank)
- motivo_suspension (TextField, blank)
```

**Índices:**
- `estado + fecha_inicio_asignacion`
- `paciente + estado`
- `grupo + estado`

**Constraint:**
- unique_together: `(paciente, grupo, estado)`

---

#### 3. `grupos_pacientependiente`
```sql
- id (AutoField, PK)
- paciente_id (ForeignKey → procedimientos_paciente)
- preferencia_horario (TimeField)
- dias_preferidos (JSONField)
- prioridad (CharField, 10, choices)
- estado (CharField, 20, choices)
- fecha_solicitud (DateTimeField, auto_now_add)
- fecha_asignacion (DateTimeField, null, blank)
- grupo_asignado_id (ForeignKey → grupos_grupoterapeutico, null, blank)
- observaciones (TextField, blank)
- motivo_cancelacion (TextField, blank)
```

**Índices:**
- `estado + prioridad + fecha_solicitud`
- `paciente + estado`

---

## 🔗 Relaciones de Llave Foránea

```
procedimientos_paciente
    ↓
    ├── grupos_asignaciongrupo (CASCADE)
    │       ↓
    │       grupos_grupoterapeutico
    │
    └── grupos_pacientependiente (CASCADE)
            ↓
            grupos_grupoterapeutico (SET_NULL)
```

---

## ✅ Comandos de Verificación

### Después de migrar:

```bash
# Ver migraciones aplicadas
python manage.py showmigrations grupos

# Debería mostrar:
# grupos
#  [X] 0001_initial

# Verificar tablas en BD
python manage.py dbshell

# MySQL:
mysql> SHOW TABLES LIKE 'grupos%';
# Debería mostrar:
# grupos_asignaciongrupo
# grupos_grupoterapeutico
# grupos_pacientependiente

mysql> DESCRIBE grupos_grupoterapeutico;
mysql> DESCRIBE grupos_asignaciongrupo;
mysql> DESCRIBE grupos_pacientependiente;
```

---

## 🐛 Solución de Problemas

### Error: "Field 'grupo_actual' doesn't exist"
**Causa:** El modelo Paciente no tiene los campos necesarios

**Solución:**
```bash
# Verificar que Paciente tenga estos campos (agregados en Sprint 6):
# - tiene_grupo_asignado (BooleanField)
# - grupo_actual (ForeignKey)
# - estado_asignacion (CharField)

# Si faltan, agregar y crear migración:
python manage.py makemigrations procedimientos
python manage.py migrate procedimientos
```

---

### Error: "Constraint unique_together"
**Causa:** Datos duplicados en BD

**Solución:**
```bash
# Limpiar datos duplicados antes de migrar
python manage.py shell

>>> from apps.grupos.models import AsignacionGrupo
>>> duplicados = AsignacionGrupo.objects.values('paciente', 'grupo', 'estado').annotate(count=Count('id')).filter(count__gt=1)
>>> # Revisar y limpiar manualmente
```

---

### Error: JSONField en MySQL < 5.7
**Causa:** MySQL antiguo no soporta JSON

**Solución:**
1. Actualizar MySQL a 5.7+
2. O cambiar a PostgreSQL
3. O usar TextField con serialización manual

---

## 📈 Rendimiento

Los índices creados optimizan:
- ✅ Búsqueda de grupos activos por horario
- ✅ Filtrado de asignaciones por estado
- ✅ Consulta de pacientes pendientes por prioridad
- ✅ Verificación de cupos disponibles

---

## 🎉 Verificación Final

```bash
python manage.py shell

>>> from apps.grupos.models import *

# Verificar modelos
>>> GrupoTerapeutico.objects.all()
<QuerySet []>  # ✅ Modelo funciona

>>> AsignacionGrupo.objects.all()
<QuerySet []>  # ✅ Modelo funciona

>>> PacientePendiente.objects.all()
<QuerySet []>  # ✅ Modelo funciona

# Probar señales
>>> from apps.grupos import signals
>>> # ✅ Señales cargadas sin errores
```

---

**Estado:** ✅ Listo para migrar
