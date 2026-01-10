# 🚀 INICIO RÁPIDO - Sistema TEA Management

## ⚡ Pasos Rápidos para Comenzar

### 1️⃣ Preparación del Entorno (5 minutos)
```bash
# Navegar al proyecto
cd tea_management

# Crear y activar entorno virtual
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Instalar todas las dependencias
pip install -r requirements.txt
```

### 2️⃣ Configurar Base de Datos (3 minutos)
```bash
# Crear base de datos MySQL
mysql -u root -p
CREATE DATABASE tea_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Copiar archivo de configuración
cp .env.example .env

# Editar .env con tu información:
# DB_NAME=tea_management
# DB_USER=tu_usuario
# DB_PASSWORD=tu_contraseña
# DB_HOST=localhost
# DB_PORT=3306
# SECRET_KEY=(genera una nueva)
```

### 3️⃣ Inicializar el Proyecto (2 minutos)
```bash
# Crear tablas en la base de datos
python manage.py makemigrations
python manage.py migrate

# Crear usuario administrador
python manage.py createsuperuser
# Usuario: admin
# Email: admin@test.com
# Contraseña: (tu contraseña segura)
```

### 4️⃣ ¡Ejecutar! (1 minuto)
```bash
# Iniciar el servidor de desarrollo
python manage.py runserver

# El sistema estará disponible en:
# http://127.0.0.1:8000/
```

---

## 🌐 URLs Principales

Una vez el servidor esté corriendo:

### Frontend
- **Login**: http://127.0.0.1:8000/login/
- **Dashboard**: http://127.0.0.1:8000/ (requiere login)
- **Admin Django**: http://127.0.0.1:8000/admin/

### API REST
- **Documentación Swagger**: http://127.0.0.1:8000/api/docs/
- **Documentación ReDoc**: http://127.0.0.1:8000/api/redoc/
- **API Usuarios**: http://127.0.0.1:8000/api/usuarios/

### Obtener Token JWT
```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin", "password":"tu_contraseña"}'
```

---

## 🧪 Ejecutar Tests

```bash
# Todos los tests
python manage.py test

# Tests específicos de usuarios
python manage.py test apps.usuarios

# Con cobertura
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

---

## 📊 Estructura del Proyecto

```
tea_management/
│
├── 📁 config/                      # Configuración principal Django
│   ├── __init__.py
│   ├── settings.py                # ⚙️ Configuraciones
│   ├── urls.py                    # 🔗 URLs principales
│   ├── wsgi.py                    # 🚀 Deployment WSGI
│   └── asgi.py                    # 🚀 Deployment ASGI
│
├── 📁 apps/                        # Aplicaciones del proyecto
│   └── 📁 usuarios/               # ✅ SPRINT 1 COMPLETADO
│       ├── __init__.py
│       ├── apps.py                # Configuración app
│       ├── models.py              # 🗄️ Usuario, Perfil, RegistroAcceso
│       ├── admin.py               # 👨‍💼 Panel admin personalizado
│       ├── views.py               # 🎨 Vistas frontend (8 vistas)
│       ├── forms.py               # 📝 Formularios (5 forms)
│       ├── urls.py                # 🔗 URLs frontend
│       ├── signals.py             # 📡 Signals automáticos
│       ├── tests.py               # 🧪 Suite de tests (30+ tests)
│       │
│       └── 📁 api/                # API REST
│           ├── __init__.py
│           ├── serializers.py    # 🔄 8 serializadores
│           ├── views.py          # 🎯 3 ViewSets (20+ endpoints)
│           ├── permissions.py    # 🔐 4 permisos personalizados
│           └── urls.py           # 🔗 URLs API
│
├── 📁 templates/                  # (Pendiente Sprint 2)
├── 📁 static/                     # (Pendiente Sprint 2)
├── 📁 media/                      # Archivos subidos
├── 📁 logs/                       # Logs del sistema
│
├── 📄 manage.py                   # CLI de Django
├── 📄 requirements.txt            # Dependencias Python
├── 📄 .env.example                # Plantilla variables entorno
├── 📄 .gitignore                  # Git ignore
├── 📄 README.md                   # Documentación principal
├── 📄 SPRINT_1_REVIEW.md          # Review del Sprint 1
└── 📄 INICIO_RAPIDO.md           # ← Este archivo
```

---

## 🎯 Funcionalidades Disponibles (Sprint 1)

### ✅ Sistema de Autenticación
- Login/Logout
- Registro de usuarios (admin)
- Cambio de contraseña
- JWT tokens para API
- Auditoría de accesos

### ✅ Gestión de Usuarios
- CRUD completo de usuarios
- 6 roles disponibles: Admin, Coordinador, Terapeuta, Recepcionista, Médico, Psicólogo
- 3 estados: Activo, Inactivo, Suspendido
- Perfil profesional extendido
- Foto de perfil
- Cédula profesional

### ✅ API REST Completa
- 20+ endpoints
- Documentación Swagger/ReDoc
- Autenticación JWT
- Filtros y búsqueda
- Paginación automática
- Permisos por rol

### ✅ Panel de Administración
- Django Admin personalizado
- Filtros avanzados
- Búsqueda rápida
- Gestión de perfiles inline

---

## 📚 Próximos Pasos

Una vez tengas el sistema corriendo:

1. **Accede al admin**: http://127.0.0.1:8000/admin/
2. **Crea algunos usuarios de prueba** con diferentes roles
3. **Explora la API** en: http://127.0.0.1:8000/api/docs/
4. **Ejecuta los tests** para verificar que todo funciona
5. **Revisa SPRINT_1_REVIEW.md** para conocer todas las características

---

## 🆘 Solución de Problemas Comunes

### Error: "No module named 'MySQLdb'"
```bash
# Windows:
pip install mysqlclient

# Linux:
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
pip install mysqlclient

# Mac:
brew install mysql
pip install mysqlclient
```

### Error: "Access denied for user"
- Verifica las credenciales en el archivo `.env`
- Asegúrate de que MySQL esté corriendo
- Verifica los permisos del usuario de MySQL

### Error: "Secret key must not be empty"
- Copia `.env.example` a `.env`
- Genera un SECRET_KEY nuevo:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Los tests fallan
- Asegúrate de tener la base de datos configurada correctamente
- Verifica que todas las dependencias estén instaladas
- El usuario de MySQL debe tener permisos para crear bases de datos de prueba

---

## 💡 Tips Útiles

### Crear datos de prueba rápidamente
```bash
python manage.py shell

from apps.usuarios.models import Usuario

# Crear terapeuta
Usuario.objects.create_user(
    username='terapeuta1',
    email='terapeuta@test.com',
    password='Test123!',
    first_name='Ana',
    last_name='García',
    rol='TERAPEUTA'
)

# Crear coordinador
Usuario.objects.create_user(
    username='coord1',
    email='coord@test.com',
    password='Test123!',
    first_name='Carlos',
    last_name='López',
    rol='COORDINADOR'
)
```

### Ver todas las URLs disponibles
```bash
python manage.py show_urls
```

### Limpiar base de datos
```bash
python manage.py flush
```

---

## 📞 Siguiente Sprint

**Sprint 2**: Consultorios y Espacios
- Gestión de consultorios
- Asignación de espacios
- Disponibilidad de salas
- Relación terapeuta-consultorio

Ver `SPRINT_1_REVIEW.md` para más detalles.

---

## ✅ Checklist de Inicio

- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Base de datos MySQL creada
- [ ] Archivo `.env` configurado
- [ ] Migraciones ejecutadas (`python manage.py migrate`)
- [ ] Superusuario creado (`python manage.py createsuperuser`)
- [ ] Servidor corriendo (`python manage.py runserver`)
- [ ] Login exitoso en http://127.0.0.1:8000/admin/
- [ ] Tests pasando (`python manage.py test`)

---

**¡Listo para empezar a desarrollar! 🚀**

Para cualquier duda, revisa:
- `README.md` - Documentación completa
- `SPRINT_1_REVIEW.md` - Detalles del Sprint 1
- Django Docs: https://docs.djangoproject.com/
