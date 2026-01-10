# 🏗️ Guía: Crear Proyecto Django con estructura `config/`

## 📋 ¿Por qué usar `config/` en lugar del nombre del proyecto?

### ❌ Estructura Estándar (Confusa)
```
tea_management/
├── manage.py
└── tea_management/    ← Mismo nombre que el directorio padre
    ├── settings.py
    └── urls.py
```

### ✅ Estructura Recomendada (Clara)
```
tea_management/
├── manage.py
└── config/            ← Nombre descriptivo
    ├── settings.py
    └── urls.py
```

**Ventajas:**
- 🎯 Más claro: "config" describe su propósito
- 🧹 Evita confusión de nombres duplicados
- 📚 Mejor práctica en la comunidad Django
- 🔧 Más fácil de mantener

---

## 🚀 MÉTODO 1: Script Automático (MÁS RÁPIDO)

### Descarga el script
[**Descargar setup_django_project.sh**](computer:///mnt/user-data/outputs/setup_django_project.sh)

### Ejecuta
```bash
chmod +x setup_django_project.sh
./setup_django_project.sh
```

¡Listo! El script hace todo automáticamente.

---

## 🔧 MÉTODO 2: Paso a Paso Manual (COMPLETO)

### Paso 1: Crear proyecto estándar de Django

```bash
# Opción A: Crear en directorio actual
django-admin startproject tea_management .

# Opción B: Crear en nuevo directorio
django-admin startproject tea_management
cd tea_management
```

**Resultado:**
```
tea_management/
├── manage.py
└── tea_management/
    ├── __init__.py
    ├── settings.py
    ├── urls.py
    ├── asgi.py
    └── wsgi.py
```

---

### Paso 2: Renombrar carpeta

```bash
# Linux/Mac
mv tea_management config

# Windows (PowerShell)
Rename-Item -Path "tea_management" -NewName "config"

# Windows (CMD)
rename tea_management config
```

**Resultado:**
```
tea_management/
├── manage.py
└── config/          ← Renombrado
    ├── __init__.py
    ├── settings.py
    └── ...
```

---

### Paso 3: Actualizar `manage.py`

**Archivo:** `manage.py`

**Busca esta línea:**
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tea_management.settings')
```

**Cámbiala por:**
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
```

**Archivo completo:**
```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # ← Cambio aquí
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
```

---

### Paso 4: Actualizar `config/settings.py`

**Archivo:** `config/settings.py`

**Cambio 1 - ROOT_URLCONF (línea ~55):**

Busca:
```python
ROOT_URLCONF = 'tea_management.urls'
```

Cambia por:
```python
ROOT_URLCONF = 'config.urls'
```

**Cambio 2 - WSGI_APPLICATION (línea ~72):**

Busca:
```python
WSGI_APPLICATION = 'tea_management.wsgi.application'
```

Cambia por:
```python
WSGI_APPLICATION = 'config.wsgi.application'
```

---

### Paso 5: Actualizar `config/wsgi.py`

**Archivo:** `config/wsgi.py`

**Busca:**
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tea_management.settings')
```

**Cambia por:**
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
```

**Archivo completo:**
```python
"""
WSGI config for project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # ← Cambio aquí

application = get_wsgi_application()
```

---

### Paso 6: Actualizar `config/asgi.py`

**Archivo:** `config/asgi.py`

**Busca:**
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tea_management.settings')
```

**Cambia por:**
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
```

**Archivo completo:**
```python
"""
ASGI config for project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # ← Cambio aquí

application = get_asgi_application()
```

---

### Paso 7: Verificar que funciona

```bash
python manage.py check
```

**Salida esperada:**
```
System check identified no issues (0 silenced).
```

✅ **Si ves esto, ¡todo está bien!**

---

### Paso 8: (Opcional) Crear estructura de apps

```bash
# Crear directorio de apps
mkdir -p apps/usuarios
mkdir -p apps/consultorios
mkdir -p apps/terapias
mkdir -p apps/procedimientos

# Crear __init__.py en cada uno
touch apps/__init__.py
touch apps/usuarios/__init__.py
touch apps/consultorios/__init__.py
touch apps/terapias/__init__.py
touch apps/procedimientos/__init__.py

# Crear otros directorios
mkdir -p templates
mkdir -p static/css static/js static/img
mkdir -p media
mkdir -p logs
```

---

## ✅ Estructura Final

```
tea_management/
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings.py      ✏️ Modificado
│   ├── urls.py
│   ├── asgi.py          ✏️ Modificado
│   └── wsgi.py          ✏️ Modificado
├── apps/
│   ├── __init__.py
│   ├── usuarios/
│   ├── consultorios/
│   ├── terapias/
│   └── procedimientos/
├── templates/
├── static/
│   ├── css/
│   ├── js/
│   └── img/
├── media/
└── logs/
```

---

## 🧪 Probar el proyecto

```bash
# 1. Verificar configuración
python manage.py check

# 2. Iniciar servidor
python manage.py runserver

# 3. Abrir en navegador
# http://127.0.0.1:8000/
```

Deberías ver la página de bienvenida de Django 🚀

---

## 📝 Resumen de Cambios

### Archivos modificados:
1. ✅ `manage.py` - Cambiar a `config.settings`
2. ✅ `config/settings.py` - Cambiar `ROOT_URLCONF` y `WSGI_APPLICATION`
3. ✅ `config/wsgi.py` - Cambiar a `config.settings`
4. ✅ `config/asgi.py` - Cambiar a `config.settings`

### Carpeta renombrada:
- `tea_management/` → `config/`

---

## 🆘 Solución de Problemas

### Error: "No module named 'tea_management'"
👉 Olvidaste cambiar alguna referencia de `tea_management` a `config`

Revisa estos archivos:
- manage.py
- config/settings.py
- config/wsgi.py
- config/asgi.py

### Error: "Cannot import name 'settings'"
👉 El archivo settings.py no está en la ubicación correcta

Verifica:
```bash
ls config/settings.py  # Debe existir
```

### El servidor no inicia
👉 Ejecuta con más detalles:
```bash
python manage.py runserver --traceback
```

---

## 🎯 Próximos Pasos

Una vez que tengas la estructura con `config/`:

1. **Configurar base de datos** en `config/settings.py`
2. **Crear apps** con `python manage.py startapp nombre`
3. **Copiar modelos** del proyecto descargado
4. **Ejecutar migraciones**

---

## 📚 Referencias

- [Django Two Scoops Book](https://www.feldroy.com/books/two-scoops-of-django-3-x) - Recomienda esta estructura
- [Cookiecutter Django](https://github.com/cookiecutter/cookiecutter-django) - Usa esta estructura
- [Django Best Practices](https://django-best-practices.readthedocs.io/)

---

## 💡 Bonus: Comando Sed para cambios rápidos

Si estás en Linux/Mac, usa estos comandos:

```bash
# Actualizar manage.py
sed -i '' "s/'tea_management.settings'/'config.settings'/g" manage.py

# Actualizar settings.py
sed -i '' "s/tea_management.urls/config.urls/g" config/settings.py
sed -i '' "s/tea_management.wsgi/config.wsgi/g" config/settings.py

# Actualizar wsgi.py
sed -i '' "s/'tea_management.settings'/'config.settings'/g" config/wsgi.py

# Actualizar asgi.py
sed -i '' "s/'tea_management.settings'/'config.settings'/g" config/asgi.py
```

---

¡Listo! Ahora tienes un proyecto Django con la estructura `config/` 🎉
