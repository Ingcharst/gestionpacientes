"""
Tests para el módulo de terapias.
"""
from django.test import TestCase
from decimal import Decimal
from apps.terapias.models import CategoriaTerapia, Terapia


class CategoriaTerapiaModelTest(TestCase):
    """Tests para el modelo CategoriaTerapia."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.categoria = CategoriaTerapia.objects.create(
            nombre='Terapia del Lenguaje',
            codigo='TL',
            descripcion='Terapias enfocadas en comunicación y lenguaje',
            color='#007bff',
            orden=1
        )
    
    def test_crear_categoria_valida(self):
        """Test de creación de categoría válida."""
        self.assertTrue(isinstance(self.categoria, CategoriaTerapia))
        self.assertEqual(self.categoria.codigo, 'TL')
    
    def test_categoria_str(self):
        """Test del método __str__."""
        self.assertEqual(str(self.categoria), 'Terapia del Lenguaje')
    
    def test_numero_terapias_property(self):
        """Test de la propiedad numero_terapias."""
        # Sin terapias
        self.assertEqual(self.categoria.numero_terapias, 0)
        
        # Crear terapia
        Terapia.objects.create(
            nombre='Terapia de Articulación',
            codigo='TA-001',
            categoria=self.categoria,
            descripcion='Terapia para mejorar articulación',
            especialidad='LENGUAJE',
            duracion_minutos=60,
            costo_sesion=Decimal('100.00')
        )
        
        # Con 1 terapia
        self.assertEqual(self.categoria.numero_terapias, 1)
    
    def test_tiene_terapias_property(self):
        """Test de la propiedad tiene_terapias."""
        self.assertFalse(self.categoria.tiene_terapias)
        
        Terapia.objects.create(
            nombre='Terapia Test',
            codigo='TT-001',
            categoria=self.categoria,
            descripcion='Test',
            especialidad='LENGUAJE',
            duracion_minutos=60,
            costo_sesion=Decimal('100.00')
        )
        
        self.assertTrue(self.categoria.tiene_terapias)


class TerapiaModelTest(TestCase):
    """Tests para el modelo Terapia."""
    
    def setUp(self):
        """Configuración inicial."""
        self.categoria = CategoriaTerapia.objects.create(
            nombre='Terapia Ocupacional',
            codigo='TO',
            descripcion='Terapias ocupacionales',
            orden=1
        )
        
        self.terapia = Terapia.objects.create(
            nombre='Integración Sensorial',
            codigo='IS-001',
            categoria=self.categoria,
            descripcion='Terapia de integración sensorial',
            descripcion_corta='Integración sensorial para niños TEA',
            modalidad=Terapia.Modalidad.INDIVIDUAL,
            especialidad=Terapia.Especialidad.INTEGRACION_SENSORIAL,
            duracion_minutos=60,
            frecuencia_semanal_recomendada=2,
            costo_sesion=Decimal('150.00'),
            edad_minima=3,
            edad_maxima=12,
            capacidad_minima=1,
            capacidad_maxima=1
        )
    
    def test_crear_terapia_valida(self):
        """Test de creación de terapia válida."""
        self.assertTrue(isinstance(self.terapia, Terapia))
        self.assertEqual(self.terapia.codigo, 'IS-001')
        self.assertEqual(self.terapia.categoria, self.categoria)
    
    def test_terapia_str(self):
        """Test del método __str__."""
        expected = f"{self.terapia.codigo} - {self.terapia.nombre}"
        self.assertEqual(str(self.terapia), expected)
    
    def test_nombre_completo_property(self):
        """Test de la propiedad nombre_completo."""
        expected = f"{self.categoria.nombre} - {self.terapia.nombre}"
        self.assertEqual(self.terapia.nombre_completo, expected)
    
    def test_duracion_formateada_property(self):
        """Test de la propiedad duracion_formateada."""
        # 60 minutos = 1 hora
        self.assertEqual(self.terapia.duracion_formateada, '1h')
        
        # 90 minutos = 1h 30min
        self.terapia.duracion_minutos = 90
        self.terapia.save()
        self.assertEqual(self.terapia.duracion_formateada, '1h 30min')
        
        # 45 minutos = 45min
        self.terapia.duracion_minutos = 45
        self.terapia.save()
        self.assertEqual(self.terapia.duracion_formateada, '45min')
    
    def test_costo_formateado_property(self):
        """Test de la propiedad costo_formateado."""
        self.assertEqual(self.terapia.costo_formateado, '$150.00')
    
    def test_rango_edad_property(self):
        """Test de la propiedad rango_edad."""
        # Con edad mínima y máxima
        self.assertEqual(self.terapia.rango_edad, '3-12 años')
        
        # Solo edad mínima
        self.terapia.edad_maxima = None
        self.terapia.save()
        self.assertEqual(self.terapia.rango_edad, 'Desde 3 años')
        
        # Solo edad máxima
        self.terapia.edad_minima = None
        self.terapia.edad_maxima = 12
        self.terapia.save()
        self.assertEqual(self.terapia.rango_edad, 'Hasta 12 años')
        
        # Sin edades
        self.terapia.edad_minima = None
        self.terapia.edad_maxima = None
        self.terapia.save()
        self.assertEqual(self.terapia.rango_edad, 'Todas las edades')
    
    def test_es_grupal_property(self):
        """Test de la propiedad es_grupal."""
        self.assertFalse(self.terapia.es_grupal)
        
        self.terapia.modalidad = Terapia.Modalidad.GRUPAL
        self.terapia.save()
        self.assertTrue(self.terapia.es_grupal)
    
    def test_calcular_costo_mensual(self):
        """Test del método calcular_costo_mensual."""
        # Con frecuencia recomendada (2 sesiones/semana * 4 semanas = 8)
        costo_mensual = self.terapia.calcular_costo_mensual()
        esperado = self.terapia.costo_sesion * 8
        self.assertEqual(costo_mensual, esperado)
        
        # Con sesiones específicas
        costo_mensual = self.terapia.calcular_costo_mensual(sesiones_por_mes=12)
        esperado = self.terapia.costo_sesion * 12
        self.assertEqual(costo_mensual, esperado)
        
        # Con paquete mensual
        self.terapia.costo_paquete_mensual = Decimal('1000.00')
        self.terapia.save()
        costo_mensual = self.terapia.calcular_costo_mensual()
        self.assertEqual(costo_mensual, Decimal('1000.00'))
    
    def test_es_apto_para_edad(self):
        """Test del método es_apto_para_edad."""
        # Dentro del rango (3-12)
        self.assertTrue(self.terapia.es_apto_para_edad(5))
        self.assertTrue(self.terapia.es_apto_para_edad(3))
        self.assertTrue(self.terapia.es_apto_para_edad(12))
        
        # Fuera del rango
        self.assertFalse(self.terapia.es_apto_para_edad(2))
        self.assertFalse(self.terapia.es_apto_para_edad(13))
    
    def test_clean_validacion_duraciones(self):
        """Test de validación de duraciones."""
        from django.core.exceptions import ValidationError
        
        # Duración mínima > duración máxima
        terapia_invalida = Terapia(
            nombre='Test',
            codigo='T-001',
            categoria=self.categoria,
            descripcion='Test',
            especialidad='LENGUAJE',
            duracion_minutos=60,
            duracion_minima_minutos=90,
            duracion_maxima_minutos=45,
            costo_sesion=Decimal('100.00')
        )
        
        with self.assertRaises(ValidationError):
            terapia_invalida.clean()
    
    def test_clean_validacion_edades(self):
        """Test de validación de edades."""
        from django.core.exceptions import ValidationError
        
        # Edad mínima > edad máxima
        terapia_invalida = Terapia(
            nombre='Test',
            codigo='T-002',
            categoria=self.categoria,
            descripcion='Test',
            especialidad='LENGUAJE',
            duracion_minutos=60,
            costo_sesion=Decimal('100.00'),
            edad_minima=10,
            edad_maxima=5
        )
        
        with self.assertRaises(ValidationError):
            terapia_invalida.clean()
    
    def test_clean_validacion_costos(self):
        """Test de validación de costos."""
        from django.core.exceptions import ValidationError
        
        # Costo mínimo > costo sesión
        terapia_invalida = Terapia(
            nombre='Test',
            codigo='T-003',
            categoria=self.categoria,
            descripcion='Test',
            especialidad='LENGUAJE',
            duracion_minutos=60,
            costo_sesion=Decimal('100.00'),
            costo_minimo=Decimal('150.00')
        )
        
        with self.assertRaises(ValidationError):
            terapia_invalida.clean()
    
    def test_clean_validacion_capacidad(self):
        """Test de validación de capacidad."""
        from django.core.exceptions import ValidationError
        
        # Capacidad mínima > capacidad máxima
        terapia_invalida = Terapia(
            nombre='Test',
            codigo='T-004',
            categoria=self.categoria,
            descripcion='Test',
            especialidad='LENGUAJE',
            duracion_minutos=60,
            costo_sesion=Decimal('100.00'),
            capacidad_minima=5,
            capacidad_maxima=2
        )
        
        with self.assertRaises(ValidationError):
            terapia_invalida.clean()


class TerapiaIntegrationTest(TestCase):
    """Tests de integración para terapias."""
    
    def setUp(self):
        """Configuración inicial."""
        self.categoria = CategoriaTerapia.objects.create(
            nombre='Terapia Conductual',
            codigo='TC',
            descripcion='Terapias conductuales',
            orden=1
        )
    
    def test_flujo_completo_terapia(self):
        """Test del flujo completo de creación y uso de terapia."""
        # 1. Crear terapia
        terapia = Terapia.objects.create(
            nombre='Análisis Conductual Aplicado (ABA)',
            codigo='ABA-001',
            categoria=self.categoria,
            descripcion='Terapia ABA para niños con TEA',
            descripcion_corta='ABA',
            modalidad=Terapia.Modalidad.INDIVIDUAL,
            especialidad=Terapia.Especialidad.CONDUCTUAL,
            duracion_minutos=120,
            frecuencia_semanal_recomendada=5,
            costo_sesion=Decimal('200.00'),
            edad_minima=2,
            edad_maxima=18
        )
        
        # 2. Verificar propiedades
        self.assertEqual(terapia.duracion_formateada, '2h')
        self.assertEqual(terapia.rango_edad, '2-18 años')
        
        # 3. Verificar aptitud para edad
        self.assertTrue(terapia.es_apto_para_edad(5))
        self.assertFalse(terapia.es_apto_para_edad(20))
        
        # 4. Calcular costo mensual (5 sesiones/semana * 4 semanas = 20)
        costo_mensual = terapia.calcular_costo_mensual()
        esperado = Decimal('200.00') * 20
        self.assertEqual(costo_mensual, esperado)
        
        # 5. Verificar que aparece en la categoría
        self.assertTrue(self.categoria.tiene_terapias)
        self.assertEqual(self.categoria.numero_terapias, 1)
