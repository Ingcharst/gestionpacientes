# 🎯 SOLUCIÓN DEFINITIVA - Sistema IA Completo

## 📦 CONTENIDO

### 📄 Documentación
1. **GUIA_5_MINUTOS.txt** - Guía rápida paso a paso
2. **AGREGAR_CAMPO_TERAPIA.txt** - Documentación completa
3. **CODIGO_COPIAR_PEGAR.txt** - Código listo para usar

### 🐍 Scripts
4. **asignar_terapias.py** - Script automático asignación

### 🤖 Archivos IA
5. **predictor.py** - Motor IA corregido
6. **reglas.py** - Filtros actualizados
7. **features.py** - Extractor features
8. **scoring.py** - Calculador scores

---

## ⚡ APLICACIÓN RÁPIDA (5 minutos)

### Paso 1: Agregar campo al modelo (1 min)

**Archivo:** `E:\TEA_Center\tea_management\apps\grupos\models.py`

**Agregar import:**
```python
from apps.terapias.models import Terapia
```

**Agregar campo en GrupoTerapeutico:**
```python
terapia = models.ForeignKey(
    Terapia,
    on_delete=models.PROTECT,
    related_name='grupos_terapeuticos',
    verbose_name='Terapia',
    null=True,
    blank=True,
    help_text='Tipo de terapia que ofrece este grupo'
)
```

Ver **CODIGO_COPIAR_PEGAR.txt** para código exacto.

---

### Paso 2: Crear y aplicar migración (1 min)

```bash
python manage.py makemigrations grupos
python manage.py migrate grupos
```

---

### Paso 3: Asignar terapias (2 min)

```bash
# Copiar script a raíz
cp asignar_terapias.py E:\TEA_Center\tea_management\

# Ejecutar
python asignar_terapias.py
```

O asignar manualmente en admin.

---

### Paso 4: Instalar archivos IA (1 min)

```bash
# Copiar a: E:\TEA_Center\tea_management\apps\ml_models\
cp predictor.py apps/ml_models/
cp reglas.py apps/ml_models/
cp features.py apps/ml_models/
cp scoring.py apps/ml_models/
```

---

### Paso 5: Reiniciar y probar (30 seg)

```bash
python manage.py runserver
```

Probar en:
```
http://127.0.0.1:8000/grupos/paciente/17/recomendar-grupos/
```

---

## ✅ RESULTADO

✅ Campo terapia agregado sin perder datos
✅ Grupos con terapias asignadas
✅ IA filtra correctamente por terapia
✅ Recomendaciones óptimas
✅ Sistema completo funcional

---

## 📋 CHECKLIST COMPLETO

```
Preparación:
☐ Backup de BD (opcional pero recomendado)
☐ Verificar que existe app terapias

Modelo:
☐ Agregar import Terapia
☐ Agregar campo terapia a GrupoTerapeutico
☐ Guardar archivo

Migraciones:
☐ makemigrations grupos
☐ migrate grupos
☐ Verificar sin errores

Asignación:
☐ Copiar asignar_terapias.py
☐ Ejecutar script
☐ Verificar grupos asignados
☐ Asignar pendientes manualmente (si hay)

Sistema IA:
☐ Copiar 4 archivos .py a ml_models
☐ Reiniciar servidor
☐ Probar recomendaciones
☐ ✓ Funciona correctamente
```

---

## 🆘 SOPORTE

### Error: "No module named 'apps.terapias'"

Cambiar import por:
```python
from terapias.models import Terapia
```

### Grupos sin terapia después del script

Asignar manualmente:
```
http://127.0.0.1:8000/admin/grupos/grupoterapeutico/
```

### Error en migración

Revertir y corregir:
```bash
python manage.py migrate grupos <numero_anterior>
```

---

## 🎯 VENTAJAS DE ESTA SOLUCIÓN

✅ **Definitiva** - No más errores de terapia
✅ **Correcta** - Estructura BD profesional
✅ **Segura** - Preserva datos existentes
✅ **Escalable** - Fácil mantener
✅ **IA Óptima** - Filtra por terapia específica
✅ **Reversible** - Puede revertirse si necesario

---

## ⏱️ TIEMPO TOTAL: 5 MINUTOS

1. Modificar modelo: 1 min
2. Migraciones: 1 min
3. Asignar terapias: 2 min
4. Copiar archivos IA: 1 min
5. Reiniciar y probar: 30 seg

---

## 📖 DOCUMENTACIÓN

Ver **GUIA_5_MINUTOS.txt** para instrucciones paso a paso.
Ver **AGREGAR_CAMPO_TERAPIA.txt** para documentación completa.

---

**¡Éxito con la implementación!** 🚀
