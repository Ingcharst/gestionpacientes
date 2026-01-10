# 🧪 GUÍA DE TESTING - TEA MANAGEMENT

## 📊 Resumen de Tests Existentes

| Módulo | Tests | Líneas | Cobertura Objetivo |
|--------|-------|--------|-------------------|
| Usuarios | 24 | 306 | 85%+ |
| Terapias | 18 | 315 | 85%+ |
| Consultorios | 22 | 333 | 85%+ |
| Procedimientos | 38 | 589 | 85%+ |
| **TOTAL** | **102** | **1543** | **85%+** |

---

## 🚀 INSTALACIÓN DE DEPENDENCIAS DE TESTING

```bash
# Instalar dependencias de testing
pip install pytest pytest-django pytest-cov coverage --break-system-packages

# O desde requirements.txt (si existe)
pip install -r requirements-test.txt --break-system-packages
```

---

## ▶️ EJECUTAR TESTS

### Opción 1: Script Automático (Recomendado)
```bash
# Dar permisos de ejecución
chmod +x run_tests.sh

# Ejecutar
./run_tests.sh
```

### Opción 2: Django Test Runner
```bash
# Todos los tests
python manage.py test

# Por módulo
python manage.py test apps.usuarios
python manage.py test apps.terapias
python manage.py test apps.consultorios
python manage.py test apps.procedimientos

# Con verbosidad
python manage.py test --verbosity=2

# Tests en paralelo (más rápido)
python manage.py test --parallel

# Detener en primer fallo
python manage.py test --failfast
```

### Opción 3: Pytest (Recomendado para desarrollo)
```bash
# Todos los tests
pytest

# Por módulo
pytest apps/usuarios/tests.py
pytest apps/terapias/tests.py
pytest apps/consultorios/tests.py
pytest apps/procedimientos/tests.py

# Con coverage
pytest --cov=apps --cov-report=html

# Tests específicos
pytest apps/usuarios/tests.py::TestUsuarioModel
pytest apps/usuarios/tests.py::TestUsuarioModel::test_crear_usuario

# Solo tests rápidos (excluir lentos)
pytest -m "not slow"
```

---

## 📈 COBERTURA DE CÓDIGO (Coverage)

### Generar Reporte de Coverage
```bash
# Con coverage
coverage run --source='apps' manage.py test
coverage report
coverage html

# El reporte HTML estará en: htmlcov/index.html
# Ábrelo en tu navegador para ver detalles

# Con pytest
pytest --cov=apps --cov-report=html --cov-report=term-missing
```

### Ver Cobertura por Módulo
```bash
coverage report --show-missing
```

---

## 📋 QUÉ SE ESTÁ TESTEANDO

### Usuarios (24 tests)
✅ Modelo Usuario y campos
✅ Modelo Perfil
✅ Registro de accesos
✅ Autenticación y permisos
✅ CRUD de usuarios
✅ API REST endpoints
✅ Validaciones de formularios

### Terapias (18 tests)
✅ Modelo Terapia y categorías
✅ CRUD de terapias
✅ Filtros y búsqueda
✅ API REST endpoints
✅ Validaciones

### Consultorios (22 tests)
✅ Modelo Consultorio y salas
✅ Sistema de asignaciones
✅ Disponibilidad
✅ CRUD completo
✅ API REST endpoints

### Procedimientos (38 tests)
✅ Modelo Paciente
✅ Modelo SesionTerapeutica
✅ Modelo Procedimiento
✅ Objetivos terapéuticos
✅ Evolución del paciente
✅ CRUD completo
✅ API REST endpoints
✅ Validaciones complejas

---

## 🎯 CÓMO AGREGAR NUEVOS TESTS

### 1. Estructura de un Test
```python
from django.test import TestCase
from apps.usuarios.models import Usuario

class TestNuevoModelo(TestCase):
    """Tests para Nuevo Modelo"""
    
    def setUp(self):
        """Configuración inicial antes de cada test"""
        self.usuario = Usuario.objects.create(
            username='test',
            email='test@test.com'
        )
    
    def test_crear_instancia(self):
        """Test: Crear instancia del modelo"""
        # Arrange (preparar)
        data = {'campo': 'valor'}
        
        # Act (actuar)
        instancia = Modelo.objects.create(**data)
        
        # Assert (verificar)
        self.assertEqual(instancia.campo, 'valor')
        self.assertTrue(instancia.pk)
    
    def tearDown(self):
        """Limpieza después de cada test"""
        pass
```

### 2. Agregar Test a Módulo Existente
```bash
# Editar archivo de tests
nano apps/usuarios/tests.py

# Agregar nuevo método def test_nombre_descriptivo(self):
# Ejecutar solo ese test
pytest apps/usuarios/tests.py::TestClase::test_nombre_descriptivo
```

---

## 🔍 DEBUGGING DE TESTS

### Ver Output Detallado
```bash
# Django
python manage.py test --verbosity=3

# Pytest con prints
pytest -s
pytest --capture=no
```

### Ejecutar Solo Tests Fallidos
```bash
# Pytest
pytest --lf  # last-failed
pytest --ff  # failed-first
```

### PDB (Python Debugger)
```python
def test_algo(self):
    # Agregar breakpoint
    import pdb; pdb.set_trace()
    # El test se pausará aquí
```

---

## ✅ CHECKLIST ANTES DE COMMIT

- [ ] Todos los tests pasan: `python manage.py test`
- [ ] Coverage > 85%: `coverage report`
- [ ] Sin warnings: `python manage.py check`
- [ ] Linting OK: `flake8 apps/`
- [ ] Formato OK: `black apps/`

---

## 📊 MÉTRICAS DE CALIDAD

### Objetivos del Proyecto
- ✅ Cobertura mínima: **85%**
- ✅ Tests por módulo: **15+ tests**
- ✅ Tiempo de ejecución: **< 2 minutos**
- ✅ Tests sin fallos: **100%**

### Comandos de Verificación
```bash
# Cobertura total
coverage report | tail -1

# Número de tests
pytest --collect-only | grep "test session starts" -A 3

# Tiempo de ejecución
pytest --durations=10
```

---

## 🐛 PROBLEMAS COMUNES

### Error: No module named 'django'
```bash
# Solución: Activar virtualenv
source venv/bin/activate
pip install -r requirements.txt --break-system-packages
```

### Error: Database locked
```bash
# Solución: Usar base de datos en memoria para tests
# En settings.py agregar:
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
```

### Tests muy lentos
```bash
# Solución: Ejecutar en paralelo
python manage.py test --parallel auto
```

---

## 📚 RECURSOS

- [Django Testing](https://docs.djangoproject.com/en/5.0/topics/testing/)
- [Pytest-Django](https://pytest-django.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)

---

**Última actualización: 18/11/2025**
**Estado: ✅ 102 tests implementados**
