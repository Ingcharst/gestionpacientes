# 🛠️ GUÍA DE INSTALACIÓN - Módulo de Usuarios

## ✅ CORRECCIÓN APLICADA
**Error corregido**: En `partials/usuario_table.html` cambié `usuario.perfil.foto` por `usuario.foto_perfil`

---

## 📦 ARCHIVOS A INSTALAR

### 1. Descargar templates_usuarios.zip
Descarga el archivo desde: [templates_usuarios.zip](computer:///mnt/user-data/outputs/templates_usuarios.zip)

### 2. Extraer en tu proyecto
```bash
# Desde la raíz de tu proyecto tea_management
unzip templates_usuarios.zip -d templates/
```

O manualmente:
```
tea_management/
└── templates/
    └── usuarios/
        ├── usuario_list.html
        ├── usuario_detail.html
        ├── usuario_form.html
        ├── perfil_form.html
        └── partials/
            ├── usuario_table.html
            └── usuario_estado_badge.html
```

---

## 🔍 VERIFICACIÓN DE URLs Y VISTAS

### ✅ URLs ya configuradas correctamente
Tu archivo `apps/usuarios/urls.py` ya tiene las rutas correctas:

```python
urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Gestión de usuarios
    path('usuarios/', views.usuario_list, name='usuario_list'),
    path('usuarios/crear/', views.usuario_create, name='usuario_create'),
    path('usuarios/<int:pk>/', views.usuario_detail, name='usuario_detail'),
    path('usuarios/<int:pk>/editar/', views.usuario_update, name='usuario_update'),
    path('usuarios/<int:pk>/toggle-estado/', views.usuario_toggle_estado, name='usuario_toggle_estado'),
    
    # Perfil
    path('perfil/<int:pk>/editar/', views.perfil_update, name='perfil_update'),
]
```

### ✅ Vistas ya implementadas correctamente
Tu archivo `apps/usuarios/views.py` ya tiene todas las vistas necesarias:
- ✅ `usuario_list()` 
- ✅ `usuario_detail()`
- ✅ `usuario_create()`
- ✅ `usuario_update()`
- ✅ `perfil_update()`
- ✅ `usuario_toggle_estado()`

**NO NECESITAS CAMBIAR NADA EN VIEWS.PY NI URLS.PY** ✅

---

## 🧪 TESTING PASO A PASO

### 1. Verificar instalación
```bash
python manage.py runserver
```

### 2. Acceder a las rutas

**a) Lista de usuarios:**
```
http://localhost:8000/usuarios/
```
- Debe mostrar la lista de usuarios
- Los filtros deben funcionar
- La búsqueda debe actualizar sin reload (HTMX)

**b) Detalle de usuario:**
```
http://localhost:8000/usuarios/1/
```
- Debe mostrar la foto de perfil (o icono si no hay)
- Los tabs deben funcionar
- La información debe mostrarse correctamente

**c) Crear usuario (solo admin):**
```
http://localhost:8000/usuarios/crear/
```
- El formulario debe mostrarse completo
- La validación debe funcionar

**d) Editar usuario:**
```
http://localhost:8000/usuarios/1/editar/
```
- Los datos deben cargarse en el formulario
- Debe poder actualizar

**e) Editar perfil:**
```
http://localhost:8000/perfil/1/editar/
```
- Debe mostrar el formulario de perfil profesional
- Debe poder actualizar especialidades, etc.

---

## 🐛 SOLUCIÓN DE PROBLEMAS COMUNES

### Error: Template no encontrado
```bash
# Verificar que la carpeta está en el lugar correcto
ls templates/usuarios/
```
Debe mostrar: `usuario_list.html`, `usuario_detail.html`, etc.

### Error: AttributeError 'Perfil' has no attribute 'foto'
**YA CORREGIDO** ✅ - Ahora usa `usuario.foto_perfil`

### Error: CSRF token missing
Asegúrate que en `base.html` tengas:
```html
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
<script>
    document.body.addEventListener('htmx:configRequest', (event) => {
        event.detail.headers['X-CSRFToken'] = '{{ csrf_token }}';
    });
</script>
```

### Error: Bootstrap no carga
Verifica que en `base.html` tengas:
```html
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
```

---

## 📝 CHECKLIST DE VERIFICACIÓN

Antes de reportar errores, verifica:

- [ ] Los templates están en `templates/usuarios/`
- [ ] Las vistas en `views.py` están completas
- [ ] Las URLs en `urls.py` están configuradas
- [ ] Bootstrap 5 está cargado en `base.html`
- [ ] HTMX está cargado en `base.html`
- [ ] Bootstrap Icons está cargado
- [ ] El usuario está autenticado al probar
- [ ] Tienes permisos (admin para crear/toggle estado)

---

## 🎯 URLs COMPLETAS DEL MÓDULO

Si accedes desde el navegador:

```
/ → Dashboard (dashboard)
/login/ → Login
/logout/ → Logout
/usuarios/ → Lista de usuarios
/usuarios/crear/ → Crear usuario
/usuarios/<id>/ → Detalle de usuario
/usuarios/<id>/editar/ → Editar usuario
/usuarios/<id>/toggle-estado/ → Cambiar estado (HTMX POST)
/perfil/<id>/editar/ → Editar perfil profesional
```

---

## 📞 SOPORTE

Si después de seguir estos pasos sigues teniendo errores:
1. Copia el error exacto que aparece
2. Indica en qué URL ocurre
3. Comparte el traceback completo de Django

---

**Fecha de corrección**: 17/11/2025
**Estado**: ✅ LISTO PARA USAR
