# 📦 FASE 1 COMPLETADA: App Grupos Creada

## ✅ ARCHIVOS CREADOS

```
apps/grupos/
├── __init__.py          ✅ Configuración de la app
├── apps.py              ✅ Configuración AppConfig
├── models.py            ✅ 3 modelos (558 líneas)
│   ├── GrupoTerapeutico
│   ├── AsignacionGrupo
│   └── PacientePendiente
├── admin.py             ✅ Admin de Django (320 líneas)
└── signals.py           ✅ Señales automáticas (120 líneas)
```

---

## 🚀 INSTALACIÓN

### Paso 1: Copiar Archivos

Copia el contenido de la carpeta `apps/grupos/` a tu proyecto:

```bash
# Desde donde descargaste los archivos
cp -r apps/grupos /ruta/a/tu/proyecto/tea_management/apps/
```

### Paso 2: Registrar App en Settings

Edita `config/settings.py` y agrega la app a `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... apps existentes ...
    'apps.usuarios',
    'apps.terapias',
    'apps.consultorios',
    'apps.procedimientos',
    'apps.grupos',  # ← AGREGAR ESTA LÍNEA
]
```

### Paso 3: Modificar Modelo Paciente

Edita `apps/procedimientos/models.py` y agrega estos campos a la clase `Paciente`:

```python
class Paciente(models.Model):
    # ... campos existentes ...
    
    # ✅ AGREGAR ESTOS CAMPOS AL FINAL (antes de fecha_ingreso)
    
    # Control de Grupos
    tiene_grupo_asignado = models.BooleanField(
        default=False,
        verbose_name='Tiene Grupo Asignado'
    )
    
    grupo_actual = models.ForeignKey(
        'grupos.GrupoTerapeutico',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pacientes_actuales',
        verbose_name='Grupo Actual'
    )
    
    class EstadoAsignacion(models.TextChoices):
        ASIGNADO = 'ASIGNADO', _('Asignado a Grupo')
        PENDIENTE = 'PENDIENTE', _('Pendiente de Asignación')
        SIN_SOLICITUD = 'SIN_SOLICITUD', _('Sin Solicitud')
    
    estado_asignacion = models.CharField(
        max_length=20,
        choices=EstadoAsignacion.choices,
        default=EstadoAsignacion.SIN_SOLICITUD,
        verbose_name='Estado de Asignación a Grupo'
    )
    
    # Continuar con fecha_ingreso existente...
    fecha_ingreso = models.DateField(
        default=timezone.now,
        blank=True,  # ← Ya corregido
        verbose_name='Fecha de Ingreso'
    )
```

### Paso 4: Crear Migraciones

```bash
# Crear migraciones para la nueva app
python manage.py makemigrations grupos

# Crear migraciones para cambios en procedimientos
python manage.py makemigrations procedimientos

# Salida esperada:
# Migrations for 'grupos':
#   grupos/migrations/0001_initial.py
#     - Create model GrupoTerapeutico
#     - Create model AsignacionGrupo
#     - Create model PacientePendiente
#
# Migrations for 'procedimientos':
#   procedimientos/migrations/00XX_add_grupo_fields.py
#     - Add field tiene_grupo_asignado on paciente
#     - Add field grupo_actual on paciente
#     - Add field estado_asignacion on paciente
```

### Paso 5: Aplicar Migraciones

```bash
python manage.py migrate grupos
python manage.py migrate procedimientos
```

### Paso 6: Verificar en Admin

```bash
# Iniciar servidor
python manage.py runserver

# Ir a: http://localhost:8000/admin/grupos/
```

Deberías ver:
- ✅ Grupos Terapéuticos
- ✅ Asignaciones a Grupos
- ✅ Pacientes Pendientes de Asignación

---

## 📊 MODELOS CREADOS

### 1. GrupoTerapeutico
```python
Campos principales:
- nombre: "Grupo 9:00 a.m."
- hora_inicio / hora_fin: 09:00 - 11:00
- dias_disponibles: ["L","M","X","J","V"]
- capacidad_maxima: 10
- pacientes_actuales: 5 (auto-calculado)
- activo: True/False

Propiedades:
- cupos_disponibles: 5
- tiene_cupo: True
- porcentaje_ocupacion: 50.0%
- esta_lleno: False
```

### 2. AsignacionGrupo
```python
Campos principales:
- paciente: FK → Paciente
- grupo: FK → GrupoTerapeutico
- dias_asistencia: ["L","M","X"]
- numero_terapias_semanales: 3
- estado: ACTIVA/SUSPENDIDA/FINALIZADA/CANCELADA
- fecha_inicio/fin_asignacion

Métodos:
- finalizar(motivo)
- suspender(motivo)
- reactivar()
```

### 3. PacientePendiente
```python
Campos principales:
- paciente: FK → Paciente
- preferencia_horario: 09:00
- dias_preferidos: ["L","M","X"]
- prioridad: ALTA/MEDIA/BAJA
- estado: PENDIENTE/ASIGNADO/CANCELADO
- grupo_asignado: FK → GrupoTerapeutico (cuando se asigna)

Propiedades:
- dias_esperando: 15
- esta_pendiente: True
```

---

## 🧪 TESTING BÁSICO

### Test 1: Crear Grupo en Admin

```bash
# 1. Ir a admin: http://localhost:8000/admin/grupos/grupoterapeutico/add/

# 2. Llenar datos:
Nombre: Grupo 9:00 a.m.
Hora Inicio: 09:00
Hora Fin: 11:00
Días Disponibles: ["L","M","X","J","V"]
Capacidad Máxima: 10
Activo: ✓

# 3. Guardar

# 4. Verificar:
- Aparece en lista de grupos
- Cupos disponibles: 10
- Ocupación: 0%
```

### Test 2: Verificar en Shell

```bash
python manage.py shell

>>> from apps.grupos.models import GrupoTerapeutico
>>> grupo = GrupoTerapeutico.objects.first()
>>> print(grupo)
Grupo 9:00 a.m. (09:00 - 11:00)

>>> grupo.cupos_disponibles
10

>>> grupo.porcentaje_ocupacion
0.0

>>> grupo.dias_semana_texto
'Lunes, Martes, Miércoles, Jueves, Viernes'
```

### Test 3: Verificar Campos en Paciente

```bash
python manage.py shell

>>> from apps.procedimientos.models import Paciente
>>> p = Paciente.objects.first()

>>> p.tiene_grupo_asignado
False

>>> p.grupo_actual
None

>>> p.estado_asignacion
'SIN_SOLICITUD'
```

---

## 📋 CHECKLIST DE VERIFICACIÓN

- [ ] Carpeta `apps/grupos/` copiada al proyecto
- [ ] App agregada a `INSTALLED_APPS`
- [ ] Modelo `Paciente` modificado con 3 campos nuevos
- [ ] Migraciones creadas: `makemigrations grupos`
- [ ] Migraciones creadas: `makemigrations procedimientos`
- [ ] Migraciones aplicadas: `migrate`
- [ ] Admin accesible: `/admin/grupos/`
- [ ] Se pueden crear grupos en admin
- [ ] Campos nuevos visibles en modelo Paciente

---

## 🎯 PRÓXIMA FASE

**Fase 2: Lógica de Negocio (utils.py)**

Crearemos las funciones auxiliares:
- `verificar_cupo_disponible(grupo, dias)`
- `asignar_paciente_a_grupo(paciente, grupo, dias, num_terapias)`
- `marcar_paciente_pendiente(paciente, preferencias)`
- `buscar_grupo_disponible(dias, hora)`
- Y más...

**¿Listo para continuar con la Fase 2?**

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: "No module named 'apps.grupos'"
**Solución:** Verifica que la carpeta esté en `apps/grupos/` y que `__init__.py` exista

### Error: "grupos is not an installed app"
**Solución:** Agrega `'apps.grupos'` a `INSTALLED_APPS` en settings.py

### Error: "Cannot resolve keyword 'grupo_actual'"
**Solución:** Verifica que agregaste los 3 campos nuevos al modelo Paciente

### Error al migrar
**Solución:**
```bash
# Ver estado de migraciones
python manage.py showmigrations grupos
python manage.py showmigrations procedimientos

# Si hay conflictos, revisar archivos de migración
```

---

**Fecha:** 20/11/2025  
**Fase:** 1 de 6 ✅  
**Estado:** Completada  
**Archivos:** 5 archivos core + modificaciones  
**Líneas de código:** ~1000 líneas
