"""
URLs del frontend para terapias.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Categorías
    path('categorias/', views.categoria_list, name='categoria_list'),
    path('categorias/crear/', views.categoria_create, name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.categoria_update, name='categoria_update'),
    
    # Terapias
    path('', views.terapia_list, name='terapia_list'),
    path('crear/', views.terapia_create, name='terapia_create'),
    path('<int:pk>/', views.terapia_detail, name='terapia_detail'),
    path('<int:pk>/editar/', views.terapia_update, name='terapia_update'),
    
    # Catálogo y vistas públicas
    path('catalogo/', views.catalogo_terapias, name='catalogo_terapias'),
    path('especialidad/<str:especialidad>/', views.terapias_por_especialidad, name='terapias_especialidad'),
]
