# 📥 GUÍA DE DESCARGA - MÓDULO DE REPORTES

## 🎯 ARCHIVOS ZIP DISPONIBLES

### OPCIÓN 1: TODO EN UNO (RECOMENDADO) ⭐
📦 **MODULO_REPORTES_COMPLETO.zip** (25 KB)
- Contiene TODO lo necesario
- App reportes/ completa
- Templates templates_reportes/ completos
- Toda la documentación

**Contenido:**
```
MODULO_REPORTES_COMPLETO.zip
├── reportes/                              # App completa
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── utils.py
│   └── forms.py
├── templates_reportes/                    # Templates HTML
│   ├── dashboard.html
│   ├── informe_mensual_paciente_form.html
│   ├── informe_trimestral_avance_form.html
│   ├── reporte_asistencia_form.html
│   ├── reporte_terapeutas_form.html
│   └── reporte_grupos.html
├── MODULO_REPORTES_DOCUMENTACION.md      # Manual técnico
├── INSTALACION_RAPIDA_REPORTES.txt       # Guía de instalación
└── ENTREGA_MODULO_REPORTES.md            # Resumen ejecutivo
```

---

### OPCIÓN 2: ARCHIVOS SEPARADOS

Si prefieres descargarlos por separado:

📦 **reportes.zip** (8.8 KB)
- Solo la app de Django
- 7 archivos Python

📦 **templates_reportes.zip** (7 KB)
- Solo los templates HTML
- 6 archivos HTML

---

## 🚀 CÓMO USAR LOS ARCHIVOS

### Usando MODULO_REPORTES_COMPLETO.zip:

1. **Descargar y descomprimir:**
   ```bash
   # En tu proyecto Django
   unzip MODULO_REPORTES_COMPLETO.zip
   ```

2. **Copiar a las ubicaciones correctas:**
   ```bash
   # Copiar app
   cp -r reportes/ tu_proyecto/apps/
   
   # Copiar templates
   cp -r templates_reportes/* tu_proyecto/templates/reportes/
   ```

3. **Seguir INSTALACION_RAPIDA_REPORTES.txt**
   - Actualizar settings.py
   - Actualizar urls.py
   - Actualizar base.html
   - Instalar dependencias

---

### Usando archivos separados:

1. **Descargar reportes.zip y templates_reportes.zip**

2. **Descomprimir ambos:**
   ```bash
   unzip reportes.zip
   unzip templates_reportes.zip
   ```

3. **Copiar a las ubicaciones:**
   ```bash
   cp -r reportes/ tu_proyecto/apps/
   cp -r templates_reportes/ tu_proyecto/templates/reportes/
   ```

4. **Seguir guía de instalación en la documentación**

---

## 📋 CHECKLIST POST-DESCARGA

Después de descargar y descomprimir:

- [ ] Carpeta `reportes/` con 7 archivos Python
- [ ] Carpeta `templates_reportes/` con 6 archivos HTML
- [ ] Archivo `MODULO_REPORTES_DOCUMENTACION.md` (manual)
- [ ] Archivo `INSTALACION_RAPIDA_REPORTES.txt` (guía)
- [ ] Archivo `ENTREGA_MODULO_REPORTES.md` (resumen)

---

## 🛠️ INSTALACIÓN RÁPIDA

Después de descargar y copiar los archivos:

```bash
# 1. Instalar dependencias
pip install reportlab==4.0.9 openpyxl==3.1.2

# 2. Actualizar settings.py (agregar 'apps.reportes')
# 3. Actualizar urls.py (agregar ruta reportes/)
# 4. Actualizar base.html (agregar enlace en sidebar)

# 5. Probar
python manage.py runserver
# Ir a: http://localhost:8000/reportes/
```

Ver **INSTALACION_RAPIDA_REPORTES.txt** para detalles completos.

---

## ❓ RESOLUCIÓN DE PROBLEMAS

### Windows:
- Usar WinRAR, 7-Zip o el descompresor integrado
- Hacer clic derecho → "Extraer aquí"

### macOS/Linux:
```bash
unzip MODULO_REPORTES_COMPLETO.zip
# o
unzip reportes.zip
unzip templates_reportes.zip
```

### Si los archivos no se descomprimen:
1. Volver a descargar el archivo
2. Verificar que no esté corrupto
3. Usar otro programa descompresor

---

## 📞 AYUDA

Si tienes problemas para descargar o descomprimir:
1. Descarga archivo por archivo desde los enlaces directos
2. Verifica tu conexión a internet
3. Intenta con otro navegador

---

## ✅ VERIFICACIÓN

Para verificar que descargaste todo correctamente:

```bash
# Debe haber 7 archivos en reportes/
ls reportes/
# Salida esperada:
# __init__.py  apps.py  forms.py  models.py  urls.py  utils.py  views.py

# Debe haber 6 archivos en templates_reportes/
ls templates_reportes/
# Salida esperada:
# dashboard.html
# informe_mensual_paciente_form.html
# informe_trimestral_avance_form.html
# reporte_asistencia_form.html
# reporte_grupos.html
# reporte_terapeutas_form.html
```

---

**¡Listo para instalar el módulo de reportes!** 🚀
