# ✅ CHECKLIST DE INSTALACIÓN Y TESTING

## 📥 PASO 1: DESCARGAR ARCHIVOS

### Templates (Obligatorio)
- [ ] [templates_usuarios.zip](computer:///mnt/user-data/outputs/templates_usuarios.zip)
- [ ] [templates_terapias.zip](computer:///mnt/user-data/outputs/templates_terapias.zip)
- [ ] [templates_consultorios.zip](computer:///mnt/user-data/outputs/templates_consultorios.zip)
- [ ] [templates_procedimientos.zip](computer:///mnt/user-data/outputs/templates_procedimientos.zip)

### Testing (Obligatorio para tests)
- [ ] [testing_setup.zip](computer:///mnt/user-data/outputs/testing_setup.zip)

---

## 📂 PASO 2: EXTRAER ARCHIVOS

```bash
# Templates
unzip templates_usuarios.zip -d templates/
unzip templates_terapias.zip -d templates/
unzip templates_consultorios.zip -d templates/
unzip templates_procedimientos.zip -d templates/

# Testing
unzip testing_setup.zip
```

### Verificar
- [ ] Existe `templates/usuarios/`
- [ ] Existe `templates/terapias/`
- [ ] Existe `templates/consultorios/`
- [ ] Existe `templates/procedimientos/`
- [ ] Existe `pytest.ini` en raíz
- [ ] Existe `.coveragerc` en raíz
- [ ] Existe `run_tests.py` en raíz
- [ ] Existe `TESTING.md` en raíz

---

## 🔧 PASO 3: INSTALAR DEPENDENCIAS

```bash
pip install -r requirements-test.txt --break-system-packages
```

### Verificar instalación
- [ ] pytest instalado: `pytest --version`
- [ ] coverage instalado: `coverage --version`
- [ ] Django tests funcionan: `python manage.py test --help`

---

## ✅ PASO 4: VERIFICAR PROYECTO

```bash
# Verificar configuración
python manage.py check

# Verificar migraciones
python manage.py showmigrations

# Si hay migraciones pendientes
python manage.py migrate
```

### Checklist
- [ ] `python manage.py check` sin errores
- [ ] Base de datos migrada
- [ ] Servidor inicia: `python manage.py runserver`

---

## 🧪 PASO 5: EJECUTAR TESTS

### Primera ejecución
```bash
python run_tests.py
```

Selecciona opción **1** (Ejecutar TODOS los tests)

### Verificar resultados
- [ ] Tests de Usuarios: ✓ PASS
- [ ] Tests de Terapias: ✓ PASS
- [ ] Tests de Consultorios: ✓ PASS
- [ ] Tests de Procedimientos: ✓ PASS

---

## 📊 PASO 6: VERIFICAR COBERTURA

```bash
# Ejecutar con coverage
coverage run --source='apps' manage.py test

# Ver reporte
coverage report

# Generar HTML
coverage html
```

### Objetivo
- [ ] Cobertura > 85%
- [ ] Reporte HTML generado en `htmlcov/`
- [ ] Abrir `htmlcov/index.html` en navegador

---

## 🌐 PASO 7: PROBAR EN NAVEGADOR

```bash
python manage.py runserver
```

### Probar cada módulo
- [ ] Login funciona: `http://localhost:8000/login/`
- [ ] Dashboard funciona: `http://localhost:8000/`
- [ ] Usuarios: `http://localhost:8000/usuarios/`
- [ ] Terapias: `http://localhost:8000/terapias/`
- [ ] Consultorios: `http://localhost:8000/consultorios/`
- [ ] Procedimientos: `http://localhost:8000/procedimientos/`

### Funcionalidades
- [ ] Filtros HTMX funcionan
- [ ] Formularios validan correctamente
- [ ] Se pueden crear registros
- [ ] Se pueden editar registros
- [ ] No hay errores 404
- [ ] No hay errores 500

---

## 📝 PASO 8: CREAR DATOS DE PRUEBA

```bash
# Si existe el script
python generar_datos_prueba.py

# O crear manualmente
python manage.py createsuperuser
```

### Verificar
- [ ] Superusuario creado
- [ ] Datos de prueba creados (opcional)
- [ ] Login con superusuario funciona

---

## 🎯 PASO 9: TESTS ADICIONALES (Opcional)

### Tests por módulo
```bash
python run_tests.py usuarios
python run_tests.py terapias
python run_tests.py consultorios
python run_tests.py procedimientos
```

### Tests específicos
```bash
pytest apps/usuarios/tests.py -v
pytest apps/terapias/tests.py -v
pytest apps/consultorios/tests.py -v
pytest apps/procedimientos/tests.py -v
```

---

## 🚀 PASO 10: PREPARAR PARA PRODUCCIÓN (Opcional)

- [ ] Configurar `.env` con variables de producción
- [ ] `DEBUG = False` en producción
- [ ] Configurar `ALLOWED_HOSTS`
- [ ] Configurar base de datos de producción
- [ ] Configurar archivos estáticos: `collectstatic`
- [ ] Configurar servidor web (nginx/apache)
- [ ] Configurar HTTPS
- [ ] Configurar backup automático

---

## 📊 MÉTRICAS DE ÉXITO

### Mínimo Requerido
- ✅ Todos los tests pasan (102/102)
- ✅ Cobertura > 85%
- ✅ Sin errores en `python manage.py check`
- ✅ Todos los módulos accesibles en navegador

### Óptimo
- ✅ Cobertura > 90%
- ✅ Tiempo de tests < 2 minutos
- ✅ Sin warnings
- ✅ Documentación completa

---

## 🆘 PROBLEMAS COMUNES

### Error: Template not found
```bash
# Verificar que los ZIPs están extraídos
ls templates/usuarios/
ls templates/terapias/
ls templates/consultorios/
ls templates/procedimientos/
```

### Error: No module named 'pytest'
```bash
pip install -r requirements-test.txt --break-system-packages
```

### Tests muy lentos
```bash
# Usar tests en paralelo
python manage.py test --parallel
```

### Base de datos locked
```bash
# En settings.py para tests, usar SQLite en memoria
# Ya está configurado en el proyecto
```

---

## ✅ CONFIRMACIÓN FINAL

### Checklist Completo
- [ ] 5 ZIPs descargados
- [ ] Todos los archivos extraídos
- [ ] Dependencias instaladas
- [ ] `python manage.py check` OK
- [ ] Tests ejecutados (102 tests)
- [ ] Cobertura verificada (>85%)
- [ ] Sistema probado en navegador
- [ ] Sin errores

### Si todo está ✅
**¡FELICIDADES! Tu proyecto está listo para producción 🎉**

---

## 📚 DOCUMENTACIÓN DE REFERENCIA

- [PROYECTO_TESTING_COMPLETO.md](computer:///mnt/user-data/outputs/PROYECTO_TESTING_COMPLETO.md) - **Lee esto primero**
- [TESTING.md](computer:///mnt/user-data/outputs/TESTING.md) - Guía detallada de testing
- [PROYECTO_COMPLETO.md](computer:///mnt/user-data/outputs/PROYECTO_COMPLETO.md) - Info del proyecto

---

**Última actualización: 18/11/2025**  
**Estado: ✅ Proyecto 100% completo y listo para testing**
