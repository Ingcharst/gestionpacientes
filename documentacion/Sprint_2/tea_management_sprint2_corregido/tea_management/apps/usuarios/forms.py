"""
Formularios para el módulo de usuarios.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Div, HTML
from .models import Usuario, Perfil


class UsuarioLoginForm(AuthenticationForm):
    """Formulario de inicio de sesión."""
    
    username = forms.CharField(
        label='Usuario o Email',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su usuario o email',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña'
        })
    )
    
    remember_me = forms.BooleanField(
        label='Recordarme',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class UsuarioRegistroForm(UserCreationForm):
    """Formulario de registro de usuarios."""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password1', 'password2',
            'first_name', 'last_name', 'rol', 'telefono',
            'cedula_profesional', 'fecha_contratacion', 'foto_perfil'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+52 123 456 7890'
            }),
            'cedula_profesional': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_contratacion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='col-md-6'),
                Column('email', css_class='col-md-6'),
            ),
            Row(
                Column('password1', css_class='col-md-6'),
                Column('password2', css_class='col-md-6'),
            ),
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
            ),
            Row(
                Column('rol', css_class='col-md-4'),
                Column('telefono', css_class='col-md-4'),
                Column('cedula_profesional', css_class='col-md-4'),
            ),
            Row(
                Column('fecha_contratacion', css_class='col-md-6'),
                Column('foto_perfil', css_class='col-md-6'),
            ),
            Div(
                Submit('submit', 'Crear Usuario', css_class='btn btn-primary'),
                HTML('<a href="{% url "usuario_list" %}" class="btn btn-secondary ms-2">Cancelar</a>'),
                css_class='mt-3'
            )
        )


class UsuarioUpdateForm(forms.ModelForm):
    """Formulario para actualizar usuarios."""
    
    class Meta:
        model = Usuario
        fields = [
            'first_name', 'last_name', 'email', 'rol',
            'telefono', 'cedula_profesional', 'estado',
            'fecha_contratacion', 'foto_perfil', 'notas'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+52 123 456 7890'
            }),
            'cedula_profesional': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'fecha_contratacion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
            ),
            Row(
                Column('email', css_class='col-md-6'),
                Column('rol', css_class='col-md-6'),
            ),
            Row(
                Column('telefono', css_class='col-md-4'),
                Column('cedula_profesional', css_class='col-md-4'),
                Column('estado', css_class='col-md-4'),
            ),
            Row(
                Column('fecha_contratacion', css_class='col-md-6'),
                Column('foto_perfil', css_class='col-md-6'),
            ),
            'notas',
            Div(
                Submit('submit', 'Actualizar', css_class='btn btn-primary'),
                HTML('<a href="{% url "usuario_detail" object.pk %}" class="btn btn-secondary ms-2">Cancelar</a>'),
                css_class='mt-3'
            )
        )


class PerfilUpdateForm(forms.ModelForm):
    """Formulario para actualizar perfil profesional."""
    
    class Meta:
        model = Perfil
        fields = [
            'especialidades', 'especialidades_secundarias',
            'universidad', 'anios_experiencia', 'certificaciones',
            'bio', 'horario_atencion', 'disponible'
        ]
        widgets = {
            'especialidades': forms.Select(attrs={'class': 'form-select'}),
            'especialidades_secundarias': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
            'universidad': forms.TextInput(attrs={'class': 'form-control'}),
            'anios_experiencia': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '60'
            }),
            'certificaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'JSON: [{"nombre": "...", "institucion": "...", "fecha": "..."}]'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5
            }),
            'horario_atencion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'JSON: {"lunes": "9:00-17:00", ...}'
            }),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            Row(
                Column('especialidades', css_class='col-md-6'),
                Column('universidad', css_class='col-md-6'),
            ),
            Row(
                Column('anios_experiencia', css_class='col-md-6'),
                Column('disponible', css_class='col-md-6 d-flex align-items-center'),
            ),
            'especialidades_secundarias',
            'certificaciones',
            'bio',
            'horario_atencion',
            Div(
                Submit('submit', 'Actualizar Perfil', css_class='btn btn-primary'),
                HTML('<a href="{% url "usuario_detail" object.usuario.pk %}" class="btn btn-secondary ms-2">Cancelar</a>'),
                css_class='mt-3'
            )
        )


class CambiarPasswordForm(forms.Form):
    """Formulario para cambiar contraseña."""
    
    old_password = forms.CharField(
        label='Contraseña Actual',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    new_password1 = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    new_password2 = forms.CharField(
        label='Confirmar Nueva Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            'old_password',
            'new_password1',
            'new_password2',
            Div(
                Submit('submit', 'Cambiar Contraseña', css_class='btn btn-primary'),
                css_class='mt-3'
            )
        )
    
    def clean_old_password(self):
        """Valida la contraseña actual."""
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('La contraseña actual es incorrecta.')
        return old_password
    
    def clean(self):
        """Valida que las contraseñas nuevas coincidan."""
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError('Las contraseñas nuevas no coinciden.')
        
        return cleaned_data
    
    def save(self):
        """Guarda la nueva contraseña."""
        password = self.cleaned_data.get('new_password1')
        self.user.set_password(password)
        self.user.save()
        return self.user
