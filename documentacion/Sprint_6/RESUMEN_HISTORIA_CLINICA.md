# ✅ MODELO PACIENTE - AUTO-GENERACIÓN DE HISTORIA CLÍNICA

## 📦 DESCARGA COMPLETA

[historia_clinica_automatica.zip](computer:///mnt/user-data/outputs/historia_clinica_automatica.zip) **(9.1 KB)**

**Contiene:**
1. `paciente_model_corregido.py` - Modelo Paciente corregido
2. `IMPLEMENTACION_HISTORIA_CLINICA.md` - Guía completa paso a paso
3. `migrar_historias_clinicas.py` - Script para migrar datos existentes

---

## 🎯 CAMBIO PRINCIPAL

### ❌ ANTES:
- Usuario tenía que escribir historia clínica manualmente
- Campo obligatorio en formulario
- Riesgo de duplicados o errores

### ✅ AHORA:
- **Se genera automáticamente** al guardar paciente
- **Formato:** `HC-{NUMERO_DOCUMENTO}-{AÑO}`
- **Ejemplo:** `HC-123456789-2025`
- **Si existe duplicado:** `HC-123456789-2025-1`

---

## 🚀 INSTALACIÓN RÁPIDA (3 PASOS)

### 1️⃣ Reemplazar Modelo

Reemplaza la clase `Paciente` en `apps/procedimientos/models.py` con el contenido de:
```
paciente_model_corregido.py
```

**Cambios clave:**
- Campo `numero_historia_clinica` ahora es `blank=True`
- Nuevo método `generar_numero_historia_clinica()`
- Método `save()` sobrescrito para auto-generar

### 2️⃣ Crear y Aplicar Migración

```bash
# Crear migración
python manage.py makemigrations procedimientos

# Aplicar migración
python manage.py migrate procedimientos
```

### 3️⃣ Actualizar Formulario

En `apps/procedimientos/forms.py`, **eliminar** `'numero_historia_clinica'` de la lista `fields`:

```python
class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = [
            'nombres', 'apellidos', 'tipo_documento', 'numero_documento',
            'fecha_nacimiento', 'genero', 'foto',
            # ... otros campos
            # ❌ NO incluir 'numero_historia_clinica'
        ]
```

---

## ✅ VERIFICACIÓN

### Probar Creación de Paciente

```bash
python manage.py shell

>>> from apps.procedimientos.models import Paciente
>>> p = Paciente.objects.create(
...     nombres='Juan',
...     apellidos='Pérez',
...     numero_documento='123456789',
...     fecha_nacimiento='2020-01-01',
...     genero='M',
...     nombre_responsable='María Pérez',
...     parentesco_responsable='Madre',
...     telefono_responsable='3001234567',
...     diagnostico_principal='TEA Nivel 1'
... )
>>> print(p.numero_historia_clinica)
HC-123456789-2025  ← ✅ Generado automáticamente
```

---

## 📋 FORMATO DE HISTORIA CLÍNICA

### Ejemplos Generados

| Paciente | Documento | Año | Historia Clínica |
|----------|-----------|-----|------------------|
| Juan Pérez | 123456789 | 2025 | HC-123456789-2025 |
| Juan Pérez (hermano) | 123456789 | 2025 | HC-123456789-2025-1 |
| María López | 987654321 | 2025 | HC-987654321-2025 |
| Pedro Gómez | 111222333 | 2026 | HC-111222333-2026 |

### Características

✅ **Único** - Imposible duplicados  
✅ **Legible** - Fácil identificar paciente  
✅ **Automático** - Sin intervención manual  
✅ **Rastreable** - Incluye año de registro  
✅ **Escalable** - Sufijo maneja duplicados  

---

## 🔄 MIGRAR DATOS EXISTENTES (Opcional)

Si ya tienes pacientes en la BD, usa el script incluido:

```bash
python manage.py shell

# Dentro del shell:
>>> exec(open('migrar_historias_clinicas.py').read())

# Seguir instrucciones del menú
```

**Opciones del script:**
1. Migrar todas las HC (regenerar todas)
2. Verificar formato actual
3. Mostrar estadísticas

---

## 📚 DOCUMENTACIÓN COMPLETA

Lee la guía detallada:
[IMPLEMENTACION_HISTORIA_CLINICA.md](computer:///mnt/user-data/outputs/IMPLEMENTACION_HISTORIA_CLINICA.md)

**Incluye:**
- Paso a paso con screenshots conceptuales
- Comandos de backup
- Solución de problemas
- Tests de verificación
- Script de migración de datos

---

## ⚠️ IMPORTANTE ANTES DE EMPEZAR

### 1. Backup de Base de Datos

```bash
mysqldump -u root -p tea_management > backup_$(date +%Y%m%d).sql
```

### 2. Probar en Desarrollo Primero

No aplicar directamente en producción. Probar primero en ambiente de desarrollo.

### 3. Revisar Template

Eliminar el campo `numero_historia_clinica` del template `paciente_form.html`:

```html
<!-- ❌ ELIMINAR esta sección del template -->
<div class="col-md-8">
    <label>Historia Clínica *</label>
    {{ form.numero_historia_clinica }}
</div>
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [ ] Descargar `historia_clinica_automatica.zip`
- [ ] Backup de base de datos
- [ ] Reemplazar clase Paciente en models.py
- [ ] Crear migración: `makemigrations`
- [ ] Aplicar migración: `migrate`
- [ ] Actualizar PacienteForm (quitar campo HC)
- [ ] Actualizar template (quitar campo HC)
- [ ] Reiniciar servidor
- [ ] Probar crear paciente nuevo
- [ ] Verificar HC generada automáticamente
- [ ] (Opcional) Migrar pacientes existentes

---

## 🎉 RESULTADO FINAL

**Antes de guardar:**
```
Formulario con todos los campos
Historia Clínica: [Campo vacío - usuario debe escribir]
```

**Después de guardar:**
```
✅ Paciente Juan Pérez creado exitosamente
Historia Clínica: HC-123456789-2025  ← Auto-generada
```

---

## 📞 SOPORTE

Si tienes problemas:

1. Revisa la guía completa: `IMPLEMENTACION_HISTORIA_CLINICA.md`
2. Verifica logs del servidor: `python manage.py runserver`
3. Usa Django shell para debugging
4. Revisa que la migración se aplicó correctamente

---

**Creado:** 20/11/2025  
**Archivos:** 3 (modelo, guía, script)  
**Tamaño total:** 9.1 KB  
**Estado:** ✅ Listo para implementar
