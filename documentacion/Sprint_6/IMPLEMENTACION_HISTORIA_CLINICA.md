# 🔧 IMPLEMENTACIÓN: Auto-generación de Historia Clínica

## 📋 RESUMEN DE CAMBIOS

**Historia Clínica ahora se genera automáticamente:**
- Formato: `HC-{NUMERO_DOCUMENTO}-{AÑO}`
- Ejemplo: `HC-123456789-2025`
- Si existe duplicado: `HC-123456789-2025-1`

---

## 📦 ARCHIVOS A DESCARGAR

1. [paciente_model_corregido.py](computer:///mnt/user-data/outputs/paciente_model_corregido.py) - Modelo corregido

---

## 🚀 PASO A PASO: IMPLEMENTACIÓN

### **Paso 1: Backup de Base de Datos (CRÍTICO)**

```bash
# Backup de MySQL
mysqldump -u root -p tea_management > backup_antes_migracion_$(date +%Y%m%d).sql

# O desde Django
python manage.py dumpdata procedimientos.Paciente > pacientes_backup.json
```

### **Paso 2: Reemplazar Modelo**

```bash
# 1. Abrir archivo
nano apps/procedimientos/models.py

# 2. Buscar la clase Paciente (línea 13 aprox)
# 3. Reemplazar TODA la clase Paciente con el contenido de:
#    paciente_model_corregido.py
```

**Cambios clave en el modelo:**

```python
# ❌ ANTES (línea 152-157)
numero_historia_clinica = models.CharField(
    max_length=50,
    unique=True,
    verbose_name='Número de Historia Clínica',
    help_text='Número único de historia clínica'
)

# ✅ AHORA
numero_historia_clinica = models.CharField(
    max_length=50,
    unique=True,
    blank=True,  # ← NUEVO: Opcional en formularios
    editable=True,
    verbose_name='Número de Historia Clínica',
    help_text='Se genera automáticamente si no se especifica (HC-{documento}-{año})'
)

# ✅ NUEVO MÉTODO (agregar después de la clase Meta)
def generar_numero_historia_clinica(self):
    """Genera número de historia clínica automáticamente."""
    year = timezone.now().year
    base = f"HC-{self.numero_documento}-{year}"
    
    numero = base
    counter = 1
    queryset = Paciente.objects.filter(numero_historia_clinica=numero)
    if self.pk:
        queryset = queryset.exclude(pk=self.pk)
    
    while queryset.exists():
        numero = f"{base}-{counter}"
        counter += 1
        queryset = Paciente.objects.filter(numero_historia_clinica=numero)
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)
    
    return numero

# ✅ SOBRESCRIBIR SAVE
def save(self, *args, **kwargs):
    """Auto-genera historia clínica si está vacía."""
    if not self.numero_historia_clinica:
        self.numero_historia_clinica = self.generar_numero_historia_clinica()
    super().save(*args, **kwargs)
```

### **Paso 3: Crear Migración**

```bash
python manage.py makemigrations procedimientos
```

**Salida esperada:**
```
Migrations for 'procedimientos':
  procedimientos/migrations/0XXX_alter_paciente_numero_historia_clinica.py
    - Alter field numero_historia_clinica on paciente
```

### **Paso 4: Revisar Migración**

```bash
# Ver la migración generada
cat apps/procedimientos/migrations/0XXX_alter_paciente_numero_historia_clinica.py
```

**Debe verse así:**
```python
operations = [
    migrations.AlterField(
        model_name='paciente',
        name='numero_historia_clinica',
        field=models.CharField(
            blank=True,  # ← Esto es lo importante
            help_text='Se genera automáticamente...',
            max_length=50,
            unique=True,
            verbose_name='Número de Historia Clínica'
        ),
    ),
]
```

### **Paso 5: Aplicar Migración**

```bash
python manage.py migrate procedimientos
```

**Salida esperada:**
```
Running migrations:
  Applying procedimientos.0XXX_alter_paciente_numero_historia_clinica... OK
```

### **Paso 6: Actualizar Formulario**

**Editar:** `apps/procedimientos/forms.py`

```python
class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = [
            'nombres', 'apellidos', 'tipo_documento', 'numero_documento',
            'fecha_nacimiento', 'genero', 'foto',
            'telefono', 'email', 'direccion', 'ciudad',
            'nombre_responsable', 'parentesco_responsable', 
            'telefono_responsable', 'email_responsable',
            'diagnostico_principal', 'alergias', 'medicamentos', 
            'eps', 'estado', 'observaciones', 'necesidades_especiales'
        ]
        # ❌ ELIMINAR 'numero_historia_clinica' de fields
        # Ya no se incluye porque se auto-genera
```

### **Paso 7: Actualizar Template**

**Editar:** `templates/procedimientos/paciente_form.html`

**ELIMINAR** esta sección (líneas 84-91 aprox):

```html
<!-- ❌ ELIMINAR ESTO -->
<div class="col-md-8">
    <label class="form-label fw-semibold">
        <i class="bi bi-file-medical me-1"></i>Historia Clínica <span class="text-danger">*</span>
    </label>
    {{ form.numero_historia_clinica }}
    <small class="form-text text-muted">Número único de identificación médica</small>
    {% if form.numero_historia_clinica.errors %}<div class="invalid-feedback d-block">{{ form.numero_historia_clinica.errors }}</div>{% endif %}
</div>
```

**OPCIONAL:** Agregar badge informativo:

```html
<!-- ✅ AGREGAR ESTO (opcional) -->
<div class="col-12">
    <div class="alert alert-info">
        <i class="bi bi-info-circle me-2"></i>
        La <strong>Historia Clínica</strong> se generará automáticamente al guardar el paciente.
        Formato: HC-{Documento}-{Año}
    </div>
</div>
```

### **Paso 8: Reiniciar Servidor**

```bash
# Detener servidor (Ctrl+C)
# Iniciar nuevamente
python manage.py runserver
```

---

## 🧪 TESTING

### Test 1: Crear Paciente Nuevo

```bash
# Ir a: http://localhost:8000/procedimientos/pacientes/crear/
```

**Datos de prueba:**
- Nombres: Juan
- Apellidos: Pérez
- Número Documento: 123456789
- (Llenar todos los campos requeridos)
- **NO llenar Historia Clínica** (se auto-genera)

**Click:** "Guardar Paciente"

**Resultado esperado:**
```
✅ Paciente Juan Pérez creado exitosamente
✅ Historia Clínica generada: HC-123456789-2025
```

### Test 2: Verificar en Base de Datos

```bash
python manage.py shell

>>> from apps.procedimientos.models import Paciente
>>> p = Paciente.objects.last()
>>> print(p.numero_historia_clinica)
HC-123456789-2025
>>> print(p.nombre_completo)
Juan Pérez
```

### Test 3: Crear Paciente con Mismo Documento

Crear otro paciente con documento `123456789` (mismo año).

**Resultado esperado:**
```
✅ Historia Clínica: HC-123456789-2025-1  ← Con sufijo
```

### Test 4: Crear Paciente el Próximo Año

Cambiar fecha del sistema a 2026 y crear paciente.

**Resultado esperado:**
```
✅ Historia Clínica: HC-123456789-2026  ← Año diferente
```

---

## 🔄 MIGRACIÓN DE DATOS EXISTENTES

Si ya tienes pacientes en la BD sin formato correcto:

### Script de Actualización

```python
# En Django shell: python manage.py shell

from apps.procedimientos.models import Paciente
from django.utils import timezone

# Ver pacientes existentes
print(f"Total pacientes: {Paciente.objects.count()}")

# Regenerar historias clínicas para todos
for paciente in Paciente.objects.all():
    # Limpiar el campo
    paciente.numero_historia_clinica = ''
    # El save() auto-generará el nuevo formato
    paciente.save()
    print(f"✓ {paciente.nombre_completo}: {paciente.numero_historia_clinica}")

print("\n✅ Todas las historias clínicas actualizadas")
```

---

## 📊 FORMATO DE HISTORIA CLÍNICA

### Ejemplos Generados

| Documento | Año | Historia Clínica | Notas |
|-----------|-----|------------------|-------|
| 123456789 | 2025 | HC-123456789-2025 | Primera |
| 123456789 | 2025 | HC-123456789-2025-1 | Duplicado mismo año |
| 123456789 | 2026 | HC-123456789-2026 | Año diferente |
| 987654321 | 2025 | HC-987654321-2025 | Otro paciente |

### Ventajas del Formato

✅ **Único**: Combinación documento + año + sufijo  
✅ **Legible**: Fácil identificar paciente por documento  
✅ **Trazable**: Incluye año de registro  
✅ **Escalable**: Sufijo evita colisiones  
✅ **Automático**: Sin intervención manual  

---

## ⚠️ CONSIDERACIONES IMPORTANTES

### 1. Pacientes Existentes

Si tienes pacientes con historias clínicas manuales:
- **Opción A**: Conservarlas (no hacer nada)
- **Opción B**: Regenerar con script de migración

### 2. Historia Clínica Manual

Si necesitas asignar HC manualmente:
```python
paciente = Paciente(
    nombres='Juan',
    numero_documento='123456',
    numero_historia_clinica='HC-ESPECIAL-001'  # Manual
)
paciente.save()  # Se respeta el valor manual
```

### 3. Backups

**Siempre hacer backup antes de:**
- Crear migraciones
- Aplicar migraciones
- Ejecutar scripts de actualización masiva

### 4. Ambiente de Desarrollo

Probar primero en desarrollo:
```bash
# Copiar BD de producción a desarrollo
# Probar migración
# Si todo OK, aplicar en producción
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: "numero_historia_clinica cannot be null"

**Causa:** Migración aplicada pero modelo no actualizado

**Solución:**
```bash
# Revertir migración
python manage.py migrate procedimientos 0XXX_previous

# Actualizar modelo correctamente
# Volver a crear migración
python manage.py makemigrations
python manage.py migrate
```

### Error: "duplicate key value"

**Causa:** Ya existe una HC con ese número

**Solución:** El método automático maneja esto con sufijos

### Error: Template no encuentra campo

**Causa:** Template aún incluye campo numero_historia_clinica

**Solución:** Eliminar del template como se indicó en Paso 7

---

## ✅ CHECKLIST FINAL

- [ ] Backup de base de datos realizado
- [ ] Modelo Paciente actualizado con nuevos métodos
- [ ] Migración creada: `makemigrations`
- [ ] Migración aplicada: `migrate`
- [ ] Formulario actualizado (sin campo HC)
- [ ] Template actualizado (sin campo HC)
- [ ] Servidor reiniciado
- [ ] Test de creación de paciente exitoso
- [ ] Historia clínica se genera automáticamente
- [ ] Verificado en base de datos
- [ ] Verificado en admin de Django
- [ ] Probado con múltiples pacientes

---

## 📞 COMANDOS RÁPIDOS

```bash
# Backup
mysqldump -u root -p tea_management > backup_$(date +%Y%m%d).sql

# Migración
python manage.py makemigrations procedimientos
python manage.py migrate procedimientos

# Testing
python manage.py shell
>>> from apps.procedimientos.models import Paciente
>>> Paciente.objects.create(
...     nombres='Test',
...     apellidos='Usuario',
...     numero_documento='999888777',
...     fecha_nacimiento='2020-01-01',
...     genero='M',
...     nombre_responsable='Test Responsable',
...     parentesco_responsable='Padre',
...     telefono_responsable='3001234567',
...     diagnostico_principal='Test'
... )
>>> Paciente.objects.last().numero_historia_clinica
'HC-999888777-2025'
```

---

**Creado:** 20/11/2025  
**Estado:** ✅ Listo para implementar  
**Archivo principal:** [paciente_model_corregido.py](computer:///mnt/user-data/outputs/paciente_model_corregido.py)
