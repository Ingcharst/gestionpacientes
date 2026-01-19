# CREAR: apps/alertas/context_processors.py

def alertas_pendientes(request):
    """
    Context processor para mostrar contador de alertas en navbar
    """
    if request.user.is_authenticated:
        from apps.alertas.models import AlertaInasistencia
        
        count = AlertaInasistencia.objects.filter(
            estado__in=['PENDIENTE', 'NOTIFICADA']
        ).count()
        
        return {'alertas_pendientes': count}
    
    return {'alertas_pendientes': 0}

