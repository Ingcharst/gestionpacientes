# apps/reportes/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, HttpResponse
from django.utils import timezone
from datetime import datetime

from apps.procedimientos.models import Paciente, AdmisionTerapia
from apps.reportes.models import PlantillaInforme, InformeEvolucion
from .utils import generar_pdf_informe


@login_required
def crear_informe_evolucion(request, admision_id):
    """
    Crea un informe de evolución para una admisión específica.
    """
    admision = get_object_or_404(AdmisionTerapia, id=admision_id)
    paciente = admision.paciente
    
    # Determinar rango de edad
    edad = int(paciente.edad_actual) if paciente.edad_actual else 0
    if 3 <= edad <= 6:
        rango = '3-6'
    elif 7 <= edad <= 11:
        rango = '7-11'
    elif 12 <= edad <= 16:
        rango = '12-16'
    else:
        messages.error(request, f'No hay plantilla disponible para edad {edad} años')
        return redirect('procedimientos:paciente_detail', pk=paciente.id)
    
    # Buscar plantilla
    try:
        plantilla = PlantillaInforme.objects.get(
            terapia=admision.terapia,
            rango_edad=rango,
            activo=True
        )
    except PlantillaInforme.DoesNotExist:
        messages.error(request, f'No existe plantilla para {admision.terapia.nombre} - {rango} años')
        return redirect('procedimientos:paciente_detail', pk=paciente.id)
    
    if request.method == 'POST':
        # Crear informe
        informe = InformeEvolucion.objects.create(
            paciente=paciente,
            admision=admision,
            terapia=admision.terapia,
            profesional=request.user,
            plantilla_usada=plantilla,
            periodo_inicio=admision.fecha_inicio,
            periodo_fin=admision.fecha_fin or timezone.now().date(),
            observaciones_especificas=request.POST.get('observaciones', ''),
            estado='BORRADOR'
        )
        
        # Generar contenido desde plantilla
        informe.generar_contenido_desde_plantilla()
        
        messages.success(request, 'Informe creado exitosamente')
        return redirect('reportes:informe_detail', pk=informe.id)
    
    # Mostrar vista previa de plantilla
    context = {
        'paciente': paciente,
        'admision': admision,
        'plantilla': plantilla,
        'edad': edad,
        'rango': rango
    }
    
    return render(request, 'reportes/crear_informe.html', context)


@login_required
def informe_detail(request, pk):
    """
    Detalle de un informe de evolución con opción de editar y generar PDF.
    """
    informe = get_object_or_404(InformeEvolucion, id=pk)
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'finalizar':
            informe.finalizar()
            messages.success(request, 'Informe finalizado')
        
        elif accion == 'generar_pdf':
            # Generar PDF
            pdf_file = generar_pdf_informe(informe)
            informe.archivo_pdf = pdf_file
            informe.save()
            messages.success(request, 'PDF generado exitosamente')
        
        elif accion == 'editar_observaciones':
            informe.observaciones_especificas = request.POST.get('observaciones', '')
            informe.save()
            messages.success(request, 'Observaciones actualizadas')
        
        return redirect('reportes:informe_detail', pk=informe.id)
    
    context = {
        'informe': informe
    }
    
    return render(request, 'reportes/informe_detail.html', context)


@login_required
def descargar_pdf_informe(request, pk):
    """
    Descarga el PDF del informe.
    """
    informe = get_object_or_404(InformeEvolucion, id=pk)
    
    if not informe.archivo_pdf:
        # Generar si no existe
        pdf_file = generar_pdf_informe(informe)
        informe.archivo_pdf = pdf_file
        informe.save()
    
    return FileResponse(
        informe.archivo_pdf.open('rb'),
        as_attachment=True,
        filename=f'Informe_{informe.paciente.nombre_completo}_{informe.fecha_generacion.strftime("%Y%m%d")}.pdf'
    )


@login_required
def lista_informes_paciente(request, paciente_id):
    """
    Lista todos los informes de un paciente.
    """
    paciente = get_object_or_404(Paciente, id=paciente_id)
    informes = InformeEvolucion.objects.filter(
        paciente=paciente
    ).select_related('terapia', 'profesional', 'admision')
    
    context = {
        'paciente': paciente,
        'informes': informes
    }
    
    return render(request, 'reportes/lista_informes_paciente.html', context)
