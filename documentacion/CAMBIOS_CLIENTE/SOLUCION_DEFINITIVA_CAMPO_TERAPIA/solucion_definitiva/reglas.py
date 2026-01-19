"""
Motor de Reglas - Filtros Duros
Aplica reglas de negocio para filtrar grupos incompatibles
"""

from django.db.models import Count, Q


class FiltrosReglas:
    """
    Aplica filtros duros para descartar grupos incompatibles
    """
    
    def aplicar_filtros(self, grupos, paciente, valoraciones=None):
        """
        Filtra grupos según reglas de negocio - ACTUALIZADO
        
        Args:
            grupos: QuerySet de GrupoTerapeutico
            paciente: Instancia de Paciente
            valoraciones: QuerySet de ValoracionProfesional (ACTUALIZADO - plural)
            
        Returns:
            Lista de grupos que pasan todos los filtros
        """
        candidatos = []
        
        for grupo in grupos:
            # FILTRO 1: Edad compatible
            if not self._edad_compatible(paciente, grupo):
                continue
            
            # FILTRO 2: Estado activo y con cupo o lista de espera
            if not self._grupo_disponible(grupo):
                continue
            
            # FILTRO 3: Nivel de funcionamiento (si hay valoraciones)
            # ✅ CAMBIO: Buscar valoración de la terapia específica del grupo
            if valoraciones:
                valoracion_grupo = valoraciones.filter(terapia=grupo.terapia).first()
                if valoracion_grupo and not self._nivel_compatible(valoracion_grupo, grupo):
                    continue
            
            # Grupo pasó todos los filtros
            candidatos.append(grupo)
        
        return candidatos
    
    def _edad_compatible(self, paciente, grupo):
        """
        Verifica si la edad del paciente está en el rango del grupo
        Permite un margen de ±1 año fuera del rango
        """
        if paciente.edad_actual is None:
            return False
        edad = paciente.edad_actual
        edad_min = grupo.edad_minima - 1  # Margen inferior
        edad_max = grupo.edad_maxima + 1  # Margen superior
        
        return edad_min <= edad <= edad_max
    
    def _grupo_disponible(self, grupo):
        """
        Verifica si el grupo está disponible (activo y con cupo o lista)
        """
        # Grupo debe estar activo
        if not grupo.activo:
            return False
        
        # Acepta grupos con cupo o que acepten lista de espera
        tiene_cupo = grupo.cupos_disponibles > 0
        acepta_lista = hasattr(grupo, 'acepta_lista_espera') and grupo.acepta_lista_espera
        
        return tiene_cupo or acepta_lista
    
    def _nivel_compatible(self, valoracion, grupo):
        """
        Verifica compatibilidad de nivel de funcionamiento
        Permite diferencia de máximo 1 nivel
        """
        # Si el grupo no tiene nivel definido, aceptar
        if not hasattr(grupo, 'nivel_funcionamiento') or grupo.nivel_funcionamiento is None:
            return True
        
        # Si la valoración no tiene nivel, aceptar
        if not hasattr(valoracion, 'nivel_funcionamiento') or valoracion.nivel_funcionamiento is None:
            return True
        
        # Mapeo de niveles (ajustar según tu modelo)
        niveles_map = {
            'LEVE': 1,
            'MODERADO': 2,
            'SEVERO': 3,
            'PROFUNDO': 4
        }
        
        nivel_paciente = niveles_map.get(valoracion.nivel_funcionamiento, 2)
        nivel_grupo = niveles_map.get(grupo.nivel_funcionamiento, 2)
        
        # Permitir diferencia de máximo 1 nivel
        return abs(nivel_paciente - nivel_grupo) <= 1
    
    def _terapia_compatible(self, valoracion, grupo):
        """
        Verifica si el tipo de terapia del grupo es adecuado
        (Para implementar si tienes campo terapias_requeridas en valoración)
        """
        # Si no hay especificación de terapias requeridas, aceptar cualquiera
        if not hasattr(valoracion, 'terapias_requeridas'):
            return True
        
        # Si la valoración especifica terapias, verificar
        if valoracion.terapias_requeridas:
            return grupo.terapia in valoracion.terapias_requeridas
        
        return True
