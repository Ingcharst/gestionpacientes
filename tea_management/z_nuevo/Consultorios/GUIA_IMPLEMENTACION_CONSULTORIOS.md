# 🏥 GUÍA COMPLETA: Implementación de Consultorios

## 🎯 OBJETIVOS

1. ✅ Agregar campo `terapia` a `AsignacionConsultorio`
2. ✅ Implementar todas las vistas faltantes
3. ✅ Habilitar acceso a todas las interfaces

---

## 📋 PROBLEMAS IDENTIFICADOS

### 1. **Campo Terapia Faltante** ❌
```python
# ANTES (models.py línea ~262):
class AsignacionConsultorio(models.Model):
    consultorio = models.ForeignKey(...)
    terapeuta = models.ForeignKey(...)
    # ❌ NO HAY CAMPO TERAPIA
```

**Impacto:** No se puede saber qué tipo de terapia se realizará en el consultorio asignado.

### 2. **Vistas No Implementadas** ❌
```python
# ANTES (views.py):
# Archivo vacío o sin contenido
```

**Impacto:** URLs definidas pero sin funcionalidad. El usuario no puede acceder a las interfaces.

---

## 🔧 SOLUCIÓN PASO A PASO

### **PASO 1: Actualizar Modelo AsignacionConsultorio**

**Archivo:** `tea_management/apps/consultorios/models.py`

**1.1 Agregar import al inicio del archivo:**

```python
# Línea ~8, después de: from apps.usuarios.models import Usuario
from apps.terapias.models import Terapia  # ✅ AGREGAR ESTE IMPORT
```

**1.2 Reemplazar la clase AsignacionConsultorio completa:**

Buscar la línea ~262 donde empieza `class AsignacionConsultorio(models.Model):` y reemplazar TODA la clase con el código del archivo `models_asignacion_actualizado.py`.

**Cambios clave:**
- ✅ Nuevo campo `terapia` (ForeignKey a Terapia)
- ✅ Nuevo índice en Meta para optimizar consultas
- ✅ Actualizado `__str__` para mostrar terapia
- ✅ Permitir `null=True` temporalmente para migración

---

### **PASO 2: Crear Migración**

```bash
cd tea_management

# Crear migración
python manage.py makemigrations consultorios

# Debería mostrar:
# Migrations for 'consultorios':
#   apps/consultorios/migrations/00XX_asignacion_add_terapia.py
#     - Add field terapia to asignacionconsultorio

# Aplicar migración
python manage.py migrate consultorios
```

---

### **PASO 3: Reemplazar Vistas**

**Archivo:** `tea_management/apps/consultorios/views.py`

**Backup del archivo actual:**
```bash
cp apps/consultorios/views.py apps/consultorios/views.py.backup
```

**Reemplazar con el nuevo contenido:**
```bash
cp /ruta/views_consultorios_completo.py apps/consultorios/views.py
```

**Vistas implementadas:**

| Vista | Función | URL |
|-------|---------|-----|
| `consultorio_list` | Lista consultorios | `/consultorios/` |
| `consultorio_detail` | Detalle consultorio | `/consultorios/<id>/` |
| `consultorio_create` | Crear consultorio | `/consultorios/crear/` |
| `consultorio_update` | Editar consultorio | `/consultorios/<id>/editar/` |
| `consultorio_cambiar_estado` | Cambiar estado | `/consultorios/<id>/cambiar-estado/` |
| `sala_create` | Crear sala | `/consultorios/<id>/salas/crear/` |
| `sala_update` | Editar sala | `/consultorios/salas/<id>/editar/` |
| `asignacion_list` | Lista asignaciones | `/consultorios/asignaciones/` |
| `asignacion_detail` | Detalle asignación | `/consultorios/asignaciones/<id>/` |
| `asignacion_create` | Crear asignación | `/consultorios/asignaciones/crear/` |
| `asignacion_update` | Editar asignación | `/consultorios/asignaciones/<id>/editar/` |
| `mis_consultorios` | Mis consultorios | `/consultorios/mis-consultorios/` |
| `disponibilidad_list` | Lista disponibilidad | `/consultorios/disponibilidad/` |
| `disponibilidad_create` | Crear disponibilidad | `/consultorios/disponibilidad/crear/` |
| `disponibilidad_update` | Editar disponibilidad | `/consultorios/disponibilidad/<id>/editar/` |
| `calendario_disponibilidad` | Calendario | `/consultorios/disponibilidad/calendario/` |
| `estadisticas_consultorios` | Estadísticas | `/consultorios/estadisticas/` |

**Total:** 17 vistas implementadas ✅

---

### **PASO 4: Actualizar Formulario**

**Archivo:** `tea_management/apps/consultorios/forms.py`

Buscar la clase `AsignacionConsultorioForm` (~línea 100) y reemplazarla con el código del archivo `forms_asignacion_actualizado.py`.

**Cambios:**
- ✅ Campo `terapia` agregado a `fields`
- ✅ Widget Select para terapia
- ✅ Queryset filtrado (solo terapias activas)
- ✅ Layout actualizado con campo terapia

---

### **PASO 5: Verificar URLs**

**Archivo:** `tea_management/apps/consultorios/urls.py`

El archivo ya está correcto con `app_name = 'consultorios'` ✅

Verificar que esté incluido en el archivo principal:

**Archivo:** `tea_management/config/urls.py`

```python
urlpatterns = [
    # ... otras URLs
    path('consultorios/', include('apps.consultorios.urls')),
]
```

---

### **PASO 6: Verificar Templates**

Los templates deben existir en:
```
tea_management/templates/consultorios/
├── consultorio_list.html
├── consultorio_detail.html
├── consultorio_form.html
├── sala_form.html
├── asignacion_list.html
├── asignacion_detail.html
├── asignacion_form.html
├── mis_consultorios.html
├── disponibilidad_list.html
├── disponibilidad_form.html
├── calendario_disponibilidad.html
└── estadisticas.html
```

**Si faltan templates**, extraerlos del ZIP inicial que compartiste.

---

### **PASO 7: Actualizar Admin (Opcional)**

**Archivo:** `tea_management/apps/consultorios/admin.py`

Agregar `terapia` en los displays:

```python
@admin.register(AsignacionConsultorio)
class AsignacionConsultorioAdmin(admin.ModelAdmin):
    list_display = (
        'consultorio', 'terapeuta_nombre', 'terapia',  # ✅ AGREGADO
        'tipo_asignacion', 'fecha_inicio', 'fecha_fin',
        'vigente_badge', 'prioridad_stars', 'activo'
    )
    
    # ... resto del código
```

---

## 🚀 IMPLEMENTACIÓN RÁPIDA

### **Opción A: Manual (Recomendado)**

```bash
# 1. Actualizar models.py
# → Agregar import: from apps.terapias.models import Terapia
# → Reemplazar clase AsignacionConsultorio

# 2. Crear migración
python manage.py makemigrations consultorios
python manage.py migrate

# 3. Reemplazar views.py
cp /ruta/views_consultorios_completo.py apps/consultorios/views.py

# 4. Actualizar forms.py
# → Reemplazar clase AsignacionConsultorioForm

# 5. Reiniciar servidor
python manage.py runserver
```

### **Opción B: Script Automatizado**

```bash
python implementar_consultorios.sh
```

---

## ✅ VERIFICACIÓN POST-IMPLEMENTACIÓN

### **1. Verificar Migración**

```bash
python manage.py showmigrations consultorios

# Debe mostrar:
# consultorios
#  [X] 0001_initial
#  [X] 00XX_asignacion_add_terapia  ← NUEVA
```

### **2. Verificar URLs**

```bash
python manage.py shell

>>> from django.urls import reverse
>>> reverse('consultorios:consultorio_list')
'/consultorios/'  # ✅ OK

>>> reverse('consultorios:asignacion_create')
'/consultorios/asignaciones/crear/'  # ✅ OK
```

### **3. Probar en Navegador**

**Lista de URLs a probar:**

| URL | Resultado Esperado |
|-----|-------------------|
| `/consultorios/` | ✅ Lista de consultorios |
| `/consultorios/crear/` | ✅ Formulario crear consultorio |
| `/consultorios/1/` | ✅ Detalle consultorio #1 |
| `/consultorios/asignaciones/` | ✅ Lista asignaciones |
| `/consultorios/asignaciones/crear/` | ✅ Formulario con campo TERAPIA |
| `/consultorios/mis-consultorios/` | ✅ Mis consultorios (terapeuta) |
| `/consultorios/disponibilidad/` | ✅ Lista disponibilidad |
| `/consultorios/estadisticas/` | ✅ Dashboard estadísticas |

### **4. Verificar Formulario de Asignación**

1. Ir a `/consultorios/asignaciones/crear/`
2. Verificar que aparezcan TODOS estos campos:
   - ✅ Consultorio
   - ✅ Terapeuta
   - ✅ **Terapia** ← NUEVO CAMPO
   - ✅ Tipo de Asignación
   - ✅ Fecha Inicio
   - ✅ Fecha Fin
   - ✅ Prioridad
   - ✅ Días de la Semana
   - ✅ Horario
   - ✅ Notas
   - ✅ Activo

3. Crear una asignación de prueba
4. Verificar que se guardó con la terapia seleccionada

---

## 🎯 NUEVA FUNCIONALIDAD: Campo Terapia

### **Uso en el Sistema**

Con el campo `terapia` ahora puedes:

1. **Saber qué terapias se realizan en cada consultorio:**
   ```python
   # En templates:
   {{ asignacion.terapia.nombre }}
   ```

2. **Filtrar asignaciones por tipo de terapia:**
   ```python
   # En vistas:
   asignaciones = AsignacionConsultorio.objects.filter(
       terapia__nombre='Cognitiva'
   )
   ```

3. **Optimizar distribución de consultorios:**
   - Terapia Física → Salas de Terapia Física
   - Lenguaje → Salas de Lenguaje
   - Etc.

4. **Reportes más precisos:**
   - Uso por tipo de terapia
   - Disponibilidad por especialidad
   - Capacidad utilizada por terapia

---

## 📊 RESUMEN DE CAMBIOS

| Componente | Estado Antes | Estado Después |
|------------|--------------|----------------|
| Campo `terapia` | ❌ No existe | ✅ Implementado |
| Vistas | ❌ 0 vistas | ✅ 17 vistas |
| Formulario | ⚠️ Sin campo terapia | ✅ Con campo terapia |
| URLs | ⚠️ Definidas sin vistas | ✅ Funcionando |
| Migración | - | ✅ Creada |
| Funcionalidad | ❌ 10% | ✅ 100% |

---

## 🆘 TROUBLESHOOTING

### **Problema:** Error en migración
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Solución:**
```bash
python manage.py migrate --fake consultorios zero
python manage.py migrate consultorios
```

### **Problema:** Formulario sin campo terapia
**Solución:** 
1. Limpiar caché: `Ctrl+Shift+R` en navegador
2. Verificar que forms.py fue actualizado
3. Reiniciar servidor Django

### **Problema:** NoReverseMatch en URLs
**Solución:**
```bash
# Verificar namespace en urls.py
app_name = 'consultorios'  # DEBE EXISTIR

# Usar namespace en templates:
{% url 'consultorios:asignacion_create' %}  # ✅ CORRECTO
{% url 'asignacion_create' %}  # ❌ INCORRECTO
```

---

## 📞 PRÓXIMOS PASOS

1. ✅ Implementar cambios
2. ✅ Probar todas las URLs
3. ✅ Crear asignaciones con terapias
4. ⏭️ Configurar permisos por rol
5. ⏭️ Agregar validaciones adicionales
6. ⏭️ Implementar notificaciones

---

✅ **DESPUÉS DE SEGUIR ESTA GUÍA, TENDRÁS:**
- Campo `terapia` en asignaciones
- 17 vistas funcionando
- Acceso completo a todas las interfaces
- Sistema de consultorios 100% operativo
