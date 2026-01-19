from django.urls import path
from . import views

app_name = 'alertas'

urlpatterns = [
    path('', views.dashboard_alertas, name='dashboard_alertas'),
    path('<int:alerta_id>/atender/', views.atender_alerta, name='atender_alerta'),
    path('configuracion/', views.configuracion_alertas, name='configuracion_alertas'),
    path('verificar/', views.forzar_verificacion, name='forzar_verificacion'),
]


