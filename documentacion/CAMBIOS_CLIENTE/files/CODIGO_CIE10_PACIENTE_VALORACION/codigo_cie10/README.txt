# 📦 Código CIE-10 en Paciente y Valoración

## 🎯 OBJETIVO

Agregar campo de código CIE-10 en:
1. ✅ Formulario registro de paciente (campo ya existe: `codigo_enfermedad`)
2. ✅ Modelo y formulario de valoración profesional (campo nuevo: `codigo_cie10`)

---

## 📁 ARCHIVOS INCLUIDOS

| Archivo | Descripción |
|---------|-------------|
| **APLICAR_RAPIDO.txt** | Guía paso a paso (5 min) |
| **CODIGO_COPIAR.txt** | Código listo para copiar |
| **GUIA_IMPLEMENTACION.txt** | Documentación completa |
| **forms_con_cie10.py** | Formularios completos |
| **paciente_form.html** | Template paciente completo |
| **crear_valoracion.html** | Template valoración completo |
| **modelo_valoracion_con_cie10.py** | Modelo actualizado |

---

## ⚡ INICIO RÁPIDO

### Opción 1: Copiar archivos completos (Recomendado)

```bash
# Copiar templates completos
cp paciente_form.html apps/procedimientos/templates/procedimientos/
cp crear_valoracion.html apps/procedimientos/templates/procedimientos/

# Ver forms_con_cie10.py y copiar a forms.py
# (Reemplazar las clases PacienteRegistroForm y ValoracionProfesionalForm)
```

### Opción 2: Seguir guía APLICAR_RAPIDO.txt

Modificar manualmente cada archivo según la guía.

---

## 🚀 PASOS BÁSICOS

```bash
# 1. Agregar campo en modelo ValoracionProfesional
# Ver: modelo_valoracion_con_cie10.py

# 2. Migración
python manage.py makemigrations procedimientos
python manage.py migrate procedimientos

# 3. Actualizar formularios
# Ver: forms_con_cie10.py

# 4. Actualizar templates
# Ver: paciente_form.html y crear_valoracion.html

# 5. Reiniciar
python manage.py runserver
```

---

## ✅ RESULTADO

**Registro Paciente:**
- Campo CIE-10 con buscador Select2
- Opcional
- Se guarda en `Paciente.codigo_enfermedad`

**Valoración Profesional:**
- Campo CIE-10 con buscador Select2
- Opcional
- Se guarda en `ValoracionProfesional.codigo_cie10`
- Cada terapeuta asigna su propio diagnóstico

---

## 📋 FEATURES

✅ Select2 para búsqueda avanzada
✅ Búsqueda por código o nombre
✅ Campos opcionales
✅ Diseño Bootstrap 5
✅ Validación de formularios
✅ Iconos Bootstrap Icons
✅ Responsive

---

## ⏱️ TIEMPO

- Con archivos completos: 3 minutos
- Manual siguiendo guía: 5 minutos

---

**¡Listo para implementar!** 🚀
