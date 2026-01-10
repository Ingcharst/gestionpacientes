# 📊 MÓDULO DE REPORTES - TEA MANAGEMENT

## 🎯 DESCRIPCIÓN

Módulo completo de generación de reportes para el sistema TEA Management, desarrollado siguiendo metodología Scrum.

### Reportes Implementados:

#### ✅ OBLIGATORIOS
1. **Informe Mensual por Paciente** (Para Facturación)
   - Detalle completo de terapias realizadas
   - Detalle completo de procedimientos realizados
   - Totales y subtotales para facturación
   - Exportación: PDF y Excel

2. **Informe Trimestral de Avance del Paciente**
   - Evoluciones clínicas del trimestre
   - Objetivos terapéuticos y progreso
   - Estadísticas de asistencia
   - Terapias recibidas
   - Exportación: PDF

#### 🔥 ADICIONALES
3. **Reporte de Asistencia de Pacientes**
   - Consolidado mensual de todos los pacientes
   - Sesiones programadas vs asistidas
   - Porcentajes de asistencia
   - Exportación: PDF

4. **Reporte de Productividad de Terapeutas**
   - Sesiones por terapeuta
   - Pacientes atendidos
   - Tasas de completitud
   - Exportación: PDF

5. **Reporte de Grupos Terapéuticos**
   - Estado de ocupación de cada grupo
   - Capacidad vs asignados
   - Porcentajes de ocupación
   - Vista web y exportación PDF

---

## 📁 ESTRUCTURA DEL MÓDULO

```
apps/reportes/
├── __init__.py
├── apps.py              # Configuración de la app
├── models.py            # Sin modelos (reportes dinámicos)
├── views.py             # Vistas para generar reportes
├── urls.py              # URLs del módulo
└── utils.py             # Utilidades para PDF y Excel

templates/reportes/
├── dashboard.html                         # Dashboard principal
├── informe_mensual_paciente_form.html    # Form informe mensual
├── informe_trimestral_avance_form.html   # Form informe trimestral
├── reporte_asistencia_form.html          # Form asistencia
├── reporte_terapeutas_form.html          # Form terapeutas
└── reporte_grupos.html                    # Vista de grupos
```

---

## 🚀 INSTALACIÓN

### 1. Copiar Archivos del Módulo

```bash
# Copiar app completa
reportes/  →  apps/reportes/

# Copiar templates
templates_reportes/  →  templates/reportes/
```

### 2. Actualizar Configuración

**A. `config/settings.py`**

Agregar `'apps.reportes'` a `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... apps existentes ...
    'apps.procedimientos',
    'apps.grupos',
    'apps.reportes',  # ← AGREGAR ESTA LÍNEA
]
```

**B. `config/urls.py`**

Agregar ruta de reportes:

```python
urlpatterns = [
    # ... rutas existentes ...
    path('grupos/', include('apps.grupos.urls')),
    path('reportes/', include('apps.reportes.urls')),  # ← AGREGAR ESTA LÍNEA
]
```

**C. `templates/base/base.html`**

Agregar enlace en el sidebar (después de Grupos):

```html
<li class="nav-item">
    <a class="nav-link {% if 'grupos' in request.path %}active{% endif %}" 
       href="{% url 'grupos:grupo_list' %}">
        <i class="bi bi-people-fill me-2"></i> Grupos Terapéuticos
    </a>
</li>
<li class="nav-item">
    <a class="nav-link {% if 'reportes' in request.path %}active{% endif %}" 
       href="{% url 'reportes:dashboard' %}">
        <i class="bi bi-clipboard-data me-2"></i> Reportes
    </a>
</li>
```

### 3. Instalar Dependencias

```bash
# Instalar bibliotecas necesarias
pip install reportlab openpyxl
```

Si estás usando requirements.txt, agregar:
```
reportlab==4.0.9
openpyxl==3.1.2
```

### 4. Verificar Instalación

```bash
# Ejecutar servidor
python manage.py runserver

# Acceder a:
http://localhost:8000/reportes/
```

---

## 📋 USO DE LOS REPORTES

### 1. Informe Mensual por Paciente

**Acceso:** Reportes → Informe Mensual por Paciente

**Pasos:**
1. Seleccionar paciente de la lista
2. Seleccionar mes y año
3. Clic en "Generar PDF" o "Generar Excel"

**Contenido del reporte:**
- Información del paciente (HC, documento)
- Tabla de sesiones terapéuticas con:
  - Fecha, terapia, terapeuta, duración, valor
- Tabla de procedimientos con:
  - Fecha, tipo, profesional, valor
- Totales y subtotales para facturación

**Uso:** Facturación mensual, cobros, auditoría

---

### 2. Informe Trimestral de Avance

**Acceso:** Reportes → Informe Trimestral de Avance

**Pasos:**
1. Seleccionar paciente
2. Seleccionar trimestre (1-4) y año
3. Clic en "Generar PDF"

**Contenido del reporte:**
- Resumen estadístico del trimestre
  - Total sesiones, tasa de asistencia
- Terapias recibidas (top 5)
- Objetivos terapéuticos y progreso
- Evoluciones clínicas (últimas 3)

**Uso:** Evaluación de progreso, reportes a padres/tutores, seguimiento clínico

---

### 3. Reporte de Asistencia

**Acceso:** Reportes → Reporte de Asistencia

**Pasos:**
1. Seleccionar mes y año
2. Clic en "Generar PDF"

**Contenido:**
- Tabla consolidada de todos los pacientes
- Sesiones programadas, asistidas, inasistencias
- Porcentaje de asistencia por paciente

**Uso:** Control de asistencia mensual, identificar ausentismo

---

### 4. Reporte de Terapeutas

**Acceso:** Reportes → Reporte de Terapeutas

**Pasos:**
1. Seleccionar mes y año
2. Clic en "Generar PDF"

**Contenido:**
- Estadísticas por terapeuta:
  - Total de sesiones
  - Sesiones completadas
  - Pacientes atendidos
  - Tasa de completitud

**Uso:** Evaluación de productividad, distribución de carga laboral

---

### 5. Reporte de Grupos

**Acceso:** Reportes → Reporte de Grupos

**Contenido (Vista Web):**
- Tabla de todos los grupos activos
- Capacidad vs asignados
- Cupos disponibles
- Porcentaje de ocupación con barra visual
- Estado (Disponible/Completo)

**Exportación:** Botón "Exportar PDF" en la parte superior

**Uso:** Gestión de cupos, planificación de grupos

---

## 🛠️ CARACTERÍSTICAS TÉCNICAS

### Generación de PDF
- **Biblioteca:** ReportLab
- **Tamaño:** Letter (8.5" x 11")
- **Características:**
  - Encabezados personalizados con colores
  - Tablas formateadas profesionalmente
  - Paginación automática
  - Logo y branding (configurable)

### Generación de Excel
- **Biblioteca:** OpenPyXL
- **Características:**
  - Formato de celdas automático
  - Encabezados con color
  - Ajuste automático de columnas
  - Bordes y alineación

### Utilidades Incluidas
- `ReportePDFGenerator`: Clase base para PDFs
- `ReporteExcelGenerator`: Clase base para Excel
- `calcular_totales_procedimientos()`: Cálculo de totales
- `calcular_totales_sesiones()`: Cálculo de sesiones
- `formato_moneda()`: Formato de pesos colombianos
- `obtener_nombre_mes()`: Nombres de meses en español

---

## 🔒 PERMISOS Y SEGURIDAD

- Todos los reportes requieren `@login_required`
- Los usuarios solo pueden ver reportes de pacientes a los que tienen acceso
- Los archivos se generan on-the-fly (no se almacenan en servidor)
- No hay exposición de datos sensibles en URLs

---

## 📊 ESTADÍSTICAS DEL MÓDULO

| Métrica | Valor |
|---------|-------|
| Reportes Implementados | 5 |
| Vistas Creadas | 11 |
| Templates Creados | 6 |
| Líneas de Código (Python) | ~800 |
| Líneas de Código (HTML) | ~600 |
| Formatos de Exportación | PDF, Excel |
| Tiempo de Desarrollo | 1 Sprint |

---

## 🎨 INTERFAZ DE USUARIO

### Dashboard de Reportes
- Cards con estadísticas generales
- Sección de reportes obligatorios (destacados)
- Sección de reportes adicionales
- Iconos de Bootstrap Icons
- Diseño responsivo

### Formularios
- Campos de selección claros
- Validación en cliente y servidor
- Botones con íconos descriptivos
- Links de navegación intuitivos

---

## 🔧 PERSONALIZACIÓN

### Agregar Nuevos Reportes

1. **Crear vista en `views.py`:**
```python
@login_required
def mi_nuevo_reporte(request):
    # Lógica del reporte
    return render(request, 'reportes/mi_reporte.html', context)
```

2. **Agregar URL en `urls.py`:**
```python
path('mi-reporte/', views.mi_nuevo_reporte, name='mi_reporte'),
```

3. **Crear template en `templates/reportes/`**

4. **Agregar enlace en dashboard**

### Modificar Estilos de PDF

Editar `utils.py` → Clase `ReportePDFGenerator`:
```python
def _setup_custom_styles(self):
    self.styles.add(ParagraphStyle(
        name='TituloReporte',
        fontSize=18,
        textColor=colors.HexColor('#TUCOLOR'),
        # ... más estilos
    ))
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: "ModuleNotFoundError: No module named 'reportlab'"
**Solución:**
```bash
pip install reportlab openpyxl
```

### Error: "NoReverseMatch at /reportes/"
**Causa:** URLs no incluidas en config/urls.py
**Solución:** Verificar que la línea `path('reportes/', include('apps.reportes.urls'))` esté presente

### PDF se genera vacío o con error
**Causas comunes:**
- No hay datos para el período seleccionado
- Error en los filtros de fecha
**Solución:** Verificar que existan sesiones/procedimientos en las fechas seleccionadas

### Excel no descarga en algunos navegadores
**Solución:** Usar un navegador moderno (Chrome, Firefox, Edge)

---

## ✅ VERIFICACIÓN POST-INSTALACIÓN

- [ ] Enlace "Reportes" visible en el sidebar
- [ ] Dashboard de reportes carga correctamente (`/reportes/`)
- [ ] Los 5 reportes son accesibles desde el dashboard
- [ ] El informe mensual genera PDF y Excel
- [ ] El informe trimestral genera PDF
- [ ] Los reportes adicionales generan PDF
- [ ] Los datos en los reportes son correctos

---

## 📈 PRÓXIMAS MEJORAS (Backlog)

1. **Reportes Gráficos:**
   - Gráficos de barras/líneas con matplotlib
   - Exportación de gráficos en PDF

2. **Programación de Reportes:**
   - Envío automático de reportes por email
   - Reportes programados mensuales/trimestrales

3. **Personalización:**
   - Selección de columnas a incluir
   - Filtros avanzados

4. **Dashboard Analítico:**
   - KPIs dinámicos
   - Comparaciones mes a mes

5. **Más Formatos:**
   - Exportación a CSV
   - Exportación a Word (.docx)

---

## 📞 SOPORTE

Para dudas o problemas con el módulo de reportes:
- Revisar este documento
- Consultar la documentación de Django
- Revisar logs del servidor para errores específicos

---

## 📜 LICENCIA Y CRÉDITOS

**Proyecto:** TEA Management System  
**Módulo:** Reportes  
**Versión:** 1.0  
**Desarrollado:** Noviembre 2025  
**Metodología:** Scrum/Agile  
**Tecnologías:** Django 5.0, ReportLab, OpenPyXL, Bootstrap 5

---

**¡Módulo de Reportes completado y listo para producción!** 🎉
