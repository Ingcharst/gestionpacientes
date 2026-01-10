# Sistema de Gestión - Centro TEA

## 🎯 Descripción
Sistema web para gestión integral de pacientes, terapias y procedimientos en centro especializado en Trastorno del Espectro Autista (TEA) y condiciones del neurodesarrollo.

## 🛠️ Stack Tecnológico
- **Backend**: Django 5.0+
- **Base de Datos**: MySQL 8.0+
- **Frontend**: Django Templates + Bootstrap 5 + HTMX
- **API**: Django REST Framework

## 📦 Estructura del Proyecto
```
tea_management/
├── config/                 # Configuración principal
├── apps/
│   ├── usuarios/          # Gestión de usuarios y roles
│   ├── consultorios/      # Gestión de consultorios
│   ├── terapias/          # Catálogo de terapias
│   └── procedimientos/    # Procedimientos terapéuticos
├── static/                # Archivos estáticos
├── templates/             # Templates globales
└── requirements.txt
```

## 🚀 Metodología de Desarrollo
**Scrum/Agile** - Desarrollo por sprints iterativos

### Sprint 1: Fundamentos y Autenticación ✅
- Modelos: Usuario, Rol, Perfil
- Autenticación y autorización
- CRUD de usuarios

### Sprint 2: Consultorios y Espacios (Próximo)
- Modelos: Consultorio, Sala
- Gestión de espacios físicos

### Sprint 3: Catálogo de Terapias (Futuro)
- Modelos: Categoría, Terapia, Procedimiento
- Catálogo maestro completo

## 📝 Instalación

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos en .env
cp .env.example .env

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Cargar datos iniciales
python manage.py loaddata fixtures/initial_data.json

# Ejecutar servidor
python manage.py runserver
```

## 🔐 Seguridad
- Autenticación JWT
- Control de acceso basado en roles (RBAC)
- Validación de datos de entrada
- Protección CSRF
- Encriptación de datos sensibles

## 📊 Roles del Sistema
- **ADMIN**: Acceso total al sistema
- **COORDINADOR**: Gestión de terapias y asignaciones
- **TERAPEUTA**: Registro de sesiones y procedimientos
- **RECEPCIONISTA**: Gestión de citas básicas

## 🧪 Testing
```bash
python manage.py test
```

## 📄 Licencia
Propietario - Centro de Atención TEA
