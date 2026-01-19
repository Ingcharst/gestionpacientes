# ✅ CÓDIGO PARA AGREGAR A views.py

## API Búsqueda CIE-10

# Agregar estos imports al inicio del archivo:
from django.http import JsonResponse
from django.db.models import Q


# Agregar esta función al final del archivo:

def api_buscar_cie10(request):
    """
    API para búsqueda de códigos CIE-10 en tiempo real
    
    GET /procedimientos/api/buscar-cie10/?q=<busqueda>
    
    Returns:
        JSON con lista de códigos que coinciden
    """
    query = request.GET.get('q', '').strip()
    
    # Mínimo 2 caracteres para buscar
    if len(query) < 2:
        return JsonResponse({
            'resultados': [],
            'mensaje': 'Escriba al menos 2 caracteres'
        })
    
    try:
        # Buscar por código o descripción
        codigos = CodigoCIE10.objects.filter(
            Q(codigo__icontains=query) | 
            Q(descripcion__icontains=query) |
            Q(nombre__icontains=query),
            activo=True
        ).order_by('codigo')[:20]  # Máximo 20 resultados
        
        # Formatear resultados
        resultados = []
        for c in codigos:
            resultados.append({
                'id': c.id,
                'codigo': c.codigo,
                'descripcion': c.descripcion,
                'nombre': c.nombre if c.nombre else c.descripcion
            })
        
        return JsonResponse({
            'resultados': resultados,
            'total': len(resultados)
        })
        
    except Exception as e:
        return JsonResponse({
            'resultados': [],
            'error': str(e)
        }, status=500)


# ============================================
# ALTERNATIVA: Si prefieres vista basada en clase
# ============================================

from django.views import View

class BuscarCIE10View(View):
    """Vista para búsqueda de códigos CIE-10"""
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse({'resultados': []})
        
        codigos = CodigoCIE10.objects.filter(
            Q(codigo__icontains=query) | 
            Q(descripcion__icontains=query),
            activo=True
        ).order_by('codigo')[:20]
        
        resultados = [{
            'id': c.id,
            'codigo': c.codigo,
            'descripcion': c.descripcion
        } for c in codigos]
        
        return JsonResponse({'resultados': resultados})


# ============================================
# VERSIÓN COMPLETA CON CACHÉ Y OPTIMIZACIÓN
# ============================================

from django.core.cache import cache
from django.db.models import Q

def api_buscar_cie10_optimizado(request):
    """
    API optimizada para búsqueda de códigos CIE-10
    Incluye caché para mejorar rendimiento
    """
    query = request.GET.get('q', '').strip().upper()
    
    if len(query) < 2:
        return JsonResponse({'resultados': []})
    
    # Intentar obtener de caché
    cache_key = f'cie10_search_{query}'
    cached_results = cache.get(cache_key)
    
    if cached_results:
        return JsonResponse({'resultados': cached_results, 'cached': True})
    
    try:
        # Buscar en BD
        codigos = CodigoCIE10.objects.filter(
            Q(codigo__icontains=query) | 
            Q(descripcion__icontains=query) |
            Q(nombre__icontains=query),
            activo=True
        ).select_related().order_by('codigo')[:20]
        
        resultados = []
        for c in codigos:
            resultados.append({
                'id': c.id,
                'codigo': c.codigo,
                'descripcion': c.descripcion,
                'categoria': c.categoria if hasattr(c, 'categoria') else ''
            })
        
        # Guardar en caché por 1 hora
        cache.set(cache_key, resultados, 3600)
        
        return JsonResponse({
            'resultados': resultados,
            'total': len(resultados),
            'cached': False
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error en búsqueda: {str(e)}'
        }, status=500)
