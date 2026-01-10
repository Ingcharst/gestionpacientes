# 🚀 GUÍA DE PRUEBA RÁPIDA - SPRINT 8

## ⚡ Inicio Rápido (2 minutos)

### 1. Extraer Proyecto
```bash
tar -xzf tea_management_sprint8_completo.tar.gz
cd tea_management
```

### 2. Crear Datos de Prueba

```bash
python manage.py shell
```

```python
# En el shell de Django:
from apps.grupos.models import GrupoTerapeutico, AsignacionGrupo
from apps.procedimientos.models import Paciente
from datetime import time

# Crear grupos de prueba
grupos = [
    GrupoTerapeutico.objects.create(
        nombre="Grupo 9:00 a.m.",
        hora_inicio=time(9, 0),
        hora_fin=time(11, 0),
        dias_disponibles=["L", "M", "X", "J", "V"],
        capacidad_maxima=10,
        activo=True
    ),
    GrupoTerapeutico.objects.create(
        nombre="Grupo 2:00 p.m.",
        hora_inicio=time(14, 0),
        hora_fin=time(16, 0),
        dias_disponibles=["L", "X", "V"],
        capacidad_maxima=8,
        activo=True
    ),
    GrupoTerapeutico.objects.create(
        nombre="Grupo 4:00 p.m.",
        hora_inicio=time(16, 0),
        hora_fin=time(18, 0),
        dias_disponibles=["M", "J"],
        capacidad_maxima=6,
        activo=True
    )
]

print("✅ Grupos creados!")
exit()
```

### 3. Iniciar Servidor
```bash
python manage.py runserver
```

---

## 🧪 Rutas para Probar

### 1. Lista de Grupos
```
http://localhost:8000/grupos/
```
**Debe mostrar:**
- 4 cards de estadísticas
- 3 grupos en cards
- Barras de ocupación
- Botón "Crear Grupo"

---

### 2. Dashboard
```
http://localhost:8000/grupos/dashboard/
```
**Debe mostrar:**
- Métricas generales
- Gráfico de ocupación
- Lista de grupos activos
- Alertas (si hay pendientes)

---

### 3. Detalle de Grupo
```
http://localhost:8000/grupos/1/
```
**Debe mostrar:**
- Info del grupo
- Calendario semanal
- Lista de pacientes (vacía inicialmente)
- Botones de acción

---

### 4. Crear Nuevo Grupo
```
http://localhost:8000/grupos/crear/
```
**Debe mostrar:**
- Formulario en 4 secciones
- Checkboxes para días
- Validación de campos
- Botones guardar/cancelar

---

### 5. Lista de Pendientes
```
http://localhost:8000/grupos/pendientes/
```
**Debe mostrar:**
- Estadísticas por prioridad
- Tabla de pendientes (vacía inicialmente)
- Filtros
- Estado vacío positivo

---

## ✅ Checklist Visual

### Vista: Lista de Grupos
- [ ] Se muestran los 3 grupos creados
- [ ] Cards tienen colores correctos
- [ ] Barras de progreso funcionan
- [ ] Badges de estado visibles
- [ ] Días disponibles muestran correctamente
- [ ] Botones de acción funcionan

### Vista: Detalle de Grupo
- [ ] Información completa del grupo
- [ ] Calendario semanal visual
- [ ] Días disponibles resaltados
- [ ] Barra de ocupación muestra 0%
- [ ] Mensaje "No hay pacientes"
- [ ] Botón "Asignar Paciente" funciona

### Vista: Formulario
- [ ] Todos los campos se muestran
- [ ] Checkboxes de días funcionan
- [ ] Validación de horarios funciona
- [ ] Campos obligatorios marcados
- [ ] Botones de acción funcionan

### Vista: Dashboard
- [ ] 4 cards de métricas muestran datos
- [ ] Progress bar de ocupación
- [ ] Lista de grupos visible
- [ ] Sin alertas (todo OK)

---

## 🎨 Verificar Estilos

### Colores
- ✅ Azul (primary): Títulos, botones principales
- ✅ Verde (success): Disponible, activo
- ✅ Amarillo (warning): Advertencias
- ✅ Rojo (danger): Lleno, urgente

### Iconos
- ✅ Bootstrap Icons cargando
- ✅ Iconos en botones
- ✅ Iconos en headers
- ✅ Iconos en badges

### Responsive
- ✅ Desktop (3 columnas): OK
- ✅ Tablet (2 columnas): OK
- ✅ Mobile (1 columna): OK

---

## 🐛 Solución de Problemas

### Error: "Template does not exist"
**Causa:** Templates no en la ruta correcta

**Solución:**
```bash
# Verificar que existan:
ls templates/grupos/
# Debe mostrar: grupo_list.html, grupo_detail.html, etc.
```

---

### Error: 404 en /grupos/
**Causa:** URLs no incluidas

**Solución:**
```python
# En config/urls.py verificar:
path('grupos/', include('apps.grupos.urls')),
```

---

### Error: Estilos no cargan
**Causa:** Static files no configurados

**Solución:**
```bash
python manage.py collectstatic --noinput
```

---

### Error: "No such table: grupos_grupoterapeutico"
**Causa:** Migraciones no aplicadas

**Solución:**
```bash
python manage.py migrate grupos
```

---

## 📸 Screenshots Esperados

### Lista de Grupos
```
┌────────────────────────────────────┐
│ Grupos Terapéuticos                │
├────────────────────────────────────┤
│ [4 cards de estadísticas]          │
├────────────────────────────────────┤
│ [Filtros de búsqueda]              │
├────────────────────────────────────┤
│ [Card] [Card] [Card]               │
│ Grupo  Grupo  Grupo                │
│ 9am    2pm    4pm                  │
│ ████   ████   ████                 │
│ 0%     0%     0%                   │
└────────────────────────────────────┘
```

### Detalle de Grupo
```
┌──────────────────┬──────────────────┐
│ Info del Grupo   │ Pacientes        │
│ ─────────────    │ ─────────────    │
│ Horario: 9-11    │ ┌──────────────┐ │
│ Días: L M X J V  │ │ No hay       │ │
│ Capacidad: 0/10  │ │ pacientes    │ │
│ ████ 0%          │ │ asignados    │ │
│                  │ └──────────────┘ │
│ Calendario       │ [Asignar]        │
│ [L] [M] [X]...   │                  │
└──────────────────┴──────────────────┘
```

---

## ✨ Próximos Pasos

### 1. Asignar Paciente
- Ir a "Asignar Paciente"
- Seleccionar paciente existente
- Elegir grupo
- Configurar días
- Guardar

### 2. Ver Lista de Pendientes
- Si un paciente no tiene cupo
- Aparecerá automáticamente en pendientes
- Se puede asignar desde allí

### 3. Dashboard en Acción
- Crear más grupos
- Asignar pacientes
- Ver métricas actualizarse
- Recibir alertas

---

## 🎯 Test Completo

```bash
# 1. Crear grupo
curl -X POST http://localhost:8000/grupos/crear/

# 2. Ver lista
curl http://localhost:8000/grupos/

# 3. Ver detalle
curl http://localhost:8000/grupos/1/

# 4. Ver dashboard
curl http://localhost:8000/grupos/dashboard/

# ✅ Todas deben retornar 200 OK
```

---

## 🎉 ¡Listo!

Si todo funciona, deberías tener:
- ✅ Sistema visual completo
- ✅ Navegación fluida
- ✅ Formularios funcionales
- ✅ Estadísticas en tiempo real
- ✅ Diseño profesional

**¡El sistema de grupos está 100% operativo!** 🚀
