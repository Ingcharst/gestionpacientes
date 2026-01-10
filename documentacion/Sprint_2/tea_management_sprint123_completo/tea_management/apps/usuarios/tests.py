"""
Tests para el módulo de usuarios.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.usuarios.models import Usuario, Perfil, RegistroAcceso

User = get_user_model()


class UsuarioModelTest(TestCase):
    """Tests para el modelo Usuario."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User',
            rol=Usuario.Rol.TERAPEUTA
        )
    
    def test_crear_usuario_valido(self):
        """Test de creación de usuario válido."""
        self.assertTrue(isinstance(self.usuario, Usuario))
        self.assertEqual(self.usuario.rol, Usuario.Rol.TERAPEUTA)
        self.assertEqual(self.usuario.username, 'testuser')
    
    def test_usuario_str(self):
        """Test del método __str__."""
        expected = f"{self.usuario.get_full_name()} ({self.usuario.get_rol_display()})"
        self.assertEqual(str(self.usuario), expected)
    
    def test_get_full_name(self):
        """Test del método get_full_name."""
        self.assertEqual(self.usuario.get_full_name(), 'Test User')
    
    def test_es_terapeuta_property(self):
        """Test de la propiedad es_terapeuta."""
        self.assertTrue(self.usuario.es_terapeuta)
        
        admin = Usuario.objects.create_user(
            username='admin',
            rol=Usuario.Rol.ADMIN,
            password='AdminPass123!'
        )
        self.assertFalse(admin.es_terapeuta)
    
    def test_es_admin_property(self):
        """Test de la propiedad es_admin."""
        self.assertFalse(self.usuario.es_admin)
        
        admin = Usuario.objects.create_user(
            username='admin',
            rol=Usuario.Rol.ADMIN,
            password='AdminPass123!'
        )
        self.assertTrue(admin.es_admin)
    
    def test_puede_gestionar_terapias_property(self):
        """Test de la propiedad puede_gestionar_terapias."""
        self.assertFalse(self.usuario.puede_gestionar_terapias)
        
        coordinador = Usuario.objects.create_user(
            username='coordinador',
            rol=Usuario.Rol.COORDINADOR,
            password='CoordPass123!'
        )
        self.assertTrue(coordinador.puede_gestionar_terapias)
    
    def test_creacion_perfil_automatico(self):
        """Test que el perfil se crea automáticamente con el usuario."""
        self.assertTrue(hasattr(self.usuario, 'perfil'))
        self.assertIsInstance(self.usuario.perfil, Perfil)


class PerfilModelTest(TestCase):
    """Tests para el modelo Perfil."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            password='TestPass123!',
            rol=Usuario.Rol.TERAPEUTA
        )
        self.perfil = self.usuario.perfil
    
    def test_perfil_str(self):
        """Test del método __str__ del perfil."""
        expected = f"Perfil de {self.usuario.get_full_name()}"
        self.assertEqual(str(self.perfil), expected)
    
    def test_agregar_especialidad(self):
        """Test del método agregar_especialidad."""
        self.perfil.agregar_especialidad('Python')
        self.assertIn('Python', self.perfil.especialidades_secundarias)
    
    def test_agregar_certificacion(self):
        """Test del método agregar_certificacion."""
        self.perfil.agregar_certificacion(
            nombre='Certificación TEA',
            institucion='Universidad Test',
            fecha='2024-01-01'
        )
        self.assertEqual(len(self.perfil.certificaciones), 1)
        self.assertEqual(self.perfil.certificaciones[0]['nombre'], 'Certificación TEA')


class RegistroAccesoModelTest(TestCase):
    """Tests para el modelo RegistroAcceso."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
    
    def test_crear_registro_acceso(self):
        """Test de creación de registro de acceso."""
        registro = RegistroAcceso.objects.create(
            usuario=self.usuario,
            tipo_acceso=RegistroAcceso.TipoAcceso.LOGIN,
            ip_address='127.0.0.1',
            exitoso=True
        )
        
        self.assertIsInstance(registro, RegistroAcceso)
        self.assertEqual(registro.usuario, self.usuario)
        self.assertTrue(registro.exitoso)
    
    def test_registro_str(self):
        """Test del método __str__ del registro."""
        registro = RegistroAcceso.objects.create(
            usuario=self.usuario,
            tipo_acceso=RegistroAcceso.TipoAcceso.LOGIN,
            ip_address='127.0.0.1'
        )
        
        self.assertIn(self.usuario.username, str(registro))


class UsuarioViewsTest(TestCase):
    """Tests para las vistas de usuarios."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123!',
            rol=Usuario.Rol.TERAPEUTA
        )
        self.admin = Usuario.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='AdminPass123!',
            rol=Usuario.Rol.ADMIN,
            is_staff=True
        )
    
    def test_login_view_get(self):
        """Test de vista de login (GET)."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/login.html')
    
    def test_login_view_post_valid(self):
        """Test de login con credenciales válidas."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(response.url.startswith('/'))
    
    def test_login_view_post_invalid(self):
        """Test de login con credenciales inválidas."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
    
    def test_dashboard_requires_login(self):
        """Test que el dashboard requiere autenticación."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect a login
    
    def test_dashboard_authenticated(self):
        """Test del dashboard con usuario autenticado."""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/dashboard.html')
    
    def test_usuario_list_requires_login(self):
        """Test que la lista de usuarios requiere autenticación."""
        response = self.client.get(reverse('usuario_list'))
        self.assertEqual(response.status_code, 302)
    
    def test_usuario_list_authenticated(self):
        """Test de lista de usuarios con usuario autenticado."""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('usuario_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/usuario_list.html')
    
    def test_usuario_detail_requires_login(self):
        """Test que el detalle de usuario requiere autenticación."""
        response = self.client.get(
            reverse('usuario_detail', kwargs={'pk': self.usuario.pk})
        )
        self.assertEqual(response.status_code, 302)
    
    def test_usuario_create_requires_admin(self):
        """Test que crear usuario requiere ser administrador."""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('usuario_create'))
        self.assertEqual(response.status_code, 302)  # Redirect por no ser admin


class UsuarioAPITest(TestCase):
    """Tests para la API de usuarios."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User',
            rol=Usuario.Rol.TERAPEUTA
        )
        self.admin = Usuario.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='AdminPass123!',
            rol=Usuario.Rol.ADMIN
        )
    
    def test_api_requires_authentication(self):
        """Test que la API requiere autenticación."""
        response = self.client.get('/api/usuarios/')
        self.assertEqual(response.status_code, 401)  # Unauthorized
    
    def test_token_obtain(self):
        """Test de obtención de token JWT."""
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())


class UsuarioIntegrationTest(TestCase):
    """Tests de integración para el módulo de usuarios."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.client = Client()
        self.admin = Usuario.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='AdminPass123!',
            rol=Usuario.Rol.ADMIN,
            is_staff=True
        )
    
    def test_flujo_completo_creacion_usuario(self):
        """Test del flujo completo de creación de usuario."""
        # 1. Login como admin
        self.client.login(username='admin', password='AdminPass123!')
        
        # 2. Acceder al formulario de creación
        response = self.client.get(reverse('usuario_create'))
        self.assertEqual(response.status_code, 200)
        
        # 3. Crear usuario
        response = self.client.post(reverse('usuario_create'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'NewPass123!',
            'password2': 'NewPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'rol': Usuario.Rol.TERAPEUTA,
            'telefono': '+5212345678901',
        })
        
        # 4. Verificar que se creó el usuario
        self.assertTrue(Usuario.objects.filter(username='newuser').exists())
        nuevo_usuario = Usuario.objects.get(username='newuser')
        
        # 5. Verificar que se creó el perfil automáticamente
        self.assertTrue(hasattr(nuevo_usuario, 'perfil'))
