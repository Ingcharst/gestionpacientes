"""
Vistas del frontend para usuarios.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Usuario, Perfil, RegistroAcceso
from .forms import (
    UsuarioLoginForm,
    UsuarioRegistroForm,
    UsuarioUpdateForm,
    PerfilUpdateForm
)


def login_view(request):
    """Vista de inicio de sesión."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Registrar acceso exitoso
            RegistroAcceso.objects.create(
                usuario=user,
                tipo_acceso=RegistroAcceso.TipoAcceso.LOGIN,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                exitoso=True
            )
            
            next_url = request.POST.get('next') or 'dashboard'
            messages.success(request, f'¡Bienvenido {user.get_full_name()}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'auth/login.html', {})


@login_required
def logout_view(request):
    """Vista de cierre de sesión."""
    # Registrar cierre de sesión
    RegistroAcceso.objects.create(
        usuario=request.user,
        tipo_acceso=RegistroAcceso.TipoAcceso.LOGOUT,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        exitoso=True
    )
    
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')


@login_required
def dashboard(request):
    """Dashboard principal del sistema."""
    from apps.procedimientos.models import Paciente, SesionTerapeutica
    from apps.consultorios.models import Consultorio
    from apps.terapias.models import Terapia
    from apps.grupos.models import GrupoTerapeutico, AsignacionGrupo, PacientePendiente
    from datetime import date
    
    # Estadísticas de grupos
    grupos_activos = GrupoTerapeutico.objects.filter(activo=True).count()
    pacientes_asignados = AsignacionGrupo.objects.filter(estado='ACTIVA').count()
    pacientes_pendientes = PacientePendiente.objects.filter(estado='PENDIENTE').count()
    
    # Calcular cupos disponibles
    cupos_disponibles = 0
    for grupo in GrupoTerapeutico.objects.filter(activo=True):
        cupos_disponibles += grupo.cupos_disponibles
    
    context = {
        'stats': {
            'pacientes_activos': Paciente.objects.filter(estado='ACTIVO').count(),
            'sesiones_hoy': SesionTerapeutica.objects.filter(fecha=date.today()).count(),
            'consultorios_disponibles': Consultorio.objects.filter(estado='DISPONIBLE').count(),
            'terapias_activas': Terapia.objects.filter(activo=True).count(),
            'grupos_activos': grupos_activos,
            'pacientes_en_grupos': pacientes_asignados,
            'cupos_disponibles': cupos_disponibles,
            'pacientes_pendientes': pacientes_pendientes,
        },
        'proximas_sesiones': SesionTerapeutica.objects.filter(
            fecha=date.today()
        ).select_related('paciente', 'terapia', 'terapeuta').order_by('hora_inicio')[:10],
        'alertas': []
    }
    return render(request, 'auth/dashboard.html', context)


@login_required
def usuario_list(request):
    """Lista de usuarios del sistema."""
    usuarios = Usuario.objects.select_related('perfil').all()
    
    # Filtros
    rol = request.GET.get('rol')
    estado = request.GET.get('estado')
    search = request.GET.get('search')
    
    if rol:
        usuarios = usuarios.filter(rol=rol)
    
    if estado:
        usuarios = usuarios.filter(estado=estado)
    
    if search:
        usuarios = usuarios.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    context = {
        'usuarios': usuarios,
        'roles': Usuario.Rol.choices,
        'estados': Usuario.EstadoUsuario.choices,
    }
    
    # Si es petición HTMX, solo renderizar la tabla
    if request.headers.get('HX-Request'):
        return render(request, 'usuarios/partials/usuario_table.html', context)
    
    return render(request, 'usuarios/usuario_list.html', context)


@login_required
def usuario_detail(request, pk):
    """Detalle de un usuario."""
    usuario = get_object_or_404(Usuario.objects.select_related('perfil'), pk=pk)
    
    context = {
        'usuario': usuario,
        'ultimos_accesos': RegistroAcceso.objects.filter(usuario=usuario)[:20],
    }
    
    return render(request, 'usuarios/usuario_detail.html', context)


@login_required
def usuario_create(request):
    """Crear nuevo usuario."""
    if not request.user.es_admin:
        messages.error(request, 'No tienes permiso para crear usuarios.')
        return redirect('usuario_list')
    
    if request.method == 'POST':
        form = UsuarioRegistroForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Usuario {usuario.username} creado exitosamente.')
            return redirect('usuario_detail', pk=usuario.pk)
    else:
        form = UsuarioRegistroForm()
    
    return render(request, 'usuarios/usuario_form.html', {'form': form, 'action': 'Crear'})


@login_required
def usuario_update(request, pk):
    """Actualizar usuario."""
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # Verificar permisos
    if not (request.user == usuario or request.user.es_admin):
        messages.error(request, 'No tienes permiso para editar este usuario.')
        return redirect('usuario_detail', pk=pk)
    
    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, 'Usuario actualizado exitosamente.')
            return redirect('usuario_detail', pk=usuario.pk)
    else:
        form = UsuarioUpdateForm(instance=usuario)
    
    return render(request, 'usuarios/usuario_form.html', {
        'form': form,
        'usuario': usuario,
        'action': 'Actualizar'
    })


@login_required
def perfil_update(request, pk):
    """Actualizar perfil profesional."""
    perfil = get_object_or_404(Perfil, pk=pk)
    
    # Verificar permisos
    if not (request.user == perfil.usuario or request.user.es_admin):
        messages.error(request, 'No tienes permiso para editar este perfil.')
        return redirect('usuario_detail', pk=perfil.usuario.pk)
    
    if request.method == 'POST':
        form = PerfilUpdateForm(request.POST, instance=perfil)
        if form.is_valid():
            perfil = form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('usuario_detail', pk=perfil.usuario.pk)
    else:
        form = PerfilUpdateForm(instance=perfil)
    
    return render(request, 'usuarios/perfil_form.html', {
        'form': form,
        'perfil': perfil
    })


@login_required
@require_http_methods(["POST"])
def usuario_toggle_estado(request, pk):
    """Activa o desactiva un usuario (HTMX)."""
    if not request.user.es_admin:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if usuario.estado == Usuario.EstadoUsuario.ACTIVO:
        usuario.estado = Usuario.EstadoUsuario.INACTIVO
        usuario.is_active = False
        mensaje = 'Usuario desactivado'
    else:
        usuario.estado = Usuario.EstadoUsuario.ACTIVO
        usuario.is_active = True
        mensaje = 'Usuario activado'
    
    usuario.save()
    
    if request.headers.get('HX-Request'):
        return render(request, 'usuarios/partials/usuario_estado_badge.html', {
            'usuario': usuario
        })
    
    return JsonResponse({'mensaje': mensaje})


# Funciones auxiliares

def get_client_ip(request):
    """Obtiene la IP del cliente."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip