"""
Funciones auxiliares para gestión de grupos y asignaciones.
"""
from django.db.models import Q, Count
from django.utils import timezone
from .models import GrupoTerapeutico, AsignacionGrupo, PacientePendiente


def verificar_cupo_disponible(grupo, dias_solicitados):
    """
    Verifica si un grupo tiene cupo disponible para los días solicitados.
    
    Args:
        grupo: Instancia de GrupoTerapeutico
        dias_solicitados: Lista de días (ej: ['L', 'M', 'X'])
    
    Returns:
        tuple: (bool, str) - (tiene_cupo, mensaje)
    """
    if not grupo.activo:
        return False, "El grupo no está activo"
    
    if not grupo.tiene_cupo:
        return False, f"El grupo está lleno (capacidad: {grupo.capacidad_maxima})"
    
    if not grupo.puede_asignar_dias(dias_solicitados):
        return False, f"Los días solicitados no están disponibles. Días del grupo: {grupo.dias_disponibles}"
    
    return True, "Cupo disponible"


def asignar_paciente_a_grupo(paciente, grupo, dias_asistencia, numero_terapias, notas=''):
    """
    Asigna un paciente a un grupo terapéutico.
    
    Args:
        paciente: Instancia de Paciente
        grupo: Instancia de GrupoTerapeutico
        dias_asistencia: Lista de días (ej: ['L', 'M', 'X'])
        numero_terapias: Número de terapias semanales
        notas: Notas adicionales (opcional)
    
    Returns:
        tuple: (AsignacionGrupo|None, bool, str) - (asignacion, exito, mensaje)
    """
    # Verificar cupo
    tiene_cupo, mensaje = verificar_cupo_disponible(grupo, dias_asistencia)
    if not tiene_cupo:
        return None, False, mensaje
    
    # Verificar si ya tiene asignación activa al mismo grupo
    asignacion_existente = AsignacionGrupo.objects.filter(
        paciente=paciente,
        grupo=grupo,
        estado='ACTIVA'
    ).first()
    
    if asignacion_existente:
        return asignacion_existente, False, "El paciente ya está asignado a este grupo"
    
    try:
        # Crear asignación
        asignacion = AsignacionGrupo.objects.create(
            paciente=paciente,
            grupo=grupo,
            dias_asistencia=dias_asistencia,
            numero_terapias_semanales=numero_terapias,
            fecha_inicio_asignacion=timezone.now().date(),
            estado='ACTIVA',
            notas=notas
        )
        
        # Si el paciente estaba pendiente, marcarlo como asignado
        pendientes = PacientePendiente.objects.filter(
            paciente=paciente,
            estado='PENDIENTE'
        )
        for pendiente in pendientes:
            pendiente.marcar_como_asignado(grupo)
        
        return asignacion, True, f"Paciente asignado exitosamente al {grupo.nombre}"
    
    except Exception as e:
        return None, False, f"Error al asignar paciente: {str(e)}"


def marcar_paciente_pendiente(paciente, preferencia_horario, dias_preferidos, prioridad='MEDIA', observaciones=''):
    """
    Marca un paciente como pendiente de asignación.
    
    Args:
        paciente: Instancia de Paciente
        preferencia_horario: time object con hora preferida
        dias_preferidos: Lista de días preferidos
        prioridad: 'ALTA', 'MEDIA' o 'BAJA'
        observaciones: Texto adicional
    
    Returns:
        tuple: (PacientePendiente, bool, str)
    """
    # Verificar si ya está pendiente
    pendiente_existente = PacientePendiente.objects.filter(
        paciente=paciente,
        estado='PENDIENTE'
    ).first()
    
    if pendiente_existente:
        return pendiente_existente, False, "El paciente ya está en lista de espera"
    
    try:
        pendiente = PacientePendiente.objects.create(
            paciente=paciente,
            preferencia_horario=preferencia_horario,
            dias_preferidos=dias_preferidos,
            prioridad=prioridad,
            estado='PENDIENTE',
            observaciones=observaciones
        )
        return pendiente, True, "Paciente marcado como pendiente"
    
    except Exception as e:
        return None, False, f"Error al marcar como pendiente: {str(e)}"


def buscar_grupo_disponible(dias_preferidos, hora_preferida=None, capacidad_minima=1):
    """
    Busca grupos disponibles que cumplan con los criterios.
    
    Args:
        dias_preferidos: Lista de días requeridos
        hora_preferida: time object (opcional)
        capacidad_minima: Cupos mínimos disponibles
    
    Returns:
        QuerySet de GrupoTerapeutico
    """
    grupos = GrupoTerapeutico.objects.filter(
        activo=True,
        pacientes_actuales__lt=models.F('capacidad_maxima')
    )
    
    # Filtrar por hora si se especifica
    if hora_preferida:
        grupos = grupos.filter(
            hora_inicio__lte=hora_preferida,
            hora_fin__gte=hora_preferida
        )
    
    # Filtrar grupos que tengan todos los días requeridos
    grupos_validos = []
    for grupo in grupos:
        if all(dia in grupo.dias_disponibles for dia in dias_preferidos):
            if grupo.cupos_disponibles >= capacidad_minima:
                grupos_validos.append(grupo.pk)
    
    return GrupoTerapeutico.objects.filter(pk__in=grupos_validos)


def calcular_ocupacion_grupo(grupo):
    """
    Calcula estadísticas de ocupación de un grupo.
    
    Returns:
        dict con estadísticas
    """
    total = grupo.capacidad_maxima
    actuales = grupo.pacientes_actuales
    disponibles = grupo.cupos_disponibles
    porcentaje = grupo.porcentaje_ocupacion
    
    return {
        'capacidad_total': total,
        'pacientes_actuales': actuales,
        'cupos_disponibles': disponibles,
        'porcentaje_ocupacion': porcentaje,
        'esta_lleno': grupo.esta_lleno,
        'tiene_cupo': grupo.tiene_cupo,
    }


def liberar_cupo_paciente(paciente, grupo=None, motivo=''):
    """
    Libera el cupo de un paciente en un grupo.
    
    Args:
        paciente: Instancia de Paciente
        grupo: GrupoTerapeutico específico (opcional, None = todos)
        motivo: Razón de la liberación
    
    Returns:
        tuple: (int, bool, str) - (cantidad_liberada, exito, mensaje)
    """
    query = AsignacionGrupo.objects.filter(
        paciente=paciente,
        estado='ACTIVA'
    )
    
    if grupo:
        query = query.filter(grupo=grupo)
    
    asignaciones = query.all()
    cantidad = len(asignaciones)
    
    if cantidad == 0:
        return 0, False, "No hay asignaciones activas para liberar"
    
    for asignacion in asignaciones:
        asignacion.finalizar(motivo=motivo)
    
    return cantidad, True, f"Se liberaron {cantidad} asignación(es)"


def obtener_pacientes_sin_grupo():
    """
    Obtiene todos los pacientes que no tienen grupo asignado.
    
    Returns:
        QuerySet de Paciente
    """
    from apps.procedimientos.models import Paciente
    
    return Paciente.objects.filter(
        Q(tiene_grupo_asignado=False) | 
        Q(estado_asignacion='EN_ESPERA')
    ).filter(
        estado='ACTIVO'
    )


def obtener_estadisticas_grupos():
    """
    Genera estadísticas generales de los grupos.
    
    Returns:
        dict con estadísticas
    """
    grupos_activos = GrupoTerapeutico.objects.filter(activo=True)
    
    total_grupos = grupos_activos.count()
    total_capacidad = sum(g.capacidad_maxima for g in grupos_activos)
    total_pacientes = sum(g.pacientes_actuales for g in grupos_activos)
    total_cupos_disponibles = sum(g.cupos_disponibles for g in grupos_activos)
    
    ocupacion_promedio = (total_pacientes / total_capacidad * 100) if total_capacidad > 0 else 0
    
    grupos_llenos = grupos_activos.filter(
        pacientes_actuales__gte=models.F('capacidad_maxima')
    ).count()
    
    pendientes = PacientePendiente.objects.filter(estado='PENDIENTE').count()
    
    return {
        'total_grupos': total_grupos,
        'total_capacidad': total_capacidad,
        'total_pacientes': total_pacientes,
        'total_cupos_disponibles': total_cupos_disponibles,
        'ocupacion_promedio': round(ocupacion_promedio, 2),
        'grupos_llenos': grupos_llenos,
        'pacientes_pendientes': pendientes,
    }


def reasignar_paciente(paciente, grupo_origen, grupo_destino, dias_asistencia, numero_terapias, motivo=''):
    """
    Reasigna un paciente de un grupo a otro.
    
    Returns:
        tuple: (AsignacionGrupo|None, bool, str)
    """
    # Verificar cupo en destino
    tiene_cupo, mensaje = verificar_cupo_disponible(grupo_destino, dias_asistencia)
    if not tiene_cupo:
        return None, False, mensaje
    
    # Finalizar asignación actual
    asignacion_origen = AsignacionGrupo.objects.filter(
        paciente=paciente,
        grupo=grupo_origen,
        estado='ACTIVA'
    ).first()
    
    if asignacion_origen:
        asignacion_origen.finalizar(motivo=f"Reasignación: {motivo}")
    
    # Crear nueva asignación
    return asignar_paciente_a_grupo(
        paciente=paciente,
        grupo=grupo_destino,
        dias_asistencia=dias_asistencia,
        numero_terapias=numero_terapias,
        notas=f"Reasignado desde {grupo_origen.nombre}. Motivo: {motivo}"
    )


from django.db import models
