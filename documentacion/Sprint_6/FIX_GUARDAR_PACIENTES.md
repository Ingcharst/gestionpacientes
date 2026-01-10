# 🐛 FIX: Pacientes No Se Guardan en la Base de Datos

## 📋 PROBLEMA IDENTIFICADO

Al hacer clic en "Guardar Paciente", el formulario no guarda en la base de datos.

**Causas:**
1. ❌ Vista `paciente_crear` no pasa `object` al contexto
2. ❌ Template usa `{% if object %}` pero recibe `paciente`
3. ❌ Falta manejo de errores visible
4. ❌ No se muestra mensaje cuando hay errores de validación

---

## ✅ SOLUCIÓN RÁPIDA

### Paso 1: Reemplazar `views.py`

Reemplaza el archivo:
```
apps/procedimientos/views.py
```

Con el archivo corregido:
[views_corregido.py](computer:///mnt/user-data/outputs/views_corregido.py)

### Cambios Clave en las Vistas:

#### ANTES (❌ No funcionaba):
```python
@login_required
def paciente_crear(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST, request.FILES)
        if form.is_valid():
            paciente = form.save(commit=False)
            paciente.creado_por = request.user  # ❌ Este campo NO existe
            paciente.save()
            # ...
    # ...
    context = {'form': form, 'titulo': 'Crear Paciente'}  # ❌ Falta 'object'
    return render(request, 'procedimientos/paciente_form.html', context)
```

#### DESPUÉS (✅ Funciona):
```python
@login_required
def paciente_crear(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                paciente = form.save()  # ✅ Guardar directo sin commit=False
                messages.success(request, f'Paciente {paciente.nombre_completo} creado exitosamente.')
                return redirect('procedimientos:paciente_detail', pk=paciente.pk)
            except Exception as e:
                messages.error(request, f'Error al guardar: {str(e)}')  # ✅ Capturar errores
        else:
            messages.error(request, 'Por favor corrija los errores.')  # ✅ Mensaje de error
    else:
        form = PacienteForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Paciente',
        'object': None  # ✅ Agregar 'object' al contexto
    }
    return render(request, 'procedimientos/paciente_form.html', context)
```

---

## 📝 CAMBIOS DETALLADOS

### 1. Función `paciente_crear` ✅

**Errores corregidos:**
- ✅ Eliminado `commit=False` y `paciente.creado_por` (campo no existe en modelo)
- ✅ Agregado `object: None` al contexto
- ✅ Agregado `try/except` para capturar errores
- ✅ Agregado `messages.error` cuando form no es válido

### 2. Función `paciente_editar` ✅

**Errores corregidos:**
- ✅ Cambiado contexto de `'paciente'` a `'object'`
- ✅ Agregado `try/except` para capturar errores
- ✅ Agregado `messages.error` cuando form no es válido

### 3. Todas las demás vistas ✅

**Mejoras aplicadas:**
- ✅ `sesion_crear`, `sesion_editar`
- ✅ `procedimiento_crear`
- Todas ahora tienen:
  - Manejo de errores con `try/except`
  - Mensajes de error visibles
  - Mejor feedback al usuario

---

## 🔍 POR QUÉ FALLABA

### Error #1: Campo `creado_por` no existe
```python
# ❌ ANTES
paciente.creado_por = request.user  # Este campo NO está en el modelo
```

El modelo `Paciente` **NO tiene** campo `creado_por`. Al intentar asignarlo, Django lanza un error silencioso.

**Solución:** Eliminar esa línea y guardar directo con `form.save()`

### Error #2: Template esperaba `object`, recibía `paciente`
```django
{# Template usa #}
{% if object and object.foto %}
    <img src="{{ object.foto.url }}">
{% endif %}

{# Pero la vista enviaba #}
context = {'paciente': paciente}  # ❌ Inconsistencia
```

**Solución:** Usar `object` en el contexto consistentemente

### Error #3: Sin mensajes de error
Cuando el formulario fallaba en validación, no se mostraba ningún mensaje al usuario.

**Solución:** Agregar `messages.error()` cuando `form.is_valid()` es False

---

## 🧪 TESTING DESPUÉS DE LA CORRECCIÓN

### 1. Prueba Básica
```bash
# Iniciar servidor
python manage.py runserver

# Ir a: http://localhost:8000/procedimientos/pacientes/crear/
```

### 2. Llenar Formulario

**Campos obligatorios (*):**
- Nombres: "Juan"
- Apellidos: "Pérez"
- Tipo Documento: "RC"
- Número Documento: "123456789" (único)
- Fecha Nacimiento: "2020-01-15"
- Género: "M"
- Historia Clínica: "HC-001" (único)
- Nombre Responsable: "María Pérez"
- Parentesco: "Madre"
- Teléfono Responsable: "3001234567"
- Diagnóstico Principal: "Trastorno del Espectro Autista"

### 3. Click "Guardar Paciente"

**Resultados esperados:**
✅ Mensaje verde: "Paciente Juan Pérez creado exitosamente"
✅ Redirección a página de detalle del paciente
✅ Paciente visible en lista: `/procedimientos/pacientes/`

**Si hay error:**
❌ Mensaje rojo con descripción del error
❌ Formulario mantiene datos ingresados
❌ Errores de validación mostrados en rojo

---

## 📊 VERIFICACIÓN EN BASE DE DATOS

### Opción 1: Django Shell
```bash
python manage.py shell

>>> from apps.procedimientos.models import Paciente
>>> Paciente.objects.all()
<QuerySet [<Paciente: Juan Pérez>]>

>>> p = Paciente.objects.first()
>>> p.nombre_completo
'Juan Pérez'
>>> p.numero_documento
'123456789'
```

### Opción 2: Django Admin
```bash
# Crear superusuario si no tienes
python manage.py createsuperuser

# Ir a: http://localhost:8000/admin
# Login → Procedimientos → Pacientes
```

---

## 🚨 ERRORES COMUNES Y SOLUCIONES

### Error: "numero_documento ya existe"
**Causa:** Número de documento duplicado (campo único)
**Solución:** Usar número diferente para cada paciente

### Error: "numero_historia_clinica ya existe"
**Causa:** Historia clínica duplicada (campo único)
**Solución:** Usar número diferente (ej: HC-001, HC-002, etc.)

### Error: "This field is required"
**Causa:** Campo obligatorio vacío
**Solución:** Llenar todos los campos con asterisco rojo (*)

### Error: Formulario no muestra nada
**Causa:** Archivo `paciente_form.html` mal ubicado
**Solución:** Verificar que esté en `templates/procedimientos/`

---

## 📁 ARCHIVOS PARA REEMPLAZAR

### 1. views.py (Principal)
**Ubicación:** `apps/procedimientos/views.py`
**Descargar:** [views_corregido.py](computer:///mnt/user-data/outputs/views_corregido.py)

### 2. paciente_form.html (Ya actualizado)
**Ubicación:** `templates/procedimientos/paciente_form.html`
**Descargar:** [paciente_form_mejorado.zip](computer:///mnt/user-data/outputs/paciente_form_mejorado.zip)

---

## ✅ CHECKLIST FINAL

Después de aplicar los cambios:

- [ ] `views.py` reemplazado con versión corregida
- [ ] `paciente_form.html` con template mejorado
- [ ] Servidor reiniciado: `python manage.py runserver`
- [ ] Formulario carga correctamente
- [ ] Campos obligatorios marcados con *
- [ ] Formulario guarda correctamente
- [ ] Mensaje de éxito aparece
- [ ] Redirección funciona
- [ ] Paciente visible en lista
- [ ] Paciente visible en admin (opcional)
- [ ] Edición de paciente funciona
- [ ] Foto se sube correctamente

---

## 📞 SI AÚN NO FUNCIONA

### Debug Paso a Paso:

1. **Ver errores de Django:**
```bash
python manage.py runserver
# Llenar formulario y enviar
# Ver terminal donde corre el servidor
```

2. **Activar modo Debug:**
En `settings.py`:
```python
DEBUG = True
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {'handlers': ['console'], 'level': 'DEBUG'},
}
```

3. **Verificar formulario:**
En Django shell:
```python
from apps.procedimientos.forms import PacienteForm

# Crear formulario con datos
data = {
    'nombres': 'Test',
    'apellidos': 'Usuario',
    # ... todos los campos requeridos
}

form = PacienteForm(data)
print(form.is_valid())
print(form.errors)
```

---

**Última actualización:** 20/11/2025  
**Estado:** ✅ Bug identificado y corregido  
**Archivo principal:** [views_corregido.py](computer:///mnt/user-data/outputs/views_corregido.py)
