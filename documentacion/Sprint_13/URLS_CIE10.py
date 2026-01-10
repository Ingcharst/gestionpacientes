# URLS CIE-10
# Archivo: apps/procedimientos/urls.py
# AGREGAR a urlpatterns

urlpatterns = [
    # ... URLs existentes ...
    
    # Búsqueda CIE-10
    path('api/cie10/buscar/', views.buscar_cie10, name='buscar_cie10'),
    path('api/cie10/<int:codigo_id>/', views.obtener_cie10, name='obtener_cie10'),
]
