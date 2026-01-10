# 🚀 TEA Management System - Sprint 5: Frontend MVP

## ✅ **SPRINT 5 COMPLETADO**

### **¿Qué se implementó?**
✅ Login responsive con Bootstrap 5  
✅ Dashboard con estadísticas en tiempo real  
✅ CRUD completo de pacientes con HTMX  
✅ Sidebar de navegación moderna  
✅ Sistema de mensajes flash  
✅ Templates base reutilizables  

---

## 📦 **Instalación Rápida**

### **1. Extraer Proyecto**
```bash
# Extraer el archivo
tar -xzf tea_management_sprint5.tar.gz
cd tea_management
```

### **2. Crear Entorno Virtual**
```bash
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Linux/Mac)
source venv/bin/activate
```

### **3. Instalar Dependencias**
```bash
pip install django==5.2.7
pip install mysqlclient
pip install python-decouple
pip install django-jazzmin
pip install djangorestframework djangorestframework-simplejwt
pip install django-cors-headers django-filter
pip install django-crispy-forms crispy-bootstrap5
pip install django-extensions django-htmx
pip install drf-spectacular whitenoise Pillow
```

### **4. Configurar .env**
Crear archivo `.env` en la raíz:
```env
DEBUG=True
SECRET_KEY=django-insecure-cambiar-en-produccion
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=tea_management
DB_USER=root
DB_PASSWORD=tu_password_mysql
DB_HOST=localhost
DB_PORT=3306
```

### **5. Base de Datos**
```sql
CREATE DATABASE tea_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

```bash
python manage.py migrate
python manage.py createsuperuser
```

### **6. Ejecutar**
```bash
python manage.py runserver
```

**Accede a**: http://localhost:8000/

---

## 🎯 **Credenciales de Prueba**

Usa el superusuario que creaste, o crea usuarios desde:
- Admin: http://localhost:8000/admin/

---

## 📁 **Estructura del Frontend**

```
templates/
├── base/base.html          ← Template principal
├── auth/
│   ├── login.html          ← Página de login
│   └── dashboard.html      ← Dashboard principal
├── pacientes/
│   ├── lista.html          ← Lista con filtros
│   ├── formulario.html     ← Crear/Editar
│   ├── detalle.html        ← Vista detallada
│   └── table.html          ← Tabla HTMX
```

---

## 🔥 **Características Principales**

### **Login**
- Diseño moderno split-screen
- Validación en tiempo real
- Registro de accesos

### **Dashboard**
- 4 KPI cards
- Lista de próximas sesiones
- Accesos rápidos
- Notificaciones

### **Pacientes**
- ✅ Lista con búsqueda HTMX
- ✅ Filtros dinámicos
- ✅ Formulario completo
- ✅ Vista detallada con tabs
- ✅ Edición inline

### **Navegación**
- Sidebar fixed
- Responsive (mobile-first)
- Indicadores de página activa

---

## 🛠️ **Tecnologías**

| Tecnología | Versión | Uso |
|------------|---------|-----|
| Django | 5.2.7 | Backend framework |
| Bootstrap | 5.3.2 | UI/CSS |
| HTMX | 1.9.10 | Interactividad |
| MySQL | 8.0+ | Base de datos |
| JWT | - | Autenticación API |

---

## 📊 **URLs Principales**

- `/` → Dashboard
- `/login/` → Login
- `/logout/` → Logout
- `/procedimientos/pacientes/` → Lista pacientes
- `/admin/` → Panel admin
- `/api/docs/` → Documentación API

---

## 🎓 **Para Estudiantes**

Este proyecto implementa:
1. ✅ **MVT Pattern** (Django)
2. ✅ **REST API** (DRF)
3. ✅ **Autenticación JWT**
4. ✅ **HTMX** (Sin JavaScript pesado)
5. ✅ **Bootstrap 5** (Responsive)
6. ✅ **Metodología Agile**

---

## 🐛 **Troubleshooting**

**MySQL Error**:
```bash
pip install mysqlclient
# Windows: Descargar wheel de https://www.lfd.uci.edu/~gohlke/pythonlibs/
```

**Migrations Error**:
```bash
python manage.py migrate --fake-initial
```

**Static Files**:
```bash
python manage.py collectstatic
```

---

## 📞 **Soporte**

**Instructor**: Carlos  
**Programa**: SENA - Análisis y Desarrollo de Sistemas  
**Sprint**: 5 de 10  

---

## 🎉 **¡Listo para usar!**

Ejecuta `python manage.py runserver` y comienza a probar el sistema.

**Próximo Sprint**: Frontend avanzado (Terapias, Consultorios, Agenda)
