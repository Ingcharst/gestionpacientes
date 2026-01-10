# 📁 Templates del Módulo de Usuarios - Sprint 6

## ✅ Archivos Creados (6 templates)

### Templates Principales
1. **usuario_list.html** - Lista de usuarios con filtros y búsqueda HTMX
2. **usuario_detail.html** - Vista detallada de usuario con tabs (Info, Perfil, Accesos)
3. **usuario_form.html** - Formulario para crear/editar usuario
4. **perfil_form.html** - Formulario para editar perfil profesional

### Templates Parciales (HTMX)
5. **partials/usuario_table.html** - Tabla de usuarios para actualización dinámica
6. **partials/usuario_estado_badge.html** - Badge de estado para toggle dinámico

---

## 📋 Características Implementadas

### ✨ usuario_list.html
- Lista completa de usuarios del sistema
- Filtros por rol, estado y búsqueda en tiempo real (HTMX)
- Tabla responsive con información clave
- Botón "Nuevo Usuario" (solo para administradores)
- Contador de usuarios total
- Acciones: Ver detalle, Editar, Cambiar estado

### 👤 usuario_detail.html
- Vista en tabs con 3 secciones:
  - **Info General**: Datos personales y del sistema
  - **Perfil Profesional**: Especialidades, certificaciones, biografía
  - **Historial**: Últimos 20 accesos al sistema
- Card lateral con foto de perfil y datos principales
- Badges visuales para rol y estado
- Botones de edición contextuales

### 📝 usuario_form.html
- Formulario completo organizado en 3 secciones:
  - **Información de Cuenta**: Username, email, contraseñas
  - **Información Personal**: Nombre, apellido, teléfono, cédula, foto
  - **Información Laboral**: Rol, estado, fecha contratación, notas
- Validación frontend y backend
- Upload de foto de perfil con preview
- Campos condicionales (contraseñas solo en creación)

### 🎓 perfil_form.html
- Formulario de perfil profesional en 3 secciones:
  - **Especialidades**: Principal y secundarias
  - **Formación Académica**: Universidad, experiencia, certificaciones
  - **Información Profesional**: Biografía, horario, disponibilidad
- Checkbox de disponibilidad para asignaciones
- Información de auditoría (fechas de creación/actualización)

### ⚡ Componentes HTMX
- **usuario_table.html**: Actualización dinámica de la tabla sin reload
- **usuario_estado_badge.html**: Toggle de estado con HTMX

---

## 🎨 Diseño y UX

- ✅ Bootstrap 5 responsive
- ✅ Bootstrap Icons integrados
- ✅ Badges de colores por rol:
  - Administrador: Rojo (`bg-danger`)
  - Terapeuta: Azul (`bg-primary`)
  - Coordinador: Amarillo (`bg-warning`)
  - Otros: Gris (`bg-secondary`)
- ✅ Estados visuales con badges
- ✅ Tabs de navegación en detalle
- ✅ Cards con sombras
- ✅ Formularios con fieldsets organizados

---

## 📦 Instrucciones de Instalación

### 1. Copiar templates
```bash
# Desde la raíz del proyecto
cp -r usuarios/ tea_management/templates/
```

### 2. Verificar estructura
```
templates/
└── usuarios/
    ├── usuario_list.html
    ├── usuario_detail.html
    ├── usuario_form.html
    ├── perfil_form.html
    └── partials/
        ├── usuario_table.html
        └── usuario_estado_badge.html
```

### 3. Verificar URLs
Las vistas ya están configuradas en `apps/usuarios/views.py` y esperan estos templates:
- `usuario_list` → `usuarios/usuario_list.html`
- `usuario_detail` → `usuarios/usuario_detail.html`
- `usuario_create/update` → `usuarios/usuario_form.html`
- `perfil_update` → `usuarios/perfil_form.html`

---

## 🧪 Testing Manual

### Lista de Usuarios
- [ ] Filtro por rol funciona
- [ ] Filtro por estado funciona
- [ ] Búsqueda en tiempo real (HTMX)
- [ ] Botón "Nuevo Usuario" visible solo para admin
- [ ] Links a detalle funcionan
- [ ] Links a edición funcionan
- [ ] Toggle de estado funciona (HTMX)

### Detalle de Usuario
- [ ] Foto de perfil se muestra correctamente
- [ ] Badges de rol y estado correctos
- [ ] Tabs de navegación funcionan
- [ ] Historial de accesos se muestra
- [ ] Botones de edición contextuales
- [ ] Link "Volver a lista" funciona

### Formularios
- [ ] Validación frontend funciona
- [ ] Upload de foto funciona
- [ ] Formulario de creación guarda correctamente
- [ ] Formulario de edición actualiza datos
- [ ] Perfil profesional se actualiza
- [ ] Botón cancelar funciona

---

## 🔐 Permisos Implementados

- **Lista**: Todos los usuarios autenticados
- **Detalle**: Todos los usuarios autenticados
- **Crear**: Solo administradores
- **Editar Usuario**: Administrador o el mismo usuario
- **Editar Perfil**: Administrador o el mismo usuario
- **Toggle Estado**: Solo administradores (no se puede desactivar a sí mismo)

---

## 📊 Próximos Pasos

El módulo de **Usuarios** está completo. Continuar con:
1. ✅ Módulo de Usuarios (COMPLETADO)
2. 🔄 Módulo de Terapias (siguiente)
3. ⏳ Módulo de Consultorios
4. ⏳ Módulo de Procedimientos

---

## 📝 Notas Técnicas

- Los templates usan el sistema de mensajes de Django (`messages`)
- HTMX está configurado con CSRF token incluido
- Los formularios usan clases Bootstrap mediante JavaScript
- Las imágenes de perfil tienen fallback a icono cuando no hay foto
- Los badges de estado se actualizan dinámicamente sin reload
- Los tabs usan Bootstrap 5 native (sin jQuery)

**Estado: COMPLETO ✅**
**Fecha: 17/11/2025**
