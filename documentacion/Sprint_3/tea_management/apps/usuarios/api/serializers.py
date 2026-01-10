"""
Serializadores para la API de usuarios.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apps.usuarios.models import Usuario, Perfil, RegistroAcceso


class PerfilSerializer(serializers.ModelSerializer):
    """Serializador para el perfil profesional."""
    
    class Meta:
        model = Perfil
        fields = [
            'id', 'especialidades', 'especialidades_secundarias',
            'universidad', 'anios_experiencia', 'certificaciones',
            'bio', 'horario_atencion', 'disponible',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']


class UsuarioListSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listados de usuarios."""
    
    nombre_completo = serializers.CharField(source='get_full_name', read_only=True)
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'nombre_completo',
            'first_name', 'last_name', 'rol', 'rol_display',
            'estado', 'estado_display', 'telefono',
            'foto_perfil', 'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']


class UsuarioDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado para usuarios."""
    
    perfil = PerfilSerializer(read_only=True)
    nombre_completo = serializers.CharField(source='get_full_name', read_only=True)
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    es_terapeuta = serializers.BooleanField(read_only=True)
    es_admin = serializers.BooleanField(read_only=True)
    puede_gestionar_terapias = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'nombre_completo',
            'first_name', 'last_name', 'rol', 'rol_display',
            'estado', 'estado_display', 'telefono', 'cedula_profesional',
            'foto_perfil', 'fecha_contratacion', 'notas',
            'is_active', 'is_staff', 'date_joined', 'last_login',
            'fecha_actualizacion', 'perfil', 'es_terapeuta',
            'es_admin', 'puede_gestionar_terapias'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'fecha_actualizacion',
            'es_terapeuta', 'es_admin', 'puede_gestionar_terapias'
        ]


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializador para creación de usuarios."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'rol', 'telefono',
            'cedula_profesional', 'fecha_contratacion', 'notas'
        ]
    
    def validate(self, attrs):
        """Valida que las contraseñas coincidan."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Las contraseñas no coinciden."
            })
        return attrs
    
    def validate_email(self, value):
        """Valida que el email sea único."""
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value
    
    def create(self, validated_data):
        """Crea un nuevo usuario con contraseña encriptada."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        usuario = Usuario.objects.create(**validated_data)
        usuario.set_password(password)
        usuario.save()
        
        return usuario


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    """Serializador para actualización de usuarios."""
    
    class Meta:
        model = Usuario
        fields = [
            'email', 'first_name', 'last_name', 'rol',
            'telefono', 'cedula_profesional', 'estado',
            'foto_perfil', 'fecha_contratacion', 'notas',
            'is_active'
        ]
    
    def validate_email(self, value):
        """Valida que el email sea único (excepto para el usuario actual)."""
        usuario = self.instance
        if Usuario.objects.exclude(pk=usuario.pk).filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value


class CambiarPasswordSerializer(serializers.Serializer):
    """Serializador para cambio de contraseña."""
    
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """Valida que la contraseña actual sea correcta."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta.")
        return value
    
    def validate(self, attrs):
        """Valida que las nuevas contraseñas coincidan."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "Las contraseñas nuevas no coinciden."
            })
        return attrs
    
    def save(self, **kwargs):
        """Actualiza la contraseña del usuario."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class RegistroAccesoSerializer(serializers.ModelSerializer):
    """Serializador para registros de acceso."""
    
    usuario_nombre = serializers.CharField(
        source='usuario.get_full_name',
        read_only=True
    )
    tipo_acceso_display = serializers.CharField(
        source='get_tipo_acceso_display',
        read_only=True
    )
    
    class Meta:
        model = RegistroAcceso
        fields = [
            'id', 'usuario', 'usuario_nombre', 'tipo_acceso',
            'tipo_acceso_display', 'ip_address', 'user_agent',
            'fecha_hora', 'exitoso', 'notas'
        ]
        read_only_fields = ['id', 'fecha_hora']


class PerfilUpdateSerializer(serializers.ModelSerializer):
    """Serializador para actualización de perfil."""
    
    class Meta:
        model = Perfil
        fields = [
            'especialidades', 'especialidades_secundarias',
            'universidad', 'anios_experiencia', 'certificaciones',
            'bio', 'horario_atencion', 'disponible'
        ]
    
    def validate_anios_experiencia(self, value):
        """Valida que los años de experiencia sean razonables."""
        if value < 0:
            raise serializers.ValidationError("Los años de experiencia no pueden ser negativos.")
        if value > 60:
            raise serializers.ValidationError("Los años de experiencia parecen incorrectos.")
        return value
