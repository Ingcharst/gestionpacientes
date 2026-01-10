# 📁 ÍNDICE DE ARCHIVOS - Sistema TEA Management

## 📚 Archivos de Documentación

### Documentación Principal
- **README.md** - Documentación completa del proyecto
- **RESUMEN_EJECUTIVO.md** - Resumen ejecutivo y visión general
- **SPRINT_1_REVIEW.md** - Review detallado del Sprint 1
- **INICIO_RAPIDO.md** - Guía rápida de instalación y setup
- **INDICE_ARCHIVOS.md** - Este archivo (índice completo)

---

## ⚙️ Configuración del Proyecto

### Archivos de Configuración
- **manage.py** - CLI principal de Django
- **requirements.txt** - Lista de dependencias Python
- **.env.example** - Plantilla de variables de entorno
- **.gitignore** - Archivos ignorados por Git
- **install.sh** - Script de instalación automatizada (ejecutable)

### Configuración Django (config/)
- **config/__init__.py** - Inicializador del paquete
- **config/settings.py** - Configuración principal de Django
- **config/urls.py** - URLs principales del proyecto
- **config/wsgi.py** - Configuración WSGI para deployment
- **config/asgi.py** - Configuración ASGI para deployment asíncrono

---

## 🎯 Aplicaciones del Proyecto

### apps/ - Directorio de Aplicaciones
- **apps/__init__.py** - Inicializador del paquete apps

---

### 📦 App: USUARIOS (✅ Completado - Sprint 1)

#### Archivos Principales
- **apps/usuarios/__init__.py** - Configuración del paquete
- **apps/usuarios/apps.py** - Configuración de la aplicación
- **apps/usuarios/models.py** - Modelos: Usuario, Perfil, RegistroAcceso
- **apps/usuarios/admin.py** - Configuración del admin de Django
- **apps/usuarios/views.py** - Vistas del frontend (8 vistas)
- **apps/usuarios/forms.py** - Formularios de Django (5 forms)
- **apps/usuarios/urls.py** - URLs del frontend
- **apps/usuarios/signals.py** - Signals para creación automática de perfil
- **apps/usuarios/tests.py** - Suite de tests (30+ test cases)

#### API REST (apps/usuarios/api/)
- **apps/usuarios/api/__init__.py** - Inicializador del paquete API
- **apps/usuarios/api/serializers.py** - 8 serializadores para la API
- **apps/usuarios/api/views.py** - 3 ViewSets con 20+ endpoints
- **apps/usuarios/api/permissions.py** - 4 permisos personalizados
- **apps/usuarios/api/urls.py** - URLs de la API REST

---

### 📦 App: CONSULTORIOS (⏳ Pendiente - Sprint 2)

- **apps/consultorios/__init__.py** - Estructura preparada para Sprint 2

**Contenido futuro:**
- models.py (Consultorio, Sala)
- admin.py (Panel admin)
- views.py (Vistas frontend)
- forms.py (Formularios)
- urls.py (URLs)
- tests.py (Tests)
- api/ (API REST)

---

### 📦 App: TERAPIAS (⏳ Pendiente - Sprint 3)

- **apps/terapias/__init__.py** - Estructura preparada para Sprint 3

**Contenido futuro:**
- models.py (Categoría, Terapia, TipoTerapia)
- admin.py (Panel admin)
- views.py (Vistas frontend)
- forms.py (Formularios)
- urls.py (URLs)
- tests.py (Tests)
- api/ (API REST)

---

### 📦 App: PROCEDIMIENTOS (⏳ Pendiente - Sprint 4)

- **apps/procedimientos/__init__.py** - Estructura preparada para Sprint 4

**Contenido futuro:**
- models.py (Procedimiento, Sesión, Registro)
- admin.py (Panel admin)
- views.py (Vistas frontend)
- forms.py (Formularios)
- urls.py (URLs)
- tests.py (Tests)
- api/ (API REST)

---

## 🎨 Frontend (Pendiente)

### templates/ - Plantillas Django
**Estado**: Estructura creada, templates pendientes para Sprint 2

**Templates necesarios:**
- base.html
- usuarios/
  - login.html
  - dashboard.html
  - usuario_list.html
  - usuario_detail.html
  - usuario_form.html
  - perfil_form.html
  - partials/
    - usuario_table.html
    - usuario_estado_badge.html

---

### static/ - Archivos Estáticos
**Estado**: Estructura creada

**Subdirectorios:**
- static/css/ - Archivos CSS
- static/js/ - Archivos JavaScript
- static/img/ - Imágenes del sitio

---

## 📂 Directorios de Datos

### media/ - Archivos Subidos
**Estado**: Directorio creado

**Subdirectorios:**
- media/usuarios/fotos/ - Fotos de perfil de usuarios

---

### logs/ - Logs del Sistema
**Estado**: Directorio creado

**Archivos de logs:**
- django.log (se crea automáticamente)

---

## 📊 Estadísticas del Proyecto

### Archivos por Tipo
```
📝 Python (.py):           18 archivos
📄 Markdown (.md):         5 archivos  
⚙️  Configuración:         4 archivos
🔧 Scripts:                1 archivo (install.sh)
📁 Directorios:           15 directorios
```

### Distribución por Módulo
```
config/                    5 archivos
apps/usuarios/            9 archivos
apps/usuarios/api/        5 archivos
apps/consultorios/        1 archivo (preparado)
apps/terapias/            1 archivo (preparado)
apps/procedimientos/      1 archivo (preparado)
Raíz del proyecto        10 archivos
```

### Líneas de Código
```
Total estimado:           ~3,500 líneas
Python:                   ~3,200 líneas
Documentación:            ~300 líneas
```

---

## 🔍 Guía de Navegación Rápida

### Para Empezar
1. **README.md** - Lee esto primero
2. **INICIO_RAPIDO.md** - Guía de instalación
3. **install.sh** - Ejecuta para instalación automática

### Para Desarrolladores
1. **apps/usuarios/models.py** - Ver modelos de ejemplo
2. **apps/usuarios/api/views.py** - Ver ViewSets de ejemplo
3. **apps/usuarios/tests.py** - Ver tests de ejemplo
4. **config/settings.py** - Configuración del proyecto

### Para Administradores
1. **RESUMEN_EJECUTIVO.md** - Visión general del proyecto
2. **SPRINT_1_REVIEW.md** - Estado actual y roadmap
3. **.env.example** - Variables de configuración

### Para Testing
1. **apps/usuarios/tests.py** - Ejecutar: `python manage.py test`
2. **requirements.txt** - Instalar: `pip install -r requirements.txt`

---

## 📝 Convenciones de Nombres

### Archivos Python
- **models.py** - Modelos de base de datos
- **views.py** - Vistas del frontend
- **forms.py** - Formularios de Django
- **admin.py** - Configuración del admin
- **urls.py** - Rutas URL
- **tests.py** - Tests unitarios
- **signals.py** - Signals de Django

### API REST
- **serializers.py** - Serializadores DRF
- **permissions.py** - Permisos personalizados
- **api/views.py** - ViewSets de la API
- **api/urls.py** - URLs de la API

---

## 🎯 Siguiente Archivo a Crear (Sprint 2)

```
apps/consultorios/models.py
├── Consultorio
├── Sala
└── DisponibilidadSala
```

---

## 📦 Dependencias Principales

Instaladas en `requirements.txt`:
- Django 5.0
- djangorestframework
- mysqlclient
- djangorestframework-simplejwt
- django-cors-headers
- django-crispy-forms
- crispy-bootstrap5
- django-htmx
- pytest-django
- drf-spectacular

---

## 🔗 Enlaces Útiles

### Documentación
- Django: https://docs.djangoproject.com/
- DRF: https://www.django-rest-framework.org/
- MySQL: https://dev.mysql.com/doc/

### API Docs (cuando el servidor está corriendo)
- Swagger: http://127.0.0.1:8000/api/docs/
- ReDoc: http://127.0.0.1:8000/api/redoc/
- Schema: http://127.0.0.1:8000/api/schema/

---

## ✅ Checklist de Archivos Críticos

### Configuración
- [✅] manage.py
- [✅] requirements.txt
- [✅] .env.example
- [✅] config/settings.py
- [✅] config/urls.py

### App Usuarios
- [✅] models.py (3 modelos)
- [✅] admin.py (3 admins)
- [✅] views.py (8 vistas)
- [✅] forms.py (5 formularios)
- [✅] tests.py (30+ tests)
- [✅] api/serializers.py (8 serializers)
- [✅] api/views.py (3 ViewSets)
- [✅] api/permissions.py (4 permisos)

### Documentación
- [✅] README.md
- [✅] SPRINT_1_REVIEW.md
- [✅] INICIO_RAPIDO.md
- [✅] RESUMEN_EJECUTIVO.md
- [✅] INDICE_ARCHIVOS.md

---

## 🚀 Comandos Útiles por Archivo

### manage.py
```bash
python manage.py runserver        # Iniciar servidor
python manage.py test             # Ejecutar tests
python manage.py makemigrations   # Crear migraciones
python manage.py migrate          # Aplicar migraciones
python manage.py createsuperuser  # Crear admin
python manage.py shell            # Shell interactivo
```

### install.sh
```bash
chmod +x install.sh    # Dar permisos
./install.sh           # Ejecutar instalación
```

### tests.py
```bash
python manage.py test apps.usuarios                    # Tests de usuarios
python manage.py test apps.usuarios.tests.UsuarioModelTest  # Test específico
```

---

## 📊 Métricas por Archivo

### Archivos Más Grandes
1. **config/settings.py** (~250 líneas)
2. **apps/usuarios/models.py** (~240 líneas)
3. **apps/usuarios/api/views.py** (~230 líneas)
4. **apps/usuarios/api/serializers.py** (~220 líneas)
5. **apps/usuarios/tests.py** (~200 líneas)

### Archivos Más Importantes
1. **config/settings.py** - Configuración central
2. **apps/usuarios/models.py** - Modelos core
3. **apps/usuarios/api/views.py** - Lógica de API
4. **README.md** - Documentación principal
5. **manage.py** - CLI principal

---

## 🎯 Roadmap de Archivos Futuros

### Sprint 2 (Próximo)
- apps/consultorios/models.py
- apps/consultorios/admin.py
- apps/consultorios/views.py
- apps/consultorios/forms.py
- apps/consultorios/api/

### Sprint 3
- apps/terapias/models.py
- apps/terapias/admin.py
- apps/terapias/api/

### Sprint 4
- apps/procedimientos/models.py
- apps/procedimientos/admin.py
- apps/procedimientos/api/

---

**Última actualización**: Sprint 1 Completado  
**Total de archivos**: 28 archivos Python + 5 documentos + 1 script  
**Estado**: ✅ Sprint 1 Completado - Listo para Sprint 2
