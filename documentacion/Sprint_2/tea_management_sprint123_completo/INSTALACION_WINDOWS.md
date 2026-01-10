# 🚀 GUÍA RÁPIDA DE INSTALACIÓN - WINDOWS 10

## 📦 SPRINT 3 COMPLETADO: Catálogo de Terapias

**Sprints incluidos:**
- ✅ Sprint 1: Usuarios y Autenticación
- ✅ Sprint 2: Consultorios y Espacios
- ✅ Sprint 3: Catálogo de Terapias ← NUEVO

---

## 📋 REQUISITOS PREVIOS

### Software Necesario (Windows 10):
- ✅ Python 3.10 o superior
- ✅ MySQL 5.7.8 o superior
- ✅ Git (opcional)

---

## 🔧 INSTALACIÓN PASO A PASO

### 1. Extraer el ZIP

```
Clic derecho en tea_management_sprint123_completo.zip
→ Extraer todo
→ Seleccionar carpeta destino (ej: E:\TEA_Center)
```

### 2. Crear Entorno Virtual

Abrir PowerShell en la carpeta del proyecto:

```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\activate

# Verificar que esté activado (debe mostrar (venv) al inicio)
```

### 3. Instalar Dependencias

```powershell
# Instalar todos los paquetes
pip install -r requirements.txt

# Si hay error con python-decouple:
pip install python-decouple

# Si hay error con mysqlclient:
pip install mysqlclient
```

### 4. Configurar Base de Datos

#### Crear BD en MySQL:
```sql
-- Abrir MySQL Workbench o línea de comandos MySQL
CREATE DATABASE tea_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'tea_user'@'localhost' IDENTIFIED BY 'tea_password_2024';
GRANT ALL PRIVILEGES ON tea_management.* TO 'tea_user'@'localhost';
FLUSH PRIVILEGES;
```

#### Configurar archivo .env:
```powershell
# Copiar el ejemplo
copy .env.example .env

# Editar .env con Notepad o VS Code
notepad .env
```

Configurar:
```
SECRET_KEY=django-insecure-tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=tea_management
DB_USER=tea_user
DB_PASSWORD=tea_password_2024
DB_HOST=localhost
DB_PORT=3306
```

### 5. Actualizar settings.py

Abrir `config/settings.py` y verificar que esté:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'corsheaders',
    'crispy_forms',
    'crispy_bootstrap5',
    'drf_spectacular',
    
    # Local apps
    'apps.usuarios',
    'apps.consultorios',  # Sprint 2
    'apps.terapias',      # Sprint 3 ← NUEVO
    # 'apps.procedimientos',  # Sprint 4 (futuro)
]
```

### 6. Crear Migraciones

```powershell
# Crear migraciones para cada app
python manage.py makemigrations usuarios
python manage.py makemigrations consultorios
python manage.py makemigrations terapias

# Aplicar todas las migraciones
python manage.py migrate
```

### 7. Crear Superusuario

```powershell
python manage.py createsuperuser

# Seguir las instrucciones:
# Username: admin
# Email: admin@tea.com
# Password: ******** (tu password)
# Password (again): ********
```

### 8. Ejecutar Tests (Opcional pero Recomendado)

```powershell
# Tests de usuarios
python manage.py test apps.usuarios

# Tests de consultorios
python manage.py test apps.consultorios

# Tests de terapias
python manage.py test apps.terapias

# Todos los tests
python manage.py test
```

**Resultado esperado:** Todos los tests deben pasar ✅

### 9. Iniciar el Servidor

```powershell
python manage.py runserver
```

**Output esperado:**
```
System check identified no issues (0 silenced).
November 06, 2025 - 20:00:00
Django version X.X, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

## ✅ VERIFICACIÓN

### 1. Admin de Django
Abrir navegador: http://127.0.0.1:8000/admin/

Deberías ver:
- AUTHENTICATION AND AUTHORIZATION
- GESTIÓN DE USUARIOS ← Sprint 1
- GESTIÓN DE CONSULTORIOS ← Sprint 2
- CATÁLOGO DE TERAPIAS ← Sprint 3 ✨

### 2. API REST
Abrir: http://127.0.0.1:8000/api/docs/

Deberías ver documentación Swagger con todos los endpoints.

### 3. Crear Datos de Prueba

```python
# Abrir shell de Django
python manage.py shell

# Ejecutar:
from apps.terapias.models import CategoriaTerapia, Terapia
from decimal import Decimal

# Crear categoría
cat = CategoriaTerapia.objects.create(
    nombre='Terapia del Lenguaje',
    codigo='TL',
    descripcion='Terapias de comunicación',
    color='#007bff',
    orden=1
)

# Crear terapia
terapia = Terapia.objects.create(
    nombre='Terapia de Articulación',
    codigo='TA-001',
    categoria=cat,
    descripcion='Mejora articulación del habla',
    modalidad='INDIVIDUAL',
    especialidad='LENGUAJE',
    duracion_minutos=60,
    frecuencia_semanal_recomendada=2,
    costo_sesion=Decimal('150.00'),
    edad_minima=3,
    edad_maxima=12
)

print(f"✅ Terapia creada: {terapia.nombre}")
print(f"Duración: {terapia.duracion_formateada}")
print(f"Costo: {terapia.costo_formateado}")
```

---

## 🌐 ENDPOINTS DISPONIBLES

### Sprint 1: Usuarios
```
/api/usuarios/
/api/token/
/api/token/refresh/
```

### Sprint 2: Consultorios
```
/api/consultorios/
/api/consultorios/asignaciones/
/api/consultorios/disponibilidades/
```

### Sprint 3: Terapias ✨
```
/api/terapias/                           # Listar terapias
/api/terapias/categorias/                # Categorías
/api/terapias/destacadas/                # Solo destacadas
/api/terapias/busqueda_avanzada/         # Búsqueda avanzada
/api/terapias/{id}/calcular_costo_mensual/  # Calcular costo
/api/terapias/estadisticas/              # Estadísticas
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: "No module named 'decouple'"
```powershell
pip install python-decouple
```

### Error: "No module named 'MySQLdb'"
```powershell
pip install mysqlclient
```

### Error: "Access denied for user"
- Verificar credenciales en `.env`
- Verificar que MySQL esté corriendo
- Crear usuario y BD en MySQL

### Error: "AttributeError at /admin/"
- Verificar que `config/urls.py` tenga:
  ```python
  path('admin/', admin.site.urls),  # NO admin_view
  ```

### Error: "combine() argument 1 must be datetime.date, not None"
- Ya está corregido en este ZIP
- El archivo `models.py` de consultorios tiene las validaciones

---

## 📊 ESTRUCTURA DEL PROYECTO

```
tea_management/
├── apps/
│   ├── usuarios/          # Sprint 1 ✅
│   ├── consultorios/      # Sprint 2 ✅
│   └── terapias/          # Sprint 3 ✅ NUEVO
│       ├── models.py      # 2 modelos
│       ├── admin.py       # Admin personalizado
│       ├── forms.py       # 3 formularios
│       ├── views.py       # 11 vistas
│       ├── urls.py        # URLs
│       ├── tests.py       # 18+ tests
│       └── api/
│           ├── serializers.py  # 6 serializadores
│           ├── views.py        # 2 ViewSets
│           └── urls.py         # Router
├── config/
│   ├── settings.py
│   └── urls.py
├── manage.py
└── requirements.txt
```

---

## 📚 DOCUMENTACIÓN ADICIONAL

### Documentos incluidos:
- ✅ `SPRINT_1_REVIEW.md` - Review Sprint 1
- ✅ `SPRINT_2_REVIEW.md` - Review Sprint 2
- ✅ `SPRINT_3_REVIEW.md` - Review Sprint 3 ← NUEVO
- ✅ `VERIFICACION_CONSULTORIOS.md` - Verificación Sprint 2
- ✅ `CORRECCION_DISPONIBILIDAD.md` - Correcciones aplicadas

### Ver documentación API:
http://127.0.0.1:8000/api/docs/

---

## 🎯 PRÓXIMOS PASOS

### Sprint 4: Procedimientos y Sesiones (Próximo)
- Modelo de Procedimiento (sesiones)
- Registro de sesiones
- Notas de evolución
- Relación con pacientes
- Reportes de progreso

---

## 💡 TIPS PARA WINDOWS 10

### PowerShell Tips:
```powershell
# Ver puertos en uso
netstat -ano | findstr :8000

# Matar proceso si puerto ocupado
taskkill /F /PID <PID>

# Limpiar caché de Python
py -m pip cache purge
```

### MySQL Tips:
```powershell
# Verificar que MySQL esté corriendo
Get-Service MySQL80

# Iniciar MySQL si está detenido
Start-Service MySQL80
```

---

## ✅ CHECKLIST DE INSTALACIÓN

- [ ] Python 3.10+ instalado
- [ ] MySQL corriendo
- [ ] Entorno virtual creado
- [ ] Dependencias instaladas
- [ ] Base de datos creada
- [ ] Archivo .env configurado
- [ ] Apps agregadas a INSTALLED_APPS
- [ ] Migraciones aplicadas
- [ ] Superusuario creado
- [ ] Tests pasando
- [ ] Servidor corriendo
- [ ] Admin accesible
- [ ] API funcionando

---

## 📞 SOPORTE

Si tienes problemas:
1. Revisa la sección "Solución de Problemas"
2. Verifica que todos los pasos se hayan completado
3. Revisa los logs de errores en PowerShell
4. Verifica los documentos de Sprint Review

---

**¡Felicitaciones! Has completado 3 de 4 sprints del proyecto (75% completado)** 🎉

**Sistema Operativo**: Windows 10  
**Ubicación**: Colombia  
**Fecha**: Noviembre 2025  
**Versión**: 1.0
