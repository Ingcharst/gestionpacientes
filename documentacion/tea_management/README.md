# TEA Management System - Sprint 5: Frontend MVP

## ✅ Sprint 5 Completado

### Implementaciones del Sprint:
- ✅ Sistema de autenticación visual (Login/Logout)
- ✅ Dashboard principal con estadísticas
- ✅ CRUD completo de pacientes con interfaz responsive
- ✅ Templates base con Bootstrap 5 y HTMX
- ✅ Navegación lateral con sidebar
- ✅ Sistema de mensajes flash
- ✅ Paginación y filtros con HTMX

### Estructura de Templates
```
templates/
├── base/
│   └── base.html          # Template base con sidebar y navbar
├── auth/
│   ├── login.html         # Página de login
│   └── dashboard.html     # Dashboard principal
├── pacientes/
│   ├── lista.html         # Lista de pacientes
│   ├── formulario.html    # Formulario crear/editar
│   ├── detalle.html       # Detalle del paciente
│   └── table.html         # Tabla parcial para HTMX
└── components/            # (Para futuras expansiones)
```

## 🚀 Cómo Ejecutar

### 1. Crear Entorno Virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Instalar Dependencias
```bash
pip install django==5.2.7
pip install mysqlclient
pip install python-decouple
pip install django-jazzmin
pip install djangorestframework
pip install djangorestframework-simplejwt
pip install django-cors-headers
pip install django-filter
pip install django-crispy-forms
pip install crispy-bootstrap5
pip install django-extensions
pip install django-htmx
pip install drf-spectacular
pip install whitenoise
pip install Pillow
```

### 3. Configurar Base de Datos
Crear archivo `.env` en la raíz del proyecto:
```env
DEBUG=True
SECRET_KEY=tu-clave-secreta
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=tea_management
DB_USER=root
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=3306
```

### 4. Crear Base de Datos MySQL
```sql
CREATE DATABASE tea_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Ejecutar Migraciones
```bash
python manage.py migrate
```

### 6. Crear Superusuario
```bash
python manage.py createsuperuser
```

### 7. Cargar Datos de Prueba (Opcional)
```bash
# Crear algunos datos de ejemplo manualmente desde el admin
# O usar el shell:
python manage.py shell
```

```python
from apps.usuarios.models import Usuario
from apps.terapias.models import CategoriaTerapia, Terapia
from apps.consultorios.models import Consultorio
from apps.procedimientos.models import Paciente
from datetime import date
from decimal import Decimal

# Crear usuarios
terapeuta = Usuario.objects.create_user(
    username='terapeuta1',
    password='password123',
    first_name='María',
    last_name='García',
    email='maria@example.com',
    rol='TERAPEUTA'
)

# Crear categoría y terapia
categoria = CategoriaTerapia.objects.create(
    nombre='Terapia del Lenguaje',
    codigo='TL',
    descripcion='Terapias enfocadas en lenguaje y comunicación'
)

terapia = Terapia.objects.create(
    nombre='Terapia del Lenguaje Individual',
    codigo='TLI-001',
    categoria=categoria,
    descripcion='Terapia individual para lenguaje',
    especialidad='LENGUAJE',
    modalidad='INDIVIDUAL',
    duracion_minutos=45,
    costo_sesion=Decimal('80000.00'),
    activo=True
)

# Crear consultorio
consultorio = Consultorio.objects.create(
    nombre='Consultorio 1',
    codigo='C1',
    tipo='LENGUAJE',
    piso=1,
    numero='101',
    capacidad=2
)

# Crear paciente
paciente = Paciente.objects.create(
    nombres='Juan',
    apellidos='Pérez',
    tipo_documento='TI',
    numero_documento='1234567890',
    fecha_nacimiento=date(2015, 6, 15),
    genero='M',
    nombre_responsable='Ana Pérez',
    parentesco_responsable='Madre',
    telefono_responsable='3001234567',
    diagnostico_principal='TEA Nivel 2',
    numero_historia_clinica='HC-2024-001',
    creado_por=Usuario.objects.first()
)
```

### 8. Ejecutar Servidor
```bash
python manage.py runserver
```

### 9. Acceder al Sistema
- **Frontend**: http://localhost:8000/
- **Admin**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/docs/

## 🎨 Características del Frontend

### Login
- Diseño moderno con Bootstrap 5
- Validación de credenciales
- Registro de accesos
- Redirección al dashboard

### Dashboard
- 4 cards con estadísticas principales
- Lista de próximas sesiones del día
- Accesos rápidos a funciones comunes
- Sistema de notificaciones

### Gestión de Pacientes
- **Lista**: Tabla responsive con búsqueda y filtros (HTMX)
- **Crear**: Formulario completo con validaciones
- **Editar**: Actualización de datos
- **Detalle**: Vista completa con tabs (Info, Médica, Sesiones)

### Sidebar
- Navegación intuitiva
- Indicador de página activa
- Links a todos los módulos
- Responsive (se oculta en móvil)

### Tecnologías Frontend
- **Bootstrap 5.3.2**: Framework CSS
- **HTMX 1.9.10**: Interactividad sin JavaScript
- **Bootstrap Icons**: Iconografía
- **CSS Custom**: Estilos personalizados

## 📋 Próximos Sprints

### Sprint 6: Frontend Avanzado
- ✅ Gestión de terapias (frontend)
- ✅ Gestión de consultorios (frontend)
- ✅ Agendamiento de sesiones
- ✅ Reportes básicos

### Sprint 7: Módulos Adicionales
- ⏳ Sistema de facturación
- ⏳ Control de inventario
- ⏳ Generación de reportes PDF
- ⏳ Dashboard analítico

## 🎓 Para Estudiantes SENA

Este proyecto implementa:
- Metodología Agile/Scrum
- Django MVT (Model-View-Template)
- REST API con Django REST Framework
- Autenticación JWT
- HTMX para SPA-like experience
- Bootstrap 5 para diseño responsive
- MySQL como base de datos
- Buenas prácticas de código

## 📝 Notas Importantes

1. **HTMX**: Permite actualizaciones parciales sin recargar página
2. **Sidebar**: Fixed en desktop, colapsable en móvil
3. **Filtros**: Se procesan con HTMX para mejor UX
4. **Mensajes**: Sistema de flash messages de Django
5. **Validaciones**: Frontend (HTML5) + Backend (Django)

## 🐛 Troubleshooting

**Error de conexión MySQL**:
```bash
pip install mysqlclient
# O en Windows: descargar .whl desde https://www.lfd.uci.edu/~gohlke/pythonlibs/
```

**Migrations conflict**:
```bash
python manage.py migrate --fake-initial
```

**HTMX no funciona**:
Verificar que el script esté cargando:
```html
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
```

## 👨‍🏫 Contacto
Instructor: Carlos - SENA
Programa: Análisis y Desarrollo de Sistemas de Información
