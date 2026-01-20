"""
Configuración del panel de administración para usuarios.
"""
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Usuario, Perfil, RegistroAcceso

class PerfilAdminForm(forms.ModelForm):
    # Campo amigable para especialidades (Checkbox en lugar de JSON manual)
    especialidades_secundarias = forms.MultipleChoiceField(
        choices=Perfil.Especialidad.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Perfil
        fields = '__all__'


class PerfilInline(admin.StackedInline):
    """Inline para mostrar perfil dentro de usuario."""
    model = Perfil
    form = PerfilAdminForm
    can_delete = False
    verbose_name_plural = 'Perfil Profesional'
    extra = 0
    fields = (
        'especialidades', 'especialidades_secundarias', 'universidad',
        'anios_experiencia', 'certificaciones', 'bio', 'disponible'
    )


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Administración personalizada de usuarios."""
    
    inlines = [PerfilInline]
    
    list_display = (
        'username', 'email', 'tipo_identificacion',
        'numero_identificacion', 'get_full_name', 'rol',
        'estado', 'foto_perfil_thumbnail', 'is_active', 'date_joined'
    )
    
    list_filter = (
        'rol', 'tipo_identificacion', 'estado', 'is_active', 'is_staff',
        'date_joined', 'fecha_contratacion'
    )
    
    search_fields = (
        'username', 'first_name', 'last_name', 'numero_identificacion',
        'email', 'cedula_profesional'
    )
    
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('Información de Acceso', {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': (
                'first_name', 'last_name', 'tipo_identificacion',
                'numero_identificacion', 'email',
                'telefono', 'foto_perfil'
            )
        }),
        ('Información Profesional', {
            'fields': (
                'rol', 'cedula_profesional',
                'fecha_contratacion', 'estado', 'notas'
            )
        }),
        ('Firma Digital', {
            'fields': ('firma',),
            'description': 'Cargar imagen de la firma del usuario'
        }),
        ('Permisos', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Información de Acceso', {
            'fields': ('username', 'password1', 'password2')
        }),
        ('Información Personal', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'tipo_identificacion',
                'numero_identificacion',
            )
        }),
        ('Firma Digital', {
            'fields': ('firma',),
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff'),
        }),
        ('Información Adicional', {
            'classes': ('wide',),
            'fields': ('rol', 'telefono', 'cedula_profesional'),
        }),
    )
    
    def foto_perfil_thumbnail(self, obj):
        """Muestra miniatura de foto de perfil."""
        if obj.foto_perfil:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.foto_perfil.url
            )
        return "Sin foto"
    
    foto_perfil_thumbnail.short_description = 'Foto'
    
    def get_queryset(self, request):
        """Optimiza consultas con select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('perfil')


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    """Administración de perfiles profesionales."""
    
    list_display = (
        'usuario', 'especialidades', 'anios_experiencia',
        'disponible', 'fecha_actualizacion'
    )
    
    list_filter = (
        'especialidades', 'disponible',
        'anios_experiencia'
    )
    
    search_fields = (
        'usuario__username', 'usuario__first_name',
        'usuario__last_name', 'universidad'
    )
    
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Información Profesional', {
            'fields': (
                'especialidades', 'especialidades_secundarias',
                'universidad', 'anios_experiencia', 'certificaciones'
            )
        }),
        ('Descripción', {
            'fields': ('bio',)
        }),
        ('Disponibilidad', {
            'fields': ('disponible', 'horario_atencion')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

@admin.register(RegistroAcceso)
class RegistroAccesoAdmin(admin.ModelAdmin):
    """Administración de registros de acceso."""
    
    list_display = (
        'usuario', 'tipo_acceso', 'ip_address',
        'exitoso', 'fecha_hora'
    )
    
    list_filter = (
        'tipo_acceso', 'exitoso', 'fecha_hora'
    )
    
    search_fields = (
        'usuario__username', 'ip_address'
    )
    
    readonly_fields = (
        'usuario', 'tipo_acceso', 'ip_address',
        'user_agent', 'fecha_hora', 'exitoso', 'notas'
    )
    
    date_hierarchy = 'fecha_hora'
    
    def has_add_permission(self, request):
        """Los registros de acceso no se crean manualmente."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Los registros de acceso no se modifican."""
        return False


