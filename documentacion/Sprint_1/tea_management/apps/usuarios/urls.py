"""
URLs del frontend para usuarios.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Gestión de usuarios
    path('usuarios/', views.usuario_list, name='usuario_list'),
    path('usuarios/crear/', views.usuario_create, name='usuario_create'),
    path('usuarios/<int:pk>/', views.usuario_detail, name='usuario_detail'),
    path('usuarios/<int:pk>/editar/', views.usuario_update, name='usuario_update'),
    path('usuarios/<int:pk>/toggle-estado/', views.usuario_toggle_estado, name='usuario_toggle_estado'),
    
    # Perfil
    path('perfil/<int:pk>/editar/', views.perfil_update, name='perfil_update'),
]
