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


# ============================================
# AGREGAR A: config/settings.py
# ============================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # AGREGAR ESTA LÍNEA:
                'apps.alertas.context_processors.alertas_pendientes',
            ],
        },
    },
]
