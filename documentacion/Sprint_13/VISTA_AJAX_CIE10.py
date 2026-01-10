# VISTA AJAX BÚSQUEDA CIE-10
# Archivo: apps/procedimientos/views.py
# AGREGAR AL FINAL

from django.http import JsonResponse
from django.db.models import Q

@login_required
def buscar_cie10(request):
    """
    Búsqueda AJAX de códigos CIE-10.
    Retorna JSON con resultados.
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    # Buscar en código o descripción
    codigos = CodigoCIE10.objects.filter(
        Q(codigo__icontains=query) |
        Q(descripcion__icontains=query) |
        Q(categoria__icontains=query),
        activo=True
    ).order_by('codigo')[:20]  # Limitar a 20 resultados
    
    results = [
        {
            'id': codigo.id,
            'codigo': codigo.codigo,
            'descripcion': codigo.descripcion,
            'categoria': codigo.categoria,
            'texto_completo': f"{codigo.codigo} - {codigo.descripcion}"
        }
        for codigo in codigos
    ]
    
    return JsonResponse({'results': results})


@login_required
def obtener_cie10(request, codigo_id):
    """
    Obtener un código CIE-10 específico por ID.
    """
    try:
        codigo = CodigoCIE10.objects.get(id=codigo_id)
        return JsonResponse({
            'success': True,
            'codigo': {
                'id': codigo.id,
                'codigo': codigo.codigo,
                'descripcion': codigo.descripcion,
                'categoria': codigo.categoria,
                'texto_completo': str(codigo)
            }
        })
    except CodigoCIE10.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Código no encontrado'
        }, status=404)
