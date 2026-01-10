# 🔄 COMPARACIÓN: Estructura Estándar vs Config

## 📊 Cambios Necesarios (Diff Visual)

---

## 1️⃣ `manage.py`

### ❌ ANTES (tea_management)
```python
def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tea_management.settings')
    # ↑ nombre del proyecto
```

### ✅ DESPUÉS (config)
```python
def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    # ↑ cambiado a 'config'
```

**🔧 Cambio:** `'tea_management.settings'` → `'config.settings'`

---

## 2️⃣ `config/settings.py`

### ❌ ANTES (tea_management)
```python
# Línea ~55
ROOT_URLCONF = 'tea_management.urls'

# Línea ~72
WSGI_APPLICATION = 'tea_management.wsgi.application'
```

### ✅ DESPUÉS (config)
```python
# Línea ~55
ROOT_URLCONF = 'config.urls'

# Línea ~72
WSGI_APPLICATION = 'config.wsgi.application'
```

**🔧 Cambios:**
- `'tea_management.urls'` → `'config.urls'`
- `'tea_management.wsgi.application'` → `'config.wsgi.application'`

---

## 3️⃣ `config/wsgi.py`

### ❌ ANTES (tea_management)
```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tea_management.settings')

application = get_wsgi_application()
```

### ✅ DESPUÉS (config)
```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
```

**🔧 Cambio:** `'tea_management.settings'` → `'config.settings'`

---

## 4️⃣ `config/asgi.py`

### ❌ ANTES (tea_management)
```python
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tea_management.settings')

application = get_asgi_application()
```

### ✅ DESPUÉS (config)
```python
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
```

**🔧 Cambio:** `'tea_management.settings'` → `'config.settings'`

---

## 📂 Estructura de Carpetas

### ❌ ANTES (Estándar de Django)
```
tea_management/
├── manage.py
└── tea_management/          ← Mismo nombre (confuso)
    ├── __init__.py
    ├── settings.py
    ├── urls.py
    ├── asgi.py
    └── wsgi.py
```

### ✅ DESPUÉS (Con config/)
```
tea_management/
├── manage.py
└── config/                  ← Nombre descriptivo
    ├── __init__.py
    ├── settings.py
    ├── urls.py
    ├── asgi.py
    └── wsgi.py
```

**🔧 Cambio:** Renombrar carpeta `tea_management/` → `config/`

---

## 📝 Resumen de Todos los Cambios

### Buscar y Reemplazar
Puedes usar estos patrones en tu editor:

| Buscar | Reemplazar | Archivos |
|--------|-----------|----------|
| `'tea_management.settings'` | `'config.settings'` | manage.py, wsgi.py, asgi.py |
| `'tea_management.urls'` | `'config.urls'` | settings.py |
| `'tea_management.wsgi.application'` | `'config.wsgi.application'` | settings.py |

### Usando VS Code (Find & Replace)
1. Presiona `Ctrl+Shift+H` (Windows/Linux) o `Cmd+Shift+H` (Mac)
2. En "Find": `tea_management\.`
3. En "Replace": `config.`
4. Click "Replace All"

### Usando Vim
```vim
:%s/tea_management\./config./g
```

### Usando Sublime Text
1. `Ctrl+H` (Find & Replace)
2. Enable "Regular Expression" mode
3. Find: `tea_management\.`
4. Replace: `config.`

---

## 🔍 Verificación Rápida

Después de hacer los cambios, verifica con:

```bash
# Buscar cualquier referencia restante
grep -r "tea_management" --include="*.py" .

# Debería mostrar solo comentarios o strings, no código
```

Si ves referencias en:
- `manage.py` → Actualízalo
- `config/settings.py` → Actualízalo
- `config/wsgi.py` → Actualízalo
- `config/asgi.py` → Actualízalo

---

## 🧪 Probar que Funcionó

```bash
# Este comando NO debe dar errores
python manage.py check

# Salida esperada:
# System check identified no issues (0 silenced).
```

✅ **Si ves "no issues", ¡todo está perfecto!**

---

## ⚡ Método Rápido (Una Línea)

### Linux/Mac:
```bash
django-admin startproject tea_management . && mv tea_management config && find . -name "*.py" -type f -exec sed -i '' 's/tea_management\./config./g' {} +
```

### Windows (PowerShell):
```powershell
django-admin startproject tea_management .; Rename-Item tea_management config; Get-ChildItem -Recurse -Filter *.py | ForEach-Object { (Get-Content $_.FullName) -replace 'tea_management\.', 'config.' | Set-Content $_.FullName }
```

---

## 📋 Checklist de Cambios

- [ ] Carpeta `tea_management/` renombrada a `config/`
- [ ] `manage.py` actualizado (línea con `setdefault`)
- [ ] `config/settings.py` actualizado (2 líneas: `ROOT_URLCONF` y `WSGI_APPLICATION`)
- [ ] `config/wsgi.py` actualizado (línea con `setdefault`)
- [ ] `config/asgi.py` actualizado (línea con `setdefault`)
- [ ] Ejecutado `python manage.py check` sin errores
- [ ] Servidor inicia correctamente con `python manage.py runserver`

---

## 🎯 Por qué estos cambios

Django busca el módulo de configuración usando estas variables:
- `DJANGO_SETTINGS_MODULE` → Apunta a `config.settings`
- `ROOT_URLCONF` → Apunta a `config.urls`
- `WSGI_APPLICATION` → Apunta a `config.wsgi.application`

Si renombramos la carpeta pero no actualizamos las referencias, Django busca en el lugar equivocado y falla.

---

## 🐛 Errores Comunes

### Error: `ModuleNotFoundError: No module named 'tea_management'`
**Causa:** Olvidaste actualizar alguna referencia

**Solución:**
```bash
# Busca todas las referencias
grep -r "tea_management" . --include="*.py"

# Actualízalas todas a "config"
```

### Error: `django.core.exceptions.ImproperlyConfigured`
**Causa:** `settings.py` tiene referencias incorrectas

**Solución:** Verifica que `ROOT_URLCONF` y `WSGI_APPLICATION` apunten a `config.*`

---

## 💡 Tips Adicionales

1. **Hazlo inmediatamente** - Cambia a `config/` antes de empezar a desarrollar
2. **Usa el script** - Es más rápido y sin errores
3. **Verifica siempre** - Ejecuta `python manage.py check` después
4. **Documenta** - Si trabajas en equipo, avisa del cambio

---

## 📚 Recursos

- [Django Docs - Settings](https://docs.djangoproject.com/en/5.0/topics/settings/)
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)
- [Cookiecutter Django](https://github.com/cookiecutter/cookiecutter-django)

---

¡Listo! Con estos cambios tendrás la estructura profesional con `config/` 🎉
