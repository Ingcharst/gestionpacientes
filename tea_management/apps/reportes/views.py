"""
Vistas para el módulo de reportes.
"""
from datetime import datetime, timedelta, date
from calendar import monthrange
from decimal import Decimal
from pyexpat.errors import messages
import io
from docx import Document
from docx.shared import Inches
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponse
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone

from apps.procedimientos.models import (
    AdmisionTerapia, Paciente, Procedimiento, SesionTerapeutica,
    ObjetivoTerapeutico, EvolucionPaciente
)
from apps.grupos.models import GrupoTerapeutico, AsignacionGrupo
from apps.reportes.models import InformeEvolucion, PlantillaInforme
from apps.terapias.models import Terapia
from apps.usuarios.models import Perfil, Usuario

from .utils import (
    ReportePDFGenerator, ReporteExcelGenerator,
    calcular_totales_procedimientos, calcular_totales_sesiones,
    formato_moneda, obtener_nombre_mes, generar_pdf_informe
)

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas


@login_required
def reportes_dashboard(request):
    """Dashboard principal de reportes."""
    context = {
        'total_pacientes': Paciente.objects.filter(estado='ACTIVO').count(),
        'total_terapeutas': Usuario.objects.filter(rol__in=['TERAPEUTA', 'PSICOLOGO', 'MEDICO']).count(),
        'total_grupos': GrupoTerapeutico.objects.filter(activo=True).count(),
    }
    return render(request, 'reportes/dashboard.html', context)


# ============================================================================
# REPORTE 1: INFORME MENSUAL POR PACIENTE (Para facturación)
# ============================================================================

@login_required
def informe_mensual_paciente_form(request):
    """Formulario para generar informe mensual de paciente."""
    pacientes = Paciente.objects.filter(estado='ACTIVO').order_by('apellidos', 'nombres')
    
    # Obtener mes y año actual
    hoy = datetime.now()
    
    context = {
        'pacientes': pacientes,
        'mes_actual': hoy.month,
        'anio_actual': hoy.year,
        'meses': [(i, obtener_nombre_mes(i)) for i in range(1, 13)],
        'anios': list(range(hoy.year - 2, hoy.year + 1)),
    }
    return render(request, 'reportes/informe_mensual_paciente_form.html', context)


@login_required
def generar_informe_mensual_paciente_pdf(request, paciente_id):
    """Generar PDF del informe mensual de un paciente."""
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Obtener mes y año de los parámetros
    mes = int(request.GET.get('mes', datetime.now().month))
    anio = int(request.GET.get('anio', datetime.now().year))
    
    # Calcular rango de fechas
    primer_dia = datetime(anio, mes, 1).date()
    ultimo_dia = datetime(anio, mes, monthrange(anio, mes)[1]).date()
    
    # Obtener procedimientos del mes
    procedimientos = Procedimiento.objects.filter(
        paciente=paciente,
        fecha__gte=primer_dia,
        fecha__lte=ultimo_dia
    ).order_by('fecha')
    
    # Obtener sesiones del mes
    sesiones = SesionTerapeutica.objects.filter(
        paciente=paciente,
        fecha__gte=primer_dia,
        fecha__lte=ultimo_dia
    ).select_related('terapia', 'terapeuta').order_by('fecha')
    
    # Calcular totales
    totales_proc = calcular_totales_procedimientos(procedimientos)
    totales_ses = calcular_totales_sesiones(sesiones)
    
    # Generar PDF
    titulo = f"INFORME MENSUAL - {obtener_nombre_mes(mes).upper()} {anio}"
    subtitulo = f"Paciente: {paciente.nombre_completo}"
    
    pdf_gen = ReportePDFGenerator(titulo, subtitulo)
    doc = pdf_gen.crear_documento()
    
    elementos = pdf_gen.crear_encabezado()
    
    # Información del paciente
    from reportlab.platypus import Paragraph, Spacer
    from reportlab.lib.units import inch
    
    elementos.append(Paragraph(
        f"<b>HC:</b> {paciente.numero_historia_clinica} | "
        f"<b>Documento:</b> {paciente.numero_documento}",
        pdf_gen.styles['Normal']
    ))
    elementos.append(Spacer(1, 0.2*inch))
    
    # Tabla de sesiones terapéuticas
    if sesiones.exists():
        elementos.append(Paragraph("<b>SESIONES TERAPÉUTICAS</b>", pdf_gen.styles['Heading2']))
        elementos.append(Spacer(1, 0.1*inch))
        
        datos_sesiones = [['Fecha', 'Terapia', 'Terapeuta', 'Duración', 'Valor']]
        for sesion in sesiones:
            datos_sesiones.append([
                sesion.fecha.strftime('%d/%m/%Y'),
                sesion.terapia.nombre[:30],
                sesion.terapeuta.nombre_completo[:25],
                f"{sesion.duracion_minutos} min",
                formato_moneda(sesion.valor_sesion)
            ])
        
        tabla_sesiones = pdf_gen.crear_tabla(
            datos_sesiones,
            col_widths=[1*inch, 2*inch, 1.8*inch, 0.8*inch, 1*inch]
        )
        elementos.append(tabla_sesiones)
        elementos.append(Spacer(1, 0.2*inch))
        
        # Subtotal sesiones
        elementos.append(Paragraph(
            f"<b>Subtotal Sesiones:</b> {formato_moneda(totales_ses['total'])} "
            f"({totales_ses['cantidad']} sesión{'es' if totales_ses['cantidad'] != 1 else ''})",
            pdf_gen.styles['Normal']
        ))
        elementos.append(Spacer(1, 0.3*inch))
    
    # Tabla de procedimientos
    if procedimientos.exists():
        elementos.append(Paragraph("<b>PROCEDIMIENTOS</b>", pdf_gen.styles['Heading2']))
        elementos.append(Spacer(1, 0.1*inch))
        
        datos_proc = [['Fecha', 'Tipo', 'Profesional', 'Valor']]
        for proc in procedimientos:
            datos_proc.append([
                proc.fecha.strftime('%d/%m/%Y'),
                proc.tipo_procedimiento[:35],
                proc.profesional.nombre_completo[:30],
                formato_moneda(proc.valor_total)
            ])
        
        tabla_proc = pdf_gen.crear_tabla(
            datos_proc,
            col_widths=[1*inch, 2.5*inch, 2*inch, 1.1*inch]
        )
        elementos.append(tabla_proc)
        elementos.append(Spacer(1, 0.2*inch))
        
        # Subtotal procedimientos
        elementos.append(Paragraph(
            f"<b>Subtotal Procedimientos:</b> {formato_moneda(totales_proc['total'])} "
            f"({totales_proc['cantidad']} procedimiento{'s' if totales_proc['cantidad'] != 1 else ''})",
            pdf_gen.styles['Normal']
        ))
        elementos.append(Spacer(1, 0.3*inch))
    
    # Total general
    total_general = totales_ses['total'] + totales_proc['total']
    elementos.append(Paragraph(
        f"<b>TOTAL GENERAL: {formato_moneda(total_general)}</b>",
        pdf_gen.styles['Heading2']
    ))
    
    # Construir PDF
    doc.build(elementos)
    
    # Nombre del archivo
    filename = f"informe_mensual_{paciente.apellidos}_{mes}_{anio}.pdf"
    return pdf_gen.get_response(filename)


@login_required
def generar_informe_mensual_paciente_excel(request, paciente_id):
    """Generar Excel del informe mensual de un paciente."""
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Obtener mes y año
    mes = int(request.GET.get('mes', datetime.now().month))
    anio = int(request.GET.get('anio', datetime.now().year))
    
    # Calcular rango de fechas
    primer_dia = datetime(anio, mes, 1).date()
    ultimo_dia = datetime(anio, mes, monthrange(anio, mes)[1]).date()
    
    # Obtener datos
    procedimientos = Procedimiento.objects.filter(
        paciente=paciente,
        fecha__gte=primer_dia,
        fecha__lte=ultimo_dia
    ).order_by('fecha')
    
    sesiones = SesionTerapeutica.objects.filter(
        paciente=paciente,
        fecha__gte=primer_dia,
        fecha__lte=ultimo_dia
    ).select_related('terapia', 'terapeuta').order_by('fecha')
    
    # Crear Excel
    excel_gen = ReporteExcelGenerator("Informe Mensual")
    excel_gen.agregar_titulo(
        f"INFORME MENSUAL - {obtener_nombre_mes(mes).upper()} {anio}",
        columnas=5
    )
    
    # Información del paciente
    excel_gen.ws.cell(row=excel_gen.current_row, column=1, value="Paciente:")
    excel_gen.ws.cell(row=excel_gen.current_row, column=2, value=paciente.nombre_completo)
    excel_gen.current_row += 1
    excel_gen.ws.cell(row=excel_gen.current_row, column=1, value="HC:")
    excel_gen.ws.cell(row=excel_gen.current_row, column=2, value=paciente.numero_historia_clinica)
    excel_gen.current_row += 2
    
    # Sesiones
    if sesiones.exists():
        excel_gen.agregar_encabezados(['Fecha', 'Terapia', 'Terapeuta', 'Duración (min)', 'Valor'])
        for sesion in sesiones:
            excel_gen.agregar_fila([
                sesion.fecha.strftime('%d/%m/%Y'),
                sesion.terapia.nombre,
                sesion.terapeuta.nombre_completo,
                sesion.duracion_minutos,
                float(sesion.valor_sesion) if sesion.valor_sesion else 0
            ])
        excel_gen.current_row += 1
    
    # Procedimientos
    if procedimientos.exists():
        excel_gen.current_row += 1
        excel_gen.agregar_encabezados(['Fecha', 'Tipo Procedimiento', 'Profesional', 'Valor'])
        for proc in procedimientos:
            excel_gen.agregar_fila([
                proc.fecha.strftime('%d/%m/%Y'),
                proc.tipo_procedimiento,
                proc.profesional.nombre_completo,
                float(proc.valor_total) if proc.valor_total else 0
            ])
    
    excel_gen.ajustar_columnas()
    
    filename = f"informe_mensual_{paciente.apellidos}_{mes}_{anio}.xlsx"
    return excel_gen.get_response(filename)


# ============================================================================
# REPORTE 2: INFORME TRIMESTRAL DE AVANCE DE PACIENTE
# ============================================================================

@login_required
def informe_trimestral_avance_form(request):
    """Formulario para informe trimestral de avance."""
    pacientes = Paciente.objects.filter(estado='ACTIVO').order_by('apellidos', 'nombres')
    
    # Trimestres del año
    hoy = datetime.now()
    trimestre_actual = ((hoy.month - 1) // 3) + 1
    
    context = {
        'pacientes': pacientes,
        'trimestre_actual': trimestre_actual,
        'anio_actual': hoy.year,
        'trimestres': [
            (1, 'Primer Trimestre (Ene-Mar)'),
            (2, 'Segundo Trimestre (Abr-Jun)'),
            (3, 'Tercer Trimestre (Jul-Sep)'),
            (4, 'Cuarto Trimestre (Oct-Dic)'),
        ],
        'anios': list(range(hoy.year - 2, hoy.year + 1)),
    }
    return render(request, 'reportes/informe_trimestral_avance_form.html', context)


@login_required
def generar_informe_trimestral_avance_pdf(request, paciente_id):
    """Generar PDF del informe trimestral de avance."""
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Obtener trimestre y año
    trimestre = int(request.GET.get('trimestre', 1))
    anio = int(request.GET.get('anio', datetime.now().year))
    
    # Calcular meses del trimestre
    mes_inicio = ((trimestre - 1) * 3) + 1
    mes_fin = mes_inicio + 2
    
    # Fechas
    fecha_inicio = datetime(anio, mes_inicio, 1).date()
    fecha_fin = datetime(anio, mes_fin, monthrange(anio, mes_fin)[1]).date()
    
    # Obtener evoluciones del trimestre
    evoluciones = EvolucionPaciente.objects.filter(
        paciente=paciente,
        fecha_sesion__gte=fecha_inicio,
        fecha_sesion__lte=fecha_fin
    ).select_related('profesional').order_by('fecha_sesion')
    
    # Obtener objetivos terapéuticos
    objetivos = ObjetivoTerapeutico.objects.filter(
        paciente=paciente
    ).order_by('-fecha_logro')
    
    # Sesiones del trimestre
    sesiones = SesionTerapeutica.objects.filter(
        paciente=paciente,
        fecha__gte=fecha_inicio,
        fecha__lte=fecha_fin
    ).select_related('terapia')
    
    # Estadísticas
    total_sesiones = sesiones.count()
    sesiones_completadas = sesiones.filter(estado='COMPLETADA').count()
    terapias_recibidas = sesiones.values('terapia__nombre').annotate(
        cantidad=Count('id')
    ).order_by('-cantidad')
    
    # Generar PDF
    titulo = f"INFORME TRIMESTRAL DE AVANCE - T{trimestre} {anio}"
    subtitulo = f"Paciente: {paciente.nombre_completo}"
    
    pdf_gen = ReportePDFGenerator(titulo, subtitulo)
    doc = pdf_gen.crear_documento()
    
    elementos = pdf_gen.crear_encabezado()
    
    from reportlab.platypus import Paragraph, Spacer
    from reportlab.lib.units import inch
    
    # Información del paciente
    elementos.append(Paragraph(
        f"<b>HC:</b> {paciente.numero_historia_clinica} | "
        f"<b>Edad:</b> {paciente.edad} años | "
        f"<b>Fecha Ingreso:</b> {paciente.fecha_ingreso.strftime('%d/%m/%Y')}",
        pdf_gen.styles['Normal']
    ))
    elementos.append(Paragraph(
        f"<b>Período:</b> {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}",
        pdf_gen.styles['Normal']
    ))
    elementos.append(Spacer(1, 0.3*inch))
    
    # Resumen estadístico
    elementos.append(Paragraph("<b>RESUMEN DEL TRIMESTRE</b>", pdf_gen.styles['Heading2']))
    elementos.append(Spacer(1, 0.1*inch))
    
    datos_resumen = [['Indicador', 'Valor']]
    datos_resumen.append(['Total de Sesiones', str(total_sesiones)])
    datos_resumen.append(['Sesiones Completadas', str(sesiones_completadas)])
    datos_resumen.append(['Tasa de Asistencia', 
                            f"{(sesiones_completadas/total_sesiones*100):.1f}%" if total_sesiones > 0 else "N/A"])
    # datos_resumen.append(['Evoluciones Registradas', str(evoluciones.count())])
    
    tabla_resumen = pdf_gen.crear_tabla(datos_resumen, col_widths=[3*inch, 2*inch])
    elementos.append(tabla_resumen)
    elementos.append(Spacer(1, 0.3*inch))
    
    # Terapias recibidas
    if terapias_recibidas:
        elementos.append(Paragraph("<b>TERAPIAS RECIBIDAS</b>", pdf_gen.styles['Heading2']))
        elementos.append(Spacer(1, 0.1*inch))
        
        datos_terapias = [['Terapia', 'Sesiones']]
        for terapia in terapias_recibidas[:5]:  # Top 5
            datos_terapias.append([
                terapia['terapia__nombre'][:40],
                str(terapia['cantidad'])
            ])
        
        tabla_terapias = pdf_gen.crear_tabla(datos_terapias, col_widths=[4*inch, 1.5*inch])
        elementos.append(tabla_terapias)
        elementos.append(Spacer(1, 0.3*inch))
    
    # Objetivos terapéuticos
    if objetivos.exists():
        elementos.append(Paragraph("<b>OBJETIVOS TERAPÉUTICOS</b>", pdf_gen.styles['Heading2']))
        elementos.append(Spacer(1, 0.1*inch))
        
        datos_objetivos = [['Objetivo', 'Estado', 'Progreso']]
        for obj in objetivos[:5]:  # Primeros 5
            datos_objetivos.append([
                obj.descripcion[:45],
                obj.get_estado_display(),
                f"{obj.progreso}%"
            ])
        
        tabla_objetivos = pdf_gen.crear_tabla(
            datos_objetivos,
            col_widths=[3*inch, 1.2*inch, 1*inch]
        )
        elementos.append(tabla_objetivos)
        elementos.append(Spacer(1, 0.3*inch))
    
    # Evoluciones clínicas
    # if evoluciones.exists():
    #     elementos.append(Paragraph("<b>EVOLUCIONES CLÍNICAS</b>", pdf_gen.styles['Heading2']))
    #     elementos.append(Spacer(1, 0.1*inch))
        
    #     for evol in evoluciones[:3]:  # Últimas 3 evoluciones
    #         elementos.append(Paragraph(
    #             f"<b>{evol.fecha.strftime('%d/%m/%Y')} - {evol.profesional.nombre_completo}</b>",
    #             pdf_gen.styles['Normal']
    #         ))
    #         elementos.append(Paragraph(
    #             evol.descripcion[:300] + ("..." if len(evol.descripcion) > 300 else ""),
    #             pdf_gen.styles['Normal']
    #         ))
    #         elementos.append(Spacer(1, 0.15*inch))
    
    # Construir PDF
    doc.build(elementos)
    
    filename = f"informe_trimestral_{paciente.apellidos}_T{trimestre}_{anio}.pdf"
    return pdf_gen.get_response(filename)


# Continuará con más reportes...


# ============================================================================
# REPORTE 3: REPORTE DE ASISTENCIA DE PACIENTES
# ============================================================================

@login_required
def reporte_asistencia_form(request):
    """Formulario para reporte de asistencia."""
    hoy = datetime.now()
    context = {
        'mes_actual': hoy.month,
        'anio_actual': hoy.year,
        'meses': [(i, obtener_nombre_mes(i)) for i in range(1, 13)],
        'anios': list(range(hoy.year - 2, hoy.year + 1)),
    }
    return render(request, 'reportes/reporte_asistencia_form.html', context)


@login_required
def generar_reporte_asistencia_pdf(request):
    """Generar reporte de asistencia en PDF."""
    mes = int(request.GET.get('mes', datetime.now().month))
    anio = int(request.GET.get('anio', datetime.now().year))
    
    primer_dia = datetime(anio, mes, 1).date()
    ultimo_dia = datetime(anio, mes, monthrange(anio, mes)[1]).date()
    
    # Obtener todas las sesiones del mes
    sesiones = SesionTerapeutica.objects.filter(
        fecha__gte=primer_dia,
        fecha__lte=ultimo_dia
    ).select_related('paciente', 'terapia')
    
    # Agrupar por paciente
    pacientes_dict = {}
    for sesion in sesiones:
        if sesion.paciente.id not in pacientes_dict:
            pacientes_dict[sesion.paciente.id] = {
                'paciente': sesion.paciente,
                'programadas': 0,
                'asistidas': 0,
                'inasistencias': 0
            }
        
        pacientes_dict[sesion.paciente.id]['programadas'] += 1
        if sesion.estado == 'COMPLETADA':
            pacientes_dict[sesion.paciente.id]['asistidas'] += 1
        elif sesion.estado == 'INASISTENCIA':
            pacientes_dict[sesion.paciente.id]['inasistencias'] += 1
    
    # Generar PDF
    titulo = f"REPORTE DE ASISTENCIA - {obtener_nombre_mes(mes).upper()} {anio}"
    pdf_gen = ReportePDFGenerator(titulo)
    doc = pdf_gen.crear_documento()
    
    elementos = pdf_gen.crear_encabezado()
    
    from reportlab.platypus import Paragraph, Spacer
    from reportlab.lib.units import inch
    
    # Tabla de asistencia
    datos = [['Paciente', 'HC', 'Programadas', 'Asistidas', 'Inasistencias', '% Asist.']]
    
    for data in pacientes_dict.values():
        porcentaje = (data['asistidas'] / data['programadas'] * 100) if data['programadas'] > 0 else 0
        datos.append([
            data['paciente'].nombre_completo[:25],
            data['paciente'].numero_historia_clinica,
            str(data['programadas']),
            str(data['asistidas']),
            str(data['inasistencias']),
            f"{porcentaje:.1f}%"
        ])
    
    tabla = pdf_gen.crear_tabla(datos, col_widths=[2*inch, 1*inch, 0.9*inch, 0.9*inch, 1*inch, 0.8*inch])
    elementos.append(tabla)
    
    doc.build(elementos)
    
    filename = f"reporte_asistencia_{mes}_{anio}.pdf"
    return pdf_gen.get_response(filename)


# ============================================================================
# REPORTE 4: REPORTE DE PRODUCTIVIDAD DE TERAPEUTAS
# ============================================================================

@login_required
def reporte_terapeutas_form(request):
    """Formulario para reporte de terapeutas."""
    terapeutas = Usuario.objects.filter(rol='TERAPEUTA', estado='ACTIVO')
    hoy = datetime.now()
    
    context = {
        'terapeutas': terapeutas,
        'mes_actual': hoy.month,
        'anio_actual': hoy.year,
        'meses': [(i, obtener_nombre_mes(i)) for i in range(1, 13)],
        'anios': list(range(hoy.year - 2, hoy.year + 1)),
    }
    return render(request, 'reportes/reporte_terapeutas_form.html', context)


@login_required
def generar_reporte_terapeutas_pdf(request):
    """Generar reporte de productividad de terapeutas."""
    mes = int(request.GET.get('mes', datetime.now().month))
    anio = int(request.GET.get('anio', datetime.now().year))
    
    primer_dia = datetime(anio, mes, 1).date()
    ultimo_dia = datetime(anio, mes, monthrange(anio, mes)[1]).date()
    
    # Obtener terapeutas con sus estadísticas
    terapeutas = Usuario.objects.filter(rol='TERAPEUTA', estado='ACTIVO')
    
    datos_terapeutas = []
    for terapeuta in terapeutas:
        sesiones = SesionTerapeutica.objects.filter(
            terapeuta=terapeuta,
            fecha__gte=primer_dia,
            fecha__lte=ultimo_dia
        )
        
        total_sesiones = sesiones.count()
        completadas = sesiones.filter(estado='COMPLETADA').count()
        pacientes_atendidos = sesiones.values('paciente').distinct().count()
        
        if total_sesiones > 0:
            datos_terapeutas.append({
                'terapeuta': terapeuta,
                'total_sesiones': total_sesiones,
                'completadas': completadas,
                'pacientes': pacientes_atendidos,
                'tasa': (completadas / total_sesiones * 100) if total_sesiones > 0 else 0
            })
    
    # Generar PDF
    titulo = f"REPORTE DE TERAPEUTAS - {obtener_nombre_mes(mes).upper()} {anio}"
    pdf_gen = ReportePDFGenerator(titulo)
    doc = pdf_gen.crear_documento()
    
    elementos = pdf_gen.crear_encabezado()
    
    from reportlab.platypus import Paragraph, Spacer
    from reportlab.lib.units import inch
    
    # Tabla
    datos = [['Terapeuta', 'Sesiones', 'Completadas', 'Pacientes', '% Complet.']]
    
    for data in sorted(datos_terapeutas, key=lambda x: x['total_sesiones'], reverse=True):
        datos.append([
            data['terapeuta'].nombre_completo[:30],
            str(data['total_sesiones']),
            str(data['completadas']),
            str(data['pacientes']),
            f"{data['tasa']:.1f}%"
        ])
    
    tabla = pdf_gen.crear_tabla(datos, col_widths=[2.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    elementos.append(tabla)
    
    doc.build(elementos)
    
    filename = f"reporte_terapeutas_{mes}_{anio}.pdf"
    return pdf_gen.get_response(filename)


# ============================================================================
# REPORTE 5: REPORTE DE GRUPOS TERAPÉUTICOS
# ============================================================================

@login_required
def reporte_grupos(request):
    """Reporte general de grupos terapéuticos."""
    grupos = GrupoTerapeutico.objects.filter(activo=True).prefetch_related('asignaciones')
    
    datos_grupos = []
    for grupo in grupos:
        asignaciones_activas = grupo.asignaciones.filter(estado='ACTIVA').count()
        datos_grupos.append({
            'grupo': grupo,
            'asignados': asignaciones_activas,
            'disponibles': grupo.cupos_disponibles,
            'ocupacion': (asignaciones_activas / grupo.capacidad_maxima * 100) if grupo.capacidad_maxima > 0 else 0
        })
    
    context = {
        'datos_grupos': datos_grupos
    }
    
    return render(request, 'reportes/reporte_grupos.html', context)


@login_required
def generar_reporte_grupos_pdf(request):
    """Generar PDF de reporte de grupos."""
    grupos = GrupoTerapeutico.objects.filter(activo=True)
    
    # Generar PDF
    titulo = "REPORTE DE GRUPOS TERAPÉUTICOS"
    pdf_gen = ReportePDFGenerator(titulo)
    doc = pdf_gen.crear_documento()
    
    elementos = pdf_gen.crear_encabezado()
    
    from reportlab.platypus import Paragraph, Spacer
    from reportlab.lib.units import inch
    
    # Tabla
    datos = [['Grupo', 'Capacidad', 'Asignados', 'Disponibles', '% Ocupación']]
    
    for grupo in grupos:
        asignados = grupo.asignaciones.filter(estado='ACTIVA').count()
        disponibles = grupo.cupos_disponibles
        ocupacion = (asignados / grupo.capacidad_maxima * 100) if grupo.capacidad_maxima > 0 else 0
        
        datos.append([
            grupo.nombre[:30],
            str(grupo.capacidad_maxima),
            str(asignados),
            str(disponibles),
            f"{ocupacion:.1f}%"
        ])
    
    tabla = pdf_gen.crear_tabla(datos, col_widths=[2.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    elementos.append(tabla)
    
    doc.build(elementos)
    
    filename = "reporte_grupos.pdf"
    return pdf_gen.get_response(filename)


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



def informe_mensual_paciente_pdf(request, paciente_id):
    from PIL import Image as PILImage
    """Generar informe mensual en PDF"""
    
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    terapia_id = request.GET.get('terapia')
    profesional_id = request.GET.get('profesional')
    mes = int(request.GET.get('mes', timezone.now().month))
    anio = int(request.GET.get('anio', timezone.now().year))
    
    if not terapia_id or not profesional_id:
        return HttpResponse("Falta terapia o profesional", status=400)
    
    terapia = get_object_or_404(Terapia, pk=terapia_id)
    profesional = get_object_or_404(Usuario, pk=profesional_id)
    perfil = get_object_or_404(Perfil, usuario=profesional_id) 
    
    # Calcular edad
    edad = calcular_edad(paciente.fecha_nacimiento)
    rango = '3-6' if edad <= 6 else '7-11' if edad <= 11 else '12-16'
    
    # Buscar plantilla
    try:
        plantilla = PlantillaInforme.objects.get(
            terapia=terapia,
            rango_edad=rango,
            activo=True
        )
    except PlantillaInforme.DoesNotExist:
        return HttpResponse(f"No existe plantilla para {terapia.nombre} - {rango} años", status=404)
    
    # Crear PDF
    buffer = io.BytesIO()

    # Función para convertir logo
    def convertir_logo(logo_path):
        """Convierte PNG con transparencia a RGB para PDF"""
        try:
            # Abrir imagen
            img = PILImage.open(logo_path)
            
            # Convertir a RGB (sin transparencia)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Crear fondo blanco
                background = PILImage.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Guardar temporal
            temp_path = 'static/img/logo_temp.jpg'
            img.save(temp_path, 'JPEG', quality=95)
            return temp_path
        except Exception as e:
            print(f"Error convirtiendo logo: {e}")
            return None
    
    # Función para header/footer
    def agregar_encabezado_pie(canvas, doc):
        canvas.saveState()
        
        # ENCABEZADO
        try:
            logo_path = 'static/img/logo.png'
            logo_convertido = convertir_logo(logo_path)
            
            if logo_convertido:
                canvas.drawImage(
                    logo_convertido, 
                    2.5*inch, 10*inch, 
                    width=2*inch, 
                    height=0.6*inch, 
                    preserveAspectRatio=True,
                    mask='auto'
                )
        except Exception as e:
            print(f"Error cargando logo: {e}")
            canvas.setFont('Helvetica-Bold', 12)
            canvas.drawCentredString(4.25*inch, 10.2*inch, 'VIDAMED SALUD INTEGRAL')
        
        # PIE DE PÁGINA
        canvas.setFont('Helvetica', 9)
        canvas.setFillColorRGB(0.5, 0.5, 0.5)
        canvas.drawCentredString(
            4.25*inch, 0.5*inch,
            'Dirección: Calle 22 # 18A - 48 Teléfono: 3207058980 e-mail: Info@ipsvidamed.com  sitio web: www.ipsvidamed.com'
        )
        
        canvas.restoreState()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=1.2*inch,
        bottomMargin=0.8*inch,
        leftMargin=inch,
        rightMargin=inch
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    style_titulo = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    style_normal = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=10
    )
    
    style_bold = ParagraphStyle(
        'CustomBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        spaceAfter=10
    )
    
    style_firma = ParagraphStyle(
        'CustomFirma',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=4
    )
    
    # Contenido
    story = []
    
    # 1. TÍTULO
    story.append(Paragraph(f'INFORME DE TERAPIA {terapia.nombre.upper()}', style_titulo))
    story.append(Spacer(1, 0.3*inch))
    
    # Función auxiliar para valores seguros
    def safe_str(valor, default='N/A'):
        """Convierte cualquier valor a string seguro"""
        if valor is None or valor == '':
            return default
        return str(valor)
    
    # 2. TABLA DE INFORMACIÓN
    # Preparar datos en formato 2x2 (etiqueta-valor por celda)
    datos_raw = [
        ('Nombres y Apellidos:', safe_str(paciente.nombre_completo), 
        'Documento de identidad:', safe_str(paciente.numero_documento)),
        ('Edad:', f'{edad} años', 
        'Fecha de Nacimiento:', safe_str(paciente.fecha_nacimiento.strftime('%d/%m/%Y') if paciente.fecha_nacimiento else None)),
        ('Admisión:', safe_str(getattr(paciente, 'numero_admision', None)), 
        'Número de Intervenciones:', 'N/A'),
        ('Escolaridad:', safe_str(getattr(paciente, 'nivel_escolar', None)), 
        'Acudiente:', safe_str(getattr(paciente, 'nombre_responsable', None))),
        ('Diagnóstico:', safe_str(getattr(paciente, 'diagnostico_principal', None)), 
        'Profesional:', safe_str(profesional.get_full_name())),
        ('EPS:', safe_str(getattr(paciente, 'eps', None)), 
        'Autorización:', 'N/A'),
    ]
   # Estilo para etiquetas
    style_etiqueta = ParagraphStyle(
        'Etiqueta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.black,
        spaceAfter=2
    )

    # Estilo para valores
    style_valor = ParagraphStyle(
        'Valor',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.black
    )

    # Construir tabla
    tabla_datos = []
    for etiq1, val1, etiq2, val2 in datos_raw:
        celda1 = [
            Paragraph(str(etiq1), style_etiqueta),
            Paragraph(str(val1), style_valor)
        ]
        
        celda2 = [
            Paragraph(str(etiq2), style_etiqueta),
            Paragraph(str(val2), style_valor)
        ]
        
        tabla_datos.append([celda1, celda2])
    
    tabla = Table(tabla_datos, colWidths=[3.25*inch, 3.25*inch])
    tabla.setStyle(TableStyle([
        # Bordes
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        
        # Alineación vertical superior
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(Paragraph("IDENTIFICACIÓN:", style_bold))
    story.append(Spacer(1, 0.1*inch))    
    story.append(tabla)
    story.append(Spacer(1, 0.3*inch))
    
    # 3. CONTENIDO DEL INFORME
    contenido = plantilla.contenido_principal
    contenido = contenido.replace('{nombre_paciente}', paciente.nombre_completo)
    contenido = contenido.replace('{edad}', str(edad))
    
    for parrafo in contenido.split('\n\n'):
        if parrafo.strip():
            story.append(Paragraph(parrafo.strip(), style_normal))
    
    # 4. RECOMENDACIONES
    if plantilla.recomendaciones_familia:
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph('<b>Familia:</b>', style_bold))
        story.append(Paragraph(plantilla.recomendaciones_familia, style_normal))
    
    if plantilla.recomendaciones_escuela:
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph('<b>Escolaridad:</b>', style_bold))
        story.append(Paragraph(plantilla.recomendaciones_escuela, style_normal))
    
    story.append(Spacer(1, 0.4*inch))
    
    # 5. FIRMA
    if hasattr(profesional, 'firma') and profesional.firma:
        try:
            img_firma = Image(profesional.firma.path, width=2*inch, height=1*inch)
            img_firma.hAlign = 'CENTER'
            story.append(img_firma)
        except:
            pass
    
    # 6. PIE DE FIRMA
    story.append(Spacer(1, 0.1*inch))

    # Obtener datos de forma segura
    try:
        # Campos directos de Usuario
        tipo_id = profesional.tipo_identificacion or 'CC'
        numero_id = profesional.numero_identificacion or 'N/A'
        cedula_prof = profesional.cedula_profesional or 'N/A'
        
        # Campos del Perfil (relación OneToOne)
        if hasattr(profesional, 'perfil'):
            universidad = profesional.perfil.universidad or 'UNIVERSIDAD'
            especialidades = profesional.perfil.especialidades or terapia.nombre
        else:
            universidad = 'UNIVERSIDAD'
            especialidades = terapia.nombre
            
    except Exception as e:
        print(f"Error obteniendo datos del perfil: {e}")
        tipo_id = 'CC'
        numero_id = 'N/A'
        cedula_prof = 'N/A'
        universidad = 'UNIVERSIDAD'
        especialidades = terapia.nombre

    firma_info = [
        f'<b>{profesional.get_full_name().upper()}</b>',
        f"{tipo_id} {numero_id}",
        universidad.upper(),
        especialidades.upper(),
        f"T.P. {cedula_prof}"
    ]

    for linea in firma_info:
        story.append(Paragraph(linea, style_firma))
        
    # firma_info = [
    #     f'<b>{profesional.get_full_name().upper()}</b>',
    #     f"{getattr(profesional, 'tipo_identificacion', 'CC')} {getattr(profesional, 'numero_identificacion', 'N/A')}",
    #     getattr(perfil, 'universidad', 'UNIVERSIDAD').upper(),
    #     getattr(perfil, 'especialidades', terapia.nombre).upper(),
    #     f"T.P. {getattr(profesional, 'cedula_profesional', 'N/A')}"
    # ]
    
    # Generar PDF
    doc.build(story, onFirstPage=agregar_encabezado_pie, onLaterPages=agregar_encabezado_pie)
    
    buffer.seek(0)
    
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Informe_{paciente.nombre_completo}_{mes}_{anio}.pdf"'
    
    return response


def calcular_edad(fecha_nacimiento):
    """Calcula edad en años"""
    hoy = date.today()
    return hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))


def informe_mensual_form(request):
    """Formulario para informe mensual"""
    
    # Debug: imprimir valores
    terapias = Terapia.objects.filter(activo=True)
    profesionales = Usuario.objects.filter(
        rol__in=['TERAPEUTA', 'PSICOLOGO', 'MEDICO'],
        is_active=True
    )
    
    print(f"Terapias encontradas: {terapias.count()}")
    print(f"Profesionales encontrados: {profesionales.count()}")
    
    context = {
        'pacientes': Paciente.objects.filter(estado = 'ACTIVO'),
        'terapias': terapias,
        'profesionales': profesionales,
        'meses': [
            (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), 
            (4, 'Abril'), (5, 'Mayo'), (6, 'Junio'),
            (7, 'Julio'), (8, 'Agosto'), (9, 'Septiembre'), 
            (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
        ],
        'anios': range(2020, timezone.now().year + 2),
        'mes_actual': timezone.now().month,
        'anio_actual': timezone.now().year,
    }
    
    return render(request, 'reportes/informe_mensual_paciente_form.html', context)





