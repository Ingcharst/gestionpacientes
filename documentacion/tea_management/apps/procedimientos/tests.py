"""
Tests para los modelos de procedimientos.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, time, timedelta
from decimal import Decimal

from apps.procedimientos.models import (
    Paciente, Procedimiento, SesionTerapeutica,
    ObjetivoTerapeutico, EvolucionPaciente
)
from apps.usuarios.models import Usuario
from apps.consultorios.models import Consultorio
from apps.terapias.models import Terapia, CategoriaTerapia


class PacienteModelTest(TestCase):
    """Tests para el modelo Paciente."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.usuario = Usuario.objects.create_user(
            username='admin_test',
            password='password123',
            rol='ADMIN'
        )
        
        self.paciente = Paciente.objects.create(
            nombres='Juan',
            apellidos='Pérez',
            tipo_documento='TI',
            numero_documento='1234567890',
            fecha_nacimiento=date(2015, 5, 15),
            genero='M',
            telefono='3001234567',
            email='juan@example.com',
            nombre_responsable='María Pérez',
            parentesco_responsable='Madre',
            telefono_responsable='3007654321',
            diagnostico_principal='TEA',
            numero_historia_clinica='HC-2024-001',
            creado_por=self.usuario
        )
    
    def test_paciente_creacion(self):
        """Test de creación de paciente."""
        self.assertEqual(self.paciente.nombres, 'Juan')
        self.assertEqual(self.paciente.apellidos, 'Pérez')
        self.assertEqual(self.paciente.numero_documento, '1234567890')
    
    def test_paciente_str(self):
        """Test del método __str__."""
        expected = f"{self.paciente.numero_historia_clinica} - Juan Pérez"
        self.assertEqual(str(self.paciente), expected)
    
    def test_nombre_completo_property(self):
        """Test de la propiedad nombre_completo."""
        self.assertEqual(self.paciente.nombre_completo, 'Juan Pérez')
    
    def test_edad_property(self):
        """Test de la propiedad edad."""
        # El paciente nació en 2015, debería tener alrededor de 9-10 años
        self.assertGreaterEqual(self.paciente.edad, 9)
        self.assertLessEqual(self.paciente.edad, 10)
    
    def test_edad_meses_property(self):
        """Test de la propiedad edad_meses."""
        # Debe tener más de 100 meses
        self.assertGreater(self.paciente.edad_meses, 100)
    
    def test_esta_activo_property(self):
        """Test de la propiedad esta_activo."""
        self.assertTrue(self.paciente.esta_activo)
        self.paciente.estado = 'INACTIVO'
        self.assertFalse(self.paciente.esta_activo)
    
    def test_tiene_alergias_property(self):
        """Test de la propiedad tiene_alergias."""
        self.assertFalse(self.paciente.tiene_alergias)
        self.paciente.alergias = 'Penicilina'
        self.assertTrue(self.paciente.tiene_alergias)
    
    def test_agregar_diagnostico_secundario(self):
        """Test del método agregar_diagnostico_secundario."""
        self.paciente.agregar_diagnostico_secundario('TDAH')
        self.assertIn('TDAH', self.paciente.diagnosticos_secundarios)
    
    def test_dar_alta(self):
        """Test del método dar_alta."""
        self.paciente.dar_alta('Completó tratamiento')
        self.assertEqual(self.paciente.estado, 'DADO_ALTA')
        self.assertIsNotNone(self.paciente.fecha_alta)
        self.assertEqual(self.paciente.motivo_inactividad, 'Completó tratamiento')


class ProcedimientoModelTest(TestCase):
    """Tests para el modelo Procedimiento."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.usuario = Usuario.objects.create_user(
            username='terapeuta_test',
            password='password123',
            rol='TERAPEUTA'
        )
        
        self.paciente = Paciente.objects.create(
            nombres='Ana',
            apellidos='García',
            tipo_documento='TI',
            numero_documento='9876543210',
            fecha_nacimiento=date(2016, 3, 20),
            genero='F',
            nombre_responsable='Pedro García',
            parentesco_responsable='Padre',
            telefono_responsable='3009876543',
            diagnostico_principal='TEA',
            numero_historia_clinica='HC-2024-002'
        )
        
        self.consultorio = Consultorio.objects.create(
            nombre='Sala 1',
            codigo='S1-001',
            tipo='INDIVIDUAL',
            piso=1,
            numero='101',
            capacidad=2
        )
        
        self.procedimiento = Procedimiento.objects.create(
            codigo='PROC-2024-001',
            tipo='EVALUACION',
            paciente=self.paciente,
            profesional=self.usuario,
            consultorio=self.consultorio,
            fecha=date.today(),
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            motivo_consulta='Evaluación inicial',
            costo=Decimal('150000.00'),
            creado_por=self.usuario
        )
    
    def test_procedimiento_creacion(self):
        """Test de creación de procedimiento."""
        self.assertEqual(self.procedimiento.codigo, 'PROC-2024-001')
        self.assertEqual(self.procedimiento.tipo, 'EVALUACION')
    
    def test_procedimiento_str(self):
        """Test del método __str__."""
        expected_str = f"PROC-2024-001 - Evaluación - Ana García"
        self.assertEqual(str(self.procedimiento), expected_str)
    
    def test_duracion_calculo_automatico(self):
        """Test del cálculo automático de duración."""
        # El save() debería calcular la duración
        self.assertEqual(self.procedimiento.duracion_minutos, 60)
    
    def test_duracion_formateada_property(self):
        """Test de la propiedad duracion_formateada."""
        self.assertEqual(self.procedimiento.duracion_formateada, '1h')
    
    def test_esta_completado_property(self):
        """Test de la propiedad esta_completado."""
        self.assertFalse(self.procedimiento.esta_completado)
        self.procedimiento.estado = 'COMPLETADO'
        self.assertTrue(self.procedimiento.esta_completado)
    
    def test_completar_metodo(self):
        """Test del método completar."""
        self.procedimiento.completar()
        self.assertEqual(self.procedimiento.estado, 'COMPLETADO')
    
    def test_cancelar_metodo(self):
        """Test del método cancelar."""
        self.procedimiento.cancelar('Paciente no asistió')
        self.assertEqual(self.procedimiento.estado, 'CANCELADO')
        self.assertEqual(self.procedimiento.motivo_cancelacion, 'Paciente no asistió')
    
    def test_validacion_hora_fin(self):
        """Test de validación de hora_fin."""
        procedimiento = Procedimiento(
            codigo='PROC-2024-002',
            tipo='CONSULTA',
            paciente=self.paciente,
            profesional=self.usuario,
            fecha=date.today(),
            hora_inicio=time(10, 0),
            hora_fin=time(9, 0),  # Hora fin antes de hora inicio
            motivo_consulta='Test',
            costo=Decimal('100000.00')
        )
        
        with self.assertRaises(ValidationError):
            procedimiento.full_clean()


class SesionTerapeuticaModelTest(TestCase):
    """Tests para el modelo SesionTerapeutica."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.terapeuta = Usuario.objects.create_user(
            username='terapeuta_test',
            password='password123',
            rol='TERAPEUTA'
        )
        
        self.paciente = Paciente.objects.create(
            nombres='Carlos',
            apellidos='Rodríguez',
            tipo_documento='TI',
            numero_documento='1111111111',
            fecha_nacimiento=date(2014, 7, 10),
            genero='M',
            nombre_responsable='Laura Rodríguez',
            parentesco_responsable='Madre',
            telefono_responsable='3001111111',
            diagnostico_principal='TEA',
            numero_historia_clinica='HC-2024-003'
        )
        
        self.categoria = CategoriaTerapia.objects.create(
            nombre='Terapia del Lenguaje',
            codigo='TL',
            descripcion='Terapias de lenguaje y comunicación'
        )
        
        self.terapia = Terapia.objects.create(
            nombre='Terapia de Lenguaje Individual',
            codigo='TLI-001',
            categoria=self.categoria,
            descripcion='Terapia individual de lenguaje',
            modalidad='INDIVIDUAL',
            especialidad='LENGUAJE',
            duracion_minutos=60,
            frecuencia_semanal_recomendada=2,
            costo_sesion=Decimal('120000.00')
        )
        
        self.consultorio = Consultorio.objects.create(
            nombre='Sala 2',
            codigo='S2-001',
            tipo='LENGUAJE',
            piso=1,
            numero='102',
            capacidad=2
        )
        
        self.sesion = SesionTerapeutica.objects.create(
            numero_sesion='SES-2024-001',
            paciente=self.paciente,
            terapeuta=self.terapeuta,
            terapia=self.terapia,
            consultorio=self.consultorio,
            fecha=date.today(),
            hora_inicio=time(14, 0),
            hora_fin=time(15, 0),
            duracion_programada_minutos=60,
            objetivos_sesion='Mejorar pronunciación',
            actividades_realizadas='Ejercicios de articulación',
            costo=Decimal('120000.00'),
            creado_por=self.terapeuta
        )
    
    def test_sesion_creacion(self):
        """Test de creación de sesión."""
        self.assertEqual(self.sesion.numero_sesion, 'SES-2024-001')
        self.assertEqual(self.sesion.paciente, self.paciente)
    
    def test_sesion_str(self):
        """Test del método __str__."""
        expected = f"SES-2024-001 - Terapia de Lenguaje Individual - Carlos Rodríguez"
        self.assertEqual(str(self.sesion), expected)
    
    def test_duracion_real_calculo(self):
        """Test del cálculo de duración real."""
        self.assertEqual(self.sesion.duracion_real_minutos, 60)
    
    def test_esta_completada_property(self):
        """Test de la propiedad esta_completada."""
        self.assertFalse(self.sesion.esta_completada)
        self.sesion.estado = 'COMPLETADA'
        self.assertTrue(self.sesion.esta_completada)
    
    def test_asistio_property(self):
        """Test de la propiedad asistio."""
        self.assertTrue(self.sesion.asistio)  # Por defecto es ASISTIO
        self.sesion.tipo_asistencia = 'NO_ASISTIO'
        self.assertFalse(self.sesion.asistio)
    
    def test_completar_metodo(self):
        """Test del método completar."""
        self.sesion.completar('Sesión exitosa')
        self.assertEqual(self.sesion.estado, 'COMPLETADA')
        self.assertIn('Sesión exitosa', self.sesion.observaciones_terapeuta)
    
    def test_cancelar_metodo(self):
        """Test del método cancelar."""
        self.sesion.cancelar('Enfermedad del paciente')
        self.assertEqual(self.sesion.estado, 'CANCELADA')
        self.assertEqual(self.sesion.motivo_cancelacion, 'Enfermedad del paciente')
    
    def test_reprogramar_metodo(self):
        """Test del método reprogramar."""
        nueva_fecha = date.today() + timedelta(days=1)
        nueva_hora = time(10, 0)
        
        nueva_sesion = self.sesion.reprogramar(nueva_fecha, nueva_hora, 'Conflicto de horario')
        
        self.assertEqual(self.sesion.estado, 'REPROGRAMADA')
        self.assertEqual(nueva_sesion.fecha, nueva_fecha)
        self.assertEqual(nueva_sesion.hora_inicio, nueva_hora)
    
    def test_agregar_tecnica(self):
        """Test del método agregar_tecnica."""
        self.sesion.agregar_tecnica('Ejercicios de respiración')
        self.assertIn('Ejercicios de respiración', self.sesion.tecnicas_utilizadas)
    
    def test_agregar_material(self):
        """Test del método agregar_material."""
        self.sesion.agregar_material('Espejo')
        self.assertIn('Espejo', self.sesion.materiales_utilizados)
    
    def test_promedio_desempeno_property(self):
        """Test de la propiedad promedio_desempeno."""
        self.sesion.desempeno_paciente = 8
        self.sesion.nivel_atencion = 7
        self.sesion.nivel_participacion = 9
        promedio = self.sesion.promedio_desempeno
        self.assertAlmostEqual(promedio, 8.0, places=1)


class ObjetivoTerapeuticoModelTest(TestCase):
    """Tests para el modelo ObjetivoTerapeutico."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.terapeuta = Usuario.objects.create_user(
            username='terapeuta_test',
            password='password123',
            rol='TERAPEUTA'
        )
        
        self.paciente = Paciente.objects.create(
            nombres='Luis',
            apellidos='Martínez',
            tipo_documento='TI',
            numero_documento='2222222222',
            fecha_nacimiento=date(2013, 9, 5),
            genero='M',
            nombre_responsable='Carmen Martínez',
            parentesco_responsable='Madre',
            telefono_responsable='3002222222',
            diagnostico_principal='TEA',
            numero_historia_clinica='HC-2024-004'
        )
        
        self.categoria = CategoriaTerapia.objects.create(
            nombre='Terapia Conductual',
            codigo='TC',
            descripcion='Terapias conductuales'
        )
        
        self.terapia = Terapia.objects.create(
            nombre='Terapia ABA',
            codigo='ABA-001',
            categoria=self.categoria,
            descripcion='Terapia conductual ABA',
            modalidad='INDIVIDUAL',
            especialidad='CONDUCTUAL',
            duracion_minutos=90,
            frecuencia_semanal_recomendada=3,
            costo_sesion=Decimal('150000.00')
        )
        
        self.objetivo = ObjetivoTerapeutico.objects.create(
            paciente=self.paciente,
            terapia=self.terapia,
            titulo='Mejorar contacto visual',
            descripcion='Incrementar la frecuencia de contacto visual durante las interacciones',
            area_desarrollo='Comunicación no verbal',
            prioridad='ALTA',
            fecha_inicio=date.today(),
            fecha_limite=date.today() + timedelta(days=90),
            criterios_exito='Mantener contacto visual por 3 segundos en 8 de 10 interacciones',
            creado_por=self.terapeuta
        )
    
    def test_objetivo_creacion(self):
        """Test de creación de objetivo."""
        self.assertEqual(self.objetivo.titulo, 'Mejorar contacto visual')
        self.assertEqual(self.objetivo.prioridad, 'ALTA')
    
    def test_objetivo_str(self):
        """Test del método __str__."""
        expected = f"Mejorar contacto visual - Luis Martínez"
        self.assertEqual(str(self.objetivo), expected)
    
    def test_esta_logrado_property(self):
        """Test de la propiedad esta_logrado."""
        self.assertFalse(self.objetivo.esta_logrado)
        self.objetivo.estado = 'LOGRADO'
        self.assertTrue(self.objetivo.esta_logrado)
    
    def test_dias_transcurridos_property(self):
        """Test de la propiedad dias_transcurridos."""
        self.assertEqual(self.objetivo.dias_transcurridos, 0)  # Hoy mismo
    
    def test_dias_restantes_property(self):
        """Test de la propiedad dias_restantes."""
        self.assertEqual(self.objetivo.dias_restantes, 90)
    
    def test_marcar_logrado_metodo(self):
        """Test del método marcar_logrado."""
        self.objetivo.marcar_logrado()
        self.assertEqual(self.objetivo.estado, 'LOGRADO')
        self.assertIsNotNone(self.objetivo.fecha_logro)
        self.assertEqual(self.objetivo.porcentaje_avance, 100)
    
    def test_actualizar_avance_metodo(self):
        """Test del método actualizar_avance."""
        self.objetivo.actualizar_avance(50)
        self.assertEqual(self.objetivo.porcentaje_avance, 50)
        
        # Si llega a 100, debe marcarse como logrado
        self.objetivo.actualizar_avance(100)
        self.assertEqual(self.objetivo.estado, 'LOGRADO')


class EvolucionPacienteModelTest(TestCase):
    """Tests para el modelo EvolucionPaciente."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.profesional = Usuario.objects.create_user(
            username='profesional_test',
            password='password123',
            rol='PSICOLOGO'
        )
        
        self.paciente = Paciente.objects.create(
            nombres='Elena',
            apellidos='Suárez',
            tipo_documento='TI',
            numero_documento='3333333333',
            fecha_nacimiento=date(2015, 11, 25),
            genero='F',
            nombre_responsable='Roberto Suárez',
            parentesco_responsable='Padre',
            telefono_responsable='3003333333',
            diagnostico_principal='TEA',
            numero_historia_clinica='HC-2024-005'
        )
        
        self.evolucion = EvolucionPaciente.objects.create(
            paciente=self.paciente,
            fecha=date.today(),
            profesional=self.profesional,
            tipo_nota='Evolución',
            titulo='Progreso en comunicación',
            contenido='La paciente muestra avances significativos en comunicación verbal.'
        )
    
    def test_evolucion_creacion(self):
        """Test de creación de evolución."""
        self.assertEqual(self.evolucion.titulo, 'Progreso en comunicación')
        self.assertEqual(self.evolucion.paciente, self.paciente)
    
    def test_evolucion_str(self):
        """Test del método __str__."""
        fecha_str = date.today().strftime('%Y-%m-%d')
        expected = f"{fecha_str} - Progreso en comunicación - Elena Suárez"
        self.assertEqual(str(self.evolucion), expected)


class IntegrationTest(TestCase):
    """Tests de integración del módulo completo."""
    
    def setUp(self):
        """Configuración inicial para tests de integración."""
        self.terapeuta = Usuario.objects.create_user(
            username='terapeuta_int',
            password='password123',
            rol='TERAPEUTA'
        )
        
        self.paciente = Paciente.objects.create(
            nombres='Integración',
            apellidos='Test',
            tipo_documento='TI',
            numero_documento='4444444444',
            fecha_nacimiento=date(2014, 1, 1),
            genero='M',
            nombre_responsable='Test Responsable',
            parentesco_responsable='Padre',
            telefono_responsable='3004444444',
            diagnostico_principal='TEA',
            numero_historia_clinica='HC-2024-006',
            creado_por=self.terapeuta
        )
    
    def test_flujo_completo_sesion_terapeutica(self):
        """Test del flujo completo de una sesión terapéutica."""
        # 1. Crear categoría y terapia
        categoria = CategoriaTerapia.objects.create(
            nombre='Test Categoría',
            codigo='TEST',
            descripcion='Categoría de prueba'
        )
        
        terapia = Terapia.objects.create(
            nombre='Terapia de Test',
            codigo='TEST-001',
            categoria=categoria,
            descripcion='Terapia de prueba',
            modalidad='INDIVIDUAL',
            especialidad='LENGUAJE',
            duracion_minutos=60,
            frecuencia_semanal_recomendada=2,
            costo_sesion=Decimal('100000.00')
        )
        
        # 2. Crear consultorio
        consultorio = Consultorio.objects.create(
            nombre='Consultorio Test',
            codigo='CT-001',
            tipo='INDIVIDUAL',
            piso=1,
            numero='999',
            capacidad=2
        )
        
        # 3. Crear objetivo terapéutico
        objetivo = ObjetivoTerapeutico.objects.create(
            paciente=self.paciente,
            terapia=terapia,
            titulo='Objetivo de prueba',
            descripcion='Descripción del objetivo',
            area_desarrollo='Test',
            fecha_inicio=date.today(),
            criterios_exito='Criterios de prueba',
            creado_por=self.terapeuta
        )
        
        # 4. Crear sesión terapéutica
        sesion = SesionTerapeutica.objects.create(
            numero_sesion='TEST-SES-001',
            paciente=self.paciente,
            terapeuta=self.terapeuta,
            terapia=terapia,
            consultorio=consultorio,
            fecha=date.today(),
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
            duracion_programada_minutos=60,
            objetivos_sesion='Trabajar en el objetivo',
            actividades_realizadas='Actividades de prueba',
            costo=Decimal('100000.00'),
            desempeno_paciente=8,
            creado_por=self.terapeuta
        )
        
        # 5. Crear evolución
        evolucion = EvolucionPaciente.objects.create(
            paciente=self.paciente,
            sesion=sesion,
            fecha=date.today(),
            profesional=self.terapeuta,
            tipo_nota='Evolución',
            titulo='Nota de evolución',
            contenido='Evolución de la sesión'
        )
        
        # Verificar relaciones
        self.assertEqual(self.paciente.sesiones.count(), 1)
        self.assertEqual(self.paciente.objetivos_terapeuticos.count(), 1)
        self.assertEqual(self.paciente.evoluciones.count(), 1)
        self.assertEqual(sesion.duracion_real_minutos, 60)
        
        # Completar sesión
        sesion.completar('Sesión exitosa')
        self.assertEqual(sesion.estado, 'COMPLETADA')
        
        # Actualizar objetivo
        objetivo.actualizar_avance(25)
        self.assertEqual(objetivo.porcentaje_avance, 25)
