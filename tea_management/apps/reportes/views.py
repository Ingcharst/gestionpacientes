"""
Vistas para el módulo de reportes.
"""
from datetime import datetime, timedelta
from calendar import monthrange
from decimal import Decimal

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone

from apps.procedimientos.models import (
    Paciente, Procedimiento, SesionTerapeutica,
    ObjetivoTerapeutico, EvolucionPaciente
)
from apps.grupos.models import GrupoTerapeutico, AsignacionGrupo
from apps.terapias.models import Terapia
from apps.usuarios.models import Usuario

from .utils import (
    ReportePDFGenerator, ReporteExcelGenerator,
    calcular_totales_procedimientos, calcular_totales_sesiones,
    formato_moneda, obtener_nombre_mes
)



@login_required
def reportes_dashboard(request):
    """Dashboard principal de reportes."""
    context = {
        'total_pacientes': Paciente.objects.filter(estado='ACTIVO').count(),
        'total_terapeutas': Usuario.objects.filter(rol='TERAPEUTA').count(),
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
