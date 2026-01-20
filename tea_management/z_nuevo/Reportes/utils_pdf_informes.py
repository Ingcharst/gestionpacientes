# apps/reportes/utils.py

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from django.core.files.base import ContentFile
from io import BytesIO
import os


def generar_pdf_informe(informe):
    """
    Genera un PDF del informe de evolución con tabla de identificación y firma.
    
    Args:
        informe: Instancia de InformeEvolucion
    
    Returns:
        ContentFile con el PDF generado
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            topMargin=0.5*inch, bottomMargin=0.5*inch,
                            leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    # Estilos
    styles = getSampleStyleSheet()
    
    titulo_style = ParagraphStyle(
        'TituloInforme',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.HexColor('#2c5f8d'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    # Elementos del documento
    elementos = []
    
    # 1. TÍTULO
    titulo = Paragraph(
        informe.plantilla_usada.titulo if informe.plantilla_usada else 'INFORME DE EVOLUCIÓN',
        titulo_style
    )
    elementos.append(titulo)
    elementos.append(Spacer(1, 0.2*inch))
    
    # 2. TABLA DE IDENTIFICACIÓN
    paciente = informe.paciente
    admision = informe.admision
    
    datos_tabla = [
        ['Nombres y Apellidos:', paciente.nombre_completo, 
         'Documento de identidad:', paciente.numero_documento],
        ['Edad:', f"{int(paciente.edad_actual)} años" if paciente.edad_actual else 'N/A',
         'Fecha de Nacimiento:', paciente.fecha_nacimiento.strftime('%d/%m/%Y')],
        ['Admisión:', admision.numero_admision,
         'Número de Intervenciones:', str(admision.cantidad_realizada)],
        ['Escolaridad:', getattr(paciente, 'nivel_escolar', 'N/A'),
         'Acudiente:', paciente.nombre_responsable],
        ['Diagnóstico:', paciente.diagnostico_principal,
         'Profesional:', informe.profesional.get_full_name()],
        ['EPS:', paciente.eps or 'N/A',
         'Autorización:', admision.numero_admision]
    ]
    
    tabla_identificacion = Table(datos_tabla, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    tabla_identificacion.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#e8f4f8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    elementos.append(tabla_identificacion)
    elementos.append(Spacer(1, 0.3*inch))
    
    # 3. CONTENIDO DEL INFORME
    # Dividir contenido en párrafos
    contenido_texto = informe.contenido_informe
    parrafos = contenido_texto.split('\n\n')
    
    for parrafo in parrafos:
        if parrafo.strip():
            # Detectar si es un título (todo mayúsculas o termina en :)
            if parrafo.isupper() or parrafo.strip().endswith(':'):
                p = Paragraph(parrafo, subtitle_style)
            else:
                p = Paragraph(parrafo, normal_style)
            elementos.append(p)
            elementos.append(Spacer(1, 0.1*inch))
    
    # 4. OBSERVACIONES ESPECÍFICAS
    if informe.observaciones_especificas:
        elementos.append(Spacer(1, 0.2*inch))
        elementos.append(Paragraph('OBSERVACIONES ADICIONALES DEL PROFESIONAL', subtitle_style))
        elementos.append(Paragraph(informe.observaciones_especificas, normal_style))
    
    # 5. RECOMENDACIONES (si están en la plantilla)
    if informe.plantilla_usada:
        if informe.plantilla_usada.recomendaciones_familia:
            elementos.append(Spacer(1, 0.2*inch))
            elementos.append(Paragraph('RECOMENDACIONES FAMILIA', subtitle_style))
            elementos.append(Paragraph(informe.plantilla_usada.recomendaciones_familia, normal_style))
        
        if informe.plantilla_usada.recomendaciones_escuela:
            elementos.append(Spacer(1, 0.2*inch))
            elementos.append(Paragraph('RECOMENDACIONES ESCOLARIDAD', subtitle_style))
            elementos.append(Paragraph(informe.plantilla_usada.recomendaciones_escuela, normal_style))
    
    # 6. FIRMA DEL PROFESIONAL
    elementos.append(Spacer(1, 0.5*inch))
    
    if informe.firma_profesional and os.path.exists(informe.firma_profesional.path):
        try:
            # Insertar imagen de firma
            firma_img = Image(informe.firma_profesional.path, width=2*inch, height=1*inch)
            firma_img.hAlign = 'CENTER'
            elementos.append(firma_img)
        except:
            # Si falla, mostrar texto
            elementos.append(Paragraph('_________________________', normal_style))
    else:
        elementos.append(Paragraph('_________________________', normal_style))
    
    # Nombre del profesional
    firma_texto = Paragraph(
        f'<b>{informe.profesional.get_full_name()}</b><br/>'
        f'{informe.profesional.get_rol_display()}<br/>'
        f'Fecha: {informe.fecha_generacion.strftime("%d/%m/%Y")}',
        ParagraphStyle('Firma', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9)
    )
    elementos.append(firma_texto)
    
    # Construir PDF
    doc.build(elementos)
    
    # Guardar en ContentFile
    buffer.seek(0)
    filename = f'informe_{informe.paciente.numero_documento}_{informe.fecha_generacion.strftime("%Y%m%d")}.pdf'
    
    return ContentFile(buffer.read(), name=filename)
