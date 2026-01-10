"""
Tests para el módulo de consultorios.
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta, date, time
from apps.consultorios.models import (
    Consultorio, Sala, AsignacionConsultorio, DisponibilidadConsultorio
)
from apps.usuarios.models import Usuario


class ConsultorioModelTest(TestCase):
    """Tests para el modelo Consultorio."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.consultorio = Consultorio.objects.create(
            nombre='Consultorio 101',
            codigo='C101',
            tipo=Consultorio.TipoConsultorio.INDIVIDUAL,
            piso=1,
            numero='101',
            capacidad=2,
            area_metros=15.50
        )
    
    def test_crear_consultorio_valido(self):
        """Test de creación de consultorio válido."""
        self.assertTrue(isinstance(self.consultorio, Consultorio))
        self.assertEqual(self.consultorio.codigo, 'C101')
        self.assertEqual(self.consultorio.piso, 1)
    
    def test_consultorio_str(self):
        """Test del método __str__."""
        expected = f"{self.consultorio.codigo} - {self.consultorio.nombre}"
        self.assertEqual(str(self.consultorio), expected)
    
    def test_nombre_completo_property(self):
        """Test de la propiedad nombre_completo."""
        expected = f"Piso {self.consultorio.piso} - {self.consultorio.nombre} ({self.consultorio.numero})"
        self.assertEqual(self.consultorio.nombre_completo, expected)
    
    def test_esta_disponible_property(self):
        """Test de la propiedad esta_disponible."""
        self.consultorio.estado = Consultorio.EstadoConsultorio.DISPONIBLE
        self.consultorio.activo = True
        self.consultorio.save()
        self.assertTrue(self.consultorio.esta_disponible)
        
        self.consultorio.estado = Consultorio.EstadoConsultorio.OCUPADO
        self.consultorio.save()
        self.assertFalse(self.consultorio.esta_disponible)
    
    def test_tiene_equipamiento_property(self):
        """Test de la propiedad tiene_equipamiento."""
        self.assertFalse(self.consultorio.tiene_equipamiento)
        
        self.consultorio.agregar_equipo('Mesa', 1)
        self.assertTrue(self.consultorio.tiene_equipamiento)
    
    def test_agregar_equipo(self):
        """Test del método agregar_equipo."""
        self.consultorio.agregar_equipo('Silla', 4)
        self.assertEqual(len(self.consultorio.equipamiento), 1)
        self.assertEqual(self.consultorio.equipamiento[0]['nombre'], 'Silla')
        self.assertEqual(self.consultorio.equipamiento[0]['cantidad'], 4)


class SalaModelTest(TestCase):
    """Tests para el modelo Sala."""
    
    def setUp(self):
        """Configuración inicial."""
        self.consultorio = Consultorio.objects.create(
            nombre='Consultorio 201',
            codigo='C201',
            tipo=Consultorio.TipoConsultorio.GRUPAL,
            piso=2,
            numero='201',
            capacidad=10
        )
        
        self.sala = Sala.objects.create(
            consultorio=self.consultorio,
            nombre='Área de Juego',
            tipo=Sala.TipoSala.JUEGO,
            area_metros=8.0
        )
    
    def test_crear_sala_valida(self):
        """Test de creación de sala válida."""
        self.assertTrue(isinstance(self.sala, Sala))
        self.assertEqual(self.sala.consultorio, self.consultorio)
    
    def test_sala_str(self):
        """Test del método __str__."""
        expected = f"{self.consultorio.codigo} - {self.sala.nombre}"
        self.assertEqual(str(self.sala), expected)
    
    def test_unique_together_constraint(self):
        """Test de restricción unique_together."""
        from django.db import IntegrityError
        
        with self.assertRaises(IntegrityError):
            Sala.objects.create(
                consultorio=self.consultorio,
                nombre='Área de Juego',  # Mismo nombre
                tipo=Sala.TipoSala.TERAPIA
            )


class AsignacionConsultorioModelTest(TestCase):
    """Tests para el modelo AsignacionConsultorio."""
    
    def setUp(self):
        """Configuración inicial."""
        self.consultorio = Consultorio.objects.create(
            nombre='Consultorio 301',
            codigo='C301',
            tipo=Consultorio.TipoConsultorio.INDIVIDUAL,
            piso=3,
            numero='301',
            capacidad=1
        )
        
        self.terapeuta = Usuario.objects.create_user(
            username='terapeuta_test',
            password='Test123!',
            rol=Usuario.Rol.TERAPEUTA,
            first_name='María',
            last_name='González'
        )
        
        self.asignacion = AsignacionConsultorio.objects.create(
            consultorio=self.consultorio,
            terapeuta=self.terapeuta,
            tipo_asignacion=AsignacionConsultorio.TipoAsignacion.PERMANENTE,
            fecha_inicio=date.today()
        )
    
    def test_crear_asignacion_valida(self):
        """Test de creación de asignación válida."""
        self.assertTrue(isinstance(self.asignacion, AsignacionConsultorio))
        self.assertEqual(self.asignacion.terapeuta, self.terapeuta)
    
    def test_asignacion_str(self):
        """Test del método __str__."""
        expected = f"{self.terapeuta.get_full_name()} - {self.consultorio.nombre}"
        self.assertEqual(str(self.asignacion), expected)
    
    def test_esta_vigente_property(self):
        """Test de la propiedad esta_vigente."""
        self.assertTrue(self.asignacion.esta_vigente)
        
        # Asignación futura
        asignacion_futura = AsignacionConsultorio.objects.create(
            consultorio=self.consultorio,
            terapeuta=self.terapeuta,
            tipo_asignacion=AsignacionConsultorio.TipoAsignacion.TEMPORAL,
            fecha_inicio=date.today() + timedelta(days=30)
        )
        self.assertFalse(asignacion_futura.esta_vigente)
    
    def test_es_permanente_property(self):
        """Test de la propiedad es_permanente."""
        self.assertTrue(self.asignacion.es_permanente)
        
        asignacion_temporal = AsignacionConsultorio.objects.create(
            consultorio=self.consultorio,
            terapeuta=self.terapeuta,
            tipo_asignacion=AsignacionConsultorio.TipoAsignacion.TEMPORAL,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=30)
        )
        self.assertFalse(asignacion_temporal.es_permanente)
    
    def test_clean_valida_terapeuta(self):
        """Test que valida que solo terapeutas se asignen."""
        from django.core.exceptions import ValidationError
        
        admin = Usuario.objects.create_user(
            username='admin_test',
            password='Test123!',
            rol=Usuario.Rol.ADMIN
        )
        
        asignacion_invalida = AsignacionConsultorio(
            consultorio=self.consultorio,
            terapeuta=admin,
            fecha_inicio=date.today()
        )
        
        with self.assertRaises(ValidationError):
            asignacion_invalida.clean()
    
    def test_agregar_dia(self):
        """Test del método agregar_dia."""
        self.asignacion.agregar_dia('Lunes', '09:00', '12:00')
        
        self.assertIn('Lunes', self.asignacion.dias_semana)
        self.assertEqual(self.asignacion.horario['Lunes']['hora_inicio'], '09:00')


class DisponibilidadConsultorioModelTest(TestCase):
    """Tests para el modelo DisponibilidadConsultorio."""
    
    def setUp(self):
        """Configuración inicial."""
        self.consultorio = Consultorio.objects.create(
            nombre='Consultorio 401',
            codigo='C401',
            tipo=Consultorio.TipoConsultorio.INDIVIDUAL,
            piso=4,
            numero='401',
            capacidad=1
        )
        
        self.disponibilidad = DisponibilidadConsultorio.objects.create(
            consultorio=self.consultorio,
            fecha=date.today(),
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            estado=DisponibilidadConsultorio.EstadoDisponibilidad.DISPONIBLE
        )
    
    def test_crear_disponibilidad_valida(self):
        """Test de creación de disponibilidad válida."""
        self.assertTrue(isinstance(self.disponibilidad, DisponibilidadConsultorio))
        self.assertEqual(self.disponibilidad.consultorio, self.consultorio)
    
    def test_disponibilidad_str(self):
        """Test del método __str__."""
        self.assertIn(self.consultorio.nombre, str(self.disponibilidad))
        self.assertIn(str(self.disponibilidad.fecha), str(self.disponibilidad))
    
    def test_duracion_minutos_property(self):
        """Test de la propiedad duracion_minutos."""
        self.assertEqual(self.disponibilidad.duracion_minutos, 60)
    
    def test_esta_disponible_property(self):
        """Test de la propiedad esta_disponible."""
        self.assertTrue(self.disponibilidad.esta_disponible)
        
        self.disponibilidad.estado = DisponibilidadConsultorio.EstadoDisponibilidad.OCUPADO
        self.disponibilidad.save()
        self.assertFalse(self.disponibilidad.esta_disponible)
    
    def test_clean_valida_horario(self):
        """Test que valida que hora_fin sea mayor a hora_inicio."""
        from django.core.exceptions import ValidationError
        
        disponibilidad_invalida = DisponibilidadConsultorio(
            consultorio=self.consultorio,
            fecha=date.today(),
            hora_inicio=time(10, 0),
            hora_fin=time(9, 0)  # Hora_fin antes que hora_inicio
        )
        
        with self.assertRaises(ValidationError):
            disponibilidad_invalida.clean()


class ConsultorioIntegrationTest(TestCase):
    """Tests de integración para consultorios."""
    
    def setUp(self):
        """Configuración inicial."""
        self.consultorio = Consultorio.objects.create(
            nombre='Consultorio Integración',
            codigo='CINT',
            tipo=Consultorio.TipoConsultorio.GRUPAL,
            piso=1,
            numero='INT01',
            capacidad=8
        )
        
        self.terapeuta = Usuario.objects.create_user(
            username='terapeuta_int',
            password='Test123!',
            rol=Usuario.Rol.TERAPEUTA,
            first_name='Pedro',
            last_name='Martínez'
        )
    
    def test_flujo_completo_asignacion(self):
        """Test del flujo completo de asignación de consultorio."""
        # 1. Crear asignación
        asignacion = AsignacionConsultorio.objects.create(
            consultorio=self.consultorio,
            terapeuta=self.terapeuta,
            tipo_asignacion=AsignacionConsultorio.TipoAsignacion.PERMANENTE,
            fecha_inicio=date.today(),
            prioridad=5
        )
        
        # 2. Verificar que se creó correctamente
        self.assertTrue(asignacion.esta_vigente)
        self.assertTrue(asignacion.es_permanente)
        
        # 3. Agregar horarios
        asignacion.agregar_dia('Lunes', '09:00', '12:00')
        asignacion.agregar_dia('Miércoles', '14:00', '17:00')
        
        # 4. Verificar horarios
        self.assertEqual(len(asignacion.dias_semana), 2)
        self.assertIn('Lunes', asignacion.dias_semana)
        self.assertIn('Miércoles', asignacion.dias_semana)
        
        # 5. Verificar que el consultorio tiene la asignación
        self.assertEqual(self.consultorio.asignaciones.count(), 1)
    
    def test_consultorio_con_salas(self):
        """Test de consultorio con múltiples salas."""
        # Crear salas
        sala1 = Sala.objects.create(
            consultorio=self.consultorio,
            nombre='Área Principal',
            tipo=Sala.TipoSala.TERAPIA,
            area_metros=12.0
        )
        
        sala2 = Sala.objects.create(
            consultorio=self.consultorio,
            nombre='Área de Juego',
            tipo=Sala.TipoSala.JUEGO,
            area_metros=6.0
        )
        
        # Verificar que el consultorio tiene las salas
        self.assertEqual(self.consultorio.salas.count(), 2)
        self.assertIn(sala1, self.consultorio.salas.all())
        self.assertIn(sala2, self.consultorio.salas.all())
