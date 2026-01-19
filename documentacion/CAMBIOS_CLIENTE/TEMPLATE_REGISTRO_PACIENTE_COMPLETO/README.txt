# 📋 TEMPLATE REGISTRO PACIENTE - COMPLETO Y CORREGIDO

## 🎯 OBJETIVO

Template actualizado con **TODOS** los campos del formulario `PacienteForm`:
- ✅ Búsqueda CIE-10 en tiempo real
- ✅ Fechas de ingreso y alta
- ✅ Motivo de inactividad
- ✅ Todos los campos médicos
- ✅ Validación completa
- ✅ Firma digital (opcional)

---

## 📁 ARCHIVOS ENTREGADOS

| Archivo | Descripción |
|---------|-------------|
| **registrar_paciente_completo.html** | Template completo corregido |
| **CAMBIOS_TEMPLATE.txt** | Resumen de cambios realizados |
| **vista_api_cie10.py** | Código API búsqueda CIE-10 |
| **urls_cie10.txt** | URLs para agregar |
| **README.txt** | Esta guía completa |

---

## 🚀 IMPLEMENTACIÓN RÁPIDA (5 pasos - 10 min)

### PASO 1: Copiar Template (1 min)

```bash
# Copiar template corregido
cp registrar_paciente_completo.html apps/procedimientos/templates/procedimientos/registrar_paciente.html
```

---

### PASO 2: Agregar Vista API (2 min)

**Archivo:** `apps/procedimientos/views.py`

```python
# Agregar imports
from django.http import JsonResponse
from django.db.models import Q

# Agregar función al final
def api_buscar_cie10(request):
    """API para búsqueda de códigos CIE-10"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'resultados': []})
    
    codigos = CodigoCIE10.objects.filter(
        Q(codigo__icontains=query) | 
        Q(descripcion__icontains=query),
        activo=True
    ).order_by('codigo')[:20]
    
    resultados = [{
        'id': c.id,
        'codigo': c.codigo,
        'descripcion': c.descripcion
    } for c in codigos]
    
    return JsonResponse({'resultados': resultados})
```

Ver **vista_api_cie10.py** para código completo.

---

### PASO 3: Agregar URL (1 min)

**Archivo:** `apps/procedimientos/urls.py`

```python
urlpatterns = [
    # ... URLs existentes ...
    
    # ✅ AGREGAR:
    path('api/buscar-cie10/', views.api_buscar_cie10, name='api_buscar_cie10'),
]
```

Ver **urls_cie10.txt** para más detalles.

---

### PASO 4: Verificar Códigos CIE-10 (1 min)

```bash
# Verificar que existan códigos
python manage.py shell
>>> from apps.procedimientos.models import CodigoCIE10
>>> CodigoCIE10.objects.filter(activo=True).count()

# Si retorna 0, cargar códigos
>>> exit()
python manage.py cargar_codigos_cie10
```

---

### PASO 5: Probar (5 min)

```bash
# Reiniciar servidor
python manage.py runserver

# Abrir navegador
http://127.0.0.1:8000/procedimientos/pacientes/crear/
```

**Verificar:**
1. ✓ Todos los campos visibles
2. ✓ Búsqueda CIE-10 funciona
3. ✓ Selección de código guarda ID
4. ✓ Campos fecha ingreso/alta presentes
5. ✓ Formulario se envía correctamente

---

## 📊 CAMPOS AGREGADOS AL TEMPLATE

### Antes (template original):
- Información personal básica
- Información de contacto
- Responsable/acudiente
- Diagnóstico principal (texto)
- Alergias, medicamentos, EPS
- Observaciones

### ✅ Ahora (template corregido):
- **TODO lo anterior +**
- **Buscador CIE-10** con autocompletado
- **Campo oculto** codigo_enfermedad
- **Fecha de ingreso**
- **Fecha de alta**
- **Motivo de inactividad**
- **JavaScript** búsqueda CIE-10
- **Select2** para mejor UX

---

## 🎨 CARACTERÍSTICAS DEL TEMPLATE

### 1. Búsqueda CIE-10 Inteligente
```
- Búsqueda en tiempo real (>2 caracteres)
- Por código (ej: F84.0)
- Por nombre (ej: Autismo)
- Máximo 20 resultados
- Selección con un clic
```

### 2. Validación
```
- Campos obligatorios marcados con *
- Validación cliente y servidor
- Mensajes de error claros
- Prevención envío incompleto
```

### 3. UX Mejorada
```
- Select2 para CIE-10
- Cards organizadas por sección
- Colores por tipo de información
- Tooltips y ayudas
- Responsive design
```

### 4. Firma Digital (Opcional)
```
- Canvas para firma
- Signature Pad library
- Guardado en base64
- Botón limpiar
```

---

## 🔧 ESTRUCTURA TÉCNICA

### Template Structure:
```
{% extends 'base/base.html' %}

{% block extra_css %}
├── Select2 CSS
├── Estilos búsqueda CIE-10
└── Estilos generales

{% block content %}
├── Header + navegación
├── Mensajes Django
├── Formulario Principal
│   ├── Información Personal
│   ├── Información Contacto
│   ├── Acudiente/Responsable
│   ├── Información Médica (+ CIE-10)
│   ├── Fechas Atención
│   └── Observaciones
└── Sidebar
    ├── Firma Digital
    └── Botones Acción

{% block extra_js %}
├── Select2 JS
├── Signature Pad JS
├── Búsqueda CIE-10 JS
└── Validación formulario
```

---

## 📝 CONFIGURACIÓN ADICIONAL

### Si usas firma digital:

En la vista, pasar contexto:
```python
return render(request, 'procedimientos/registrar_paciente.html', {
    'form': form,
    'titulo': 'Registrar Nuevo Paciente',
    'mostrar_firma': True  # ✅ Agregar
})
```

### Si NO usas firma digital:

```python
'mostrar_firma': False  # O quitar la variable
```

---

## ✅ CHECKLIST COMPLETO

### Backend:
```
☐ Vista api_buscar_cie10 agregada
☐ URL registrada para API
☐ Códigos CIE-10 cargados en BD
☐ CodigoCIE10.activo = True
☐ Vista registrar_paciente actualizada
```

### Frontend:
```
☐ Template reemplazado
☐ jQuery cargado (requerido por Select2)
☐ Bootstrap 5 disponible
☐ Bootstrap Icons cargados
```

### Testing:
```
☐ Búsqueda CIE-10 funciona
☐ Selección guarda ID correctamente
☐ Campos fecha presentes
☐ Validación funciona
☐ Formulario se envía sin errores
```

---

## 🆘 TROUBLESHOOTING

### Problema: Búsqueda CIE-10 no funciona

**Síntomas:**
- No aparecen resultados
- Console muestra error 404

**Solución:**
1. Verificar URL API en JavaScript (línea 527 template)
2. Verificar URL registrada en urls.py
3. Verificar que existan códigos CIE-10 en BD
4. Console navegador (F12) → Network → Ver petición

---

### Problema: No se guarda código CIE-10

**Síntomas:**
- Selección funciona pero no guarda

**Solución:**
1. Verificar campo oculto: `<input type="hidden" id="id_codigo_enfermedad">`
2. Verificar JavaScript actualiza hiddenInput.value
3. Verificar formulario incluye codigo_enfermedad en fields

---

### Problema: Select2 no funciona

**Síntomas:**
- Campo búsqueda no tiene estilo especial

**Solución:**
1. Verificar jQuery cargado ANTES de Select2
2. Verificar CDN de Select2 disponible
3. Console navegador → Ver errores JS

---

## 📊 COMPARACIÓN ANTES/DESPUÉS

| Aspecto | Antes | Después |
|---------|-------|---------|
| Campos visibles | 15 | 19 ✅ |
| Búsqueda CIE-10 | ❌ | ✅ |
| Fecha ingreso | ❌ | ✅ |
| Fecha alta | ❌ | ✅ |
| Motivo inactividad | ❌ | ✅ |
| Select2 | ❌ | ✅ |
| Validación JS | Básica | Completa ✅ |
| UX | Buena | Excelente ✅ |

---

## 🎯 RESULTADO FINAL

Después de implementar:

1. ✅ **Template completo** con todos los campos del formulario
2. ✅ **Búsqueda CIE-10** funcional en tiempo real
3. ✅ **API REST** para búsqueda
4. ✅ **Validación** cliente y servidor
5. ✅ **UX profesional** con Select2
6. ✅ **Responsive** en todos los dispositivos

---

## ⏱️ TIEMPO TOTAL

- Copiar template: 1 min
- Agregar vista API: 2 min
- Agregar URL: 1 min
- Verificar códigos: 1 min
- Probar: 5 min
- **TOTAL: 10 minutos** ⏱️

---

## 📞 SOPORTE

Si encuentras problemas:
1. Revisar **CAMBIOS_TEMPLATE.txt** para detalles
2. Revisar **vista_api_cie10.py** para API completa
3. Verificar checklist completo
4. Revisar console navegador (F12)

---

**¡Template listo para producción!** 🚀  
**Todos los campos del formulario implementados** ✅  
**Búsqueda CIE-10 profesional** ✅
