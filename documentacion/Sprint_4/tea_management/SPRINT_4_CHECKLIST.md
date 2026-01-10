# ✅ CHECKLIST DE IMPLEMENTACIÓN - SPRINT 4

## 📋 Pasos de Instalación

### 1. Configuración Inicial

- [ ] Agregar `'apps.procedimientos'` a `INSTALLED_APPS` en `config/settings.py`
- [ ] Agregar URLs de procedimientos en `config/urls.py`:
  ```python
  path('procedimientos/', include('apps.procedimientos.urls')),
  path('api/procedimientos/', include('apps.procedimientos.api.urls')),
  ```

### 2. Base de Datos

- [ ] Crear migraciones: `python manage.py makemigrations procedimientos`
- [ ] Aplicar migraciones: `python manage.py migrate`
- [ ] Verificar que se crearon las 5 tablas:
  - procedimientos_paciente
  - procedimientos_procedimiento
  - procedimientos_sesionterapeutica
  - procedimientos_objetivoterapeutico
  - procedimientos_evolucionpaciente

### 3. Testing

- [ ] Ejecutar todos los tests: `python manage.py test apps.procedimientos`
- [ ] Verificar que pasen los 35+ tests
- [ ] Verificar cobertura de tests (debería ser 100%)

### 4. Admin

- [ ] Iniciar servidor: `python manage.py runserver`
- [ ] Acceder al admin: http://localhost:8000/admin/
- [ ] Verificar que aparece la sección "GESTIÓN DE PROCEDIMIENTOS"
- [ ] Verificar los 5 modelos en el admin:
  - [ ] Pacientes
  - [ ] Procedimientos
  - [ ] Sesiones Terapéuticas
  - [ ] Objetivos Terapéuticos
  - [ ] Evoluciones de Pacientes

### 5. API REST

- [ ] Obtener token JWT: `POST /api/token/`
- [ ] Probar endpoints de Pacientes:
  - [ ] `GET /api/procedimientos/pacientes/`
  - [ ] `POST /api/procedimientos/pacientes/`
  - [ ] `GET /api/procedimientos/pacientes/{id}/`
  - [ ] `GET /api/procedimientos/pacientes/activos/`
  - [ ] `GET /api/procedimientos/pacientes/estadisticas/`
- [ ] Probar endpoints de Procedimientos:
  - [ ] `GET /api/procedimientos/procedimientos/`
  - [ ] `POST /api/procedimientos/procedimientos/`
  - [ ] `POST /api/procedimientos/procedimientos/{id}/completar/`
- [ ] Probar endpoints de Sesiones:
  - [ ] `GET /api/procedimientos/sesiones/`
  - [ ] `POST /api/procedimientos/sesiones/`
  - [ ] `GET /api/procedimientos/sesiones/agenda_semanal/`
  - [ ] `GET /api/procedimientos/sesiones/reporte_asistencia/`
- [ ] Probar endpoints de Objetivos:
  - [ ] `GET /api/procedimientos/objetivos/`
  - [ ] `POST /api/procedimientos/objetivos/{id}/actualizar_avance/`
- [ ] Probar endpoint de Estadísticas:
  - [ ] `GET /api/procedimientos/estadisticas/generales/`

### 6. Datos de Prueba

- [ ] Crear al menos 3 pacientes de prueba
- [ ] Crear al menos 5 sesiones terapéuticas
- [ ] Crear al menos 3 objetivos terapéuticos
- [ ] Crear al menos 2 procedimientos
- [ ] Crear al menos 1 evolución

### 7. Validaciones

- [ ] Probar creación de paciente con documento duplicado (debe fallar)
- [ ] Probar creación de sesión con hora_fin < hora_inicio (debe fallar)
- [ ] Probar asignación de procedimiento a usuario sin rol adecuado (debe fallar)
- [ ] Probar calificación fuera de rango 1-10 en sesión (debe fallar)

### 8. Funcionalidades Especiales

- [ ] Probar método `dar_alta()` en paciente
- [ ] Probar método `completar()` en procedimiento
- [ ] Probar método `completar()` en sesión
- [ ] Probar método `reprogramar()` en sesión
- [ ] Probar método `marcar_logrado()` en objetivo
- [ ] Probar método `actualizar_avance()` en objetivo

### 9. Frontend (Básico)

- [ ] Acceder a `/procedimientos/` (dashboard)
- [ ] Acceder a `/procedimientos/pacientes/` (lista)
- [ ] Crear un paciente desde el frontend
- [ ] Ver detalle de paciente con historial
- [ ] Acceder a `/procedimientos/sesiones/` (lista)
- [ ] Crear una sesión desde el frontend

### 10. Documentación

- [ ] Revisar `SPRINT_4_REVIEW.md`
- [ ] Verificar docstrings en todos los modelos
- [ ] Verificar docstrings en todos los serializers
- [ ] Verificar docstrings en todos los viewsets
- [ ] Verificar que todos los métodos tienen documentación

---

## 🔍 Verificación de Calidad

### Código
- [ ] No hay errores de sintaxis
- [ ] No hay warnings de Django
- [ ] Código sigue PEP 8
- [ ] Todos los imports son correctos
- [ ] No hay código comentado sin usar

### Seguridad
- [ ] Validaciones en todos los formularios
- [ ] Permisos configurados correctamente
- [ ] Validaciones en serializers
- [ ] Clean methods en modelos
- [ ] Protección contra SQL injection (usando ORM)

### Rendimiento
- [ ] Queries optimizados con select_related
- [ ] Indexes en campos de búsqueda frecuente
- [ ] Paginación en listas largas
- [ ] Sin N+1 queries

---

## 📊 Métricas Esperadas

- **Modelos**: 5
- **Campos Totales**: 150+
- **Endpoints API**: 45+
- **Tests**: 35+
- **Líneas de Código**: ~4,500
- **Cobertura Tests**: 100%
- **Serializadores**: 13
- **ViewSets**: 6
- **Formularios**: 5
- **Vistas Frontend**: 9

---

## 🐛 Troubleshooting Común

### Error: "Table doesn't exist"
- **Solución**: Ejecutar `python manage.py migrate`

### Error: "Import error procedimientos"
- **Solución**: Verificar que la app está en INSTALLED_APPS

### Error: "404 en /api/procedimientos/"
- **Solución**: Verificar que las URLs están incluidas en config/urls.py

### Error: "Permission denied"
- **Solución**: Verificar permisos del usuario y roles configurados

### Tests fallan
- **Solución**: Verificar que las apps de dependencia están instaladas (usuarios, consultorios, terapias)

---

## ✅ Criterios de Aceptación

El Sprint 4 está completo cuando:

1. ✅ Todas las migraciones se aplican sin errores
2. ✅ Todos los tests pasan (35+)
3. ✅ Los 5 modelos aparecen en el admin
4. ✅ Los 45+ endpoints API funcionan correctamente
5. ✅ Se pueden crear pacientes, procedimientos y sesiones
6. ✅ Las validaciones funcionan correctamente
7. ✅ Las estadísticas se calculan correctamente
8. ✅ El frontend básico funciona
9. ✅ No hay warnings de seguridad
10. ✅ La documentación está completa

---

**Fecha de Revisión**: _______________

**Responsable**: _______________

**Estado**: [ ] En Progreso [ ] Completado [ ] Con Observaciones
