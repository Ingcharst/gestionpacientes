"""
Feature Extractor - Extrae características para scoring
Calcula métricas de compatibilidad entre paciente y grupo
"""

from django.db.models import Avg, Count
from datetime import datetime


class FeatureExtractor:
    """
    Extrae features (características) para calcular compatibilidad
    """
    
    def extraer_features(self, paciente, grupo, valoracion=None):
        """
        Extrae todas las features necesarias para scoring
        
        Args:
            paciente: Instancia de Paciente
            grupo: Instancia de GrupoTerapeutico
            valoracion: Instancia de Valoracion (opcional)
            
        Returns:
            Dict con features calculadas
        """
        features = {
            # Features de edad
            'edad_paciente': paciente.edad,
            'edad_minima_grupo': grupo.edad_minima,
            'edad_maxima_grupo': grupo.edad_maxima,
            'edad_match_score': self._calcular_edad_match(paciente, grupo),
            'diferencia_edad': self._calcular_diferencia_edad(paciente, grupo),
            
            # Features de disponibilidad
            'cupos_disponibles': grupo.cupos_disponibles,
            'capacidad_total': grupo.capacidad_maxima,
            'porcentaje_ocupacion': self._calcular_ocupacion(grupo),
            'disponibilidad_score': self._calcular_disponibilidad_score(grupo),
            
            # Features de grupo
            'tasa_exito_grupo': self._calcular_tasa_exito(grupo),
            'experiencia_grupo': self._calcular_experiencia_grupo(grupo),
            'balance_genero': self._calcular_balance_genero(grupo, paciente),
        }
        
        # Features adicionales si hay valoración
        if valoracion:
            features.update({
                'nivel_match_score': self._calcular_nivel_match(valoracion, grupo),
                'areas_overlap_score': self._calcular_areas_overlap(valoracion, grupo),
            })
        
        return features
    
    def _calcular_edad_match(self, paciente, grupo):
        """
        Calcula qué tan bien la edad del paciente se ajusta al grupo
        100% = edad en el centro del rango
        Disminuye hacia los extremos
        """
        edad = paciente.edad
        edad_min = grupo.edad_minima
        edad_max = grupo.edad_maxima
        edad_centro = (edad_min + edad_max) / 2
        rango = edad_max - edad_min
        
        # Si está fuera del rango
        if edad < edad_min - 1:
            return max(0, 100 - (edad_min - edad) * 20)
        elif edad > edad_max + 1:
            return max(0, 100 - (edad - edad_max) * 20)
        
        # Si está dentro del rango
        if rango == 0:
            return 100 if edad == edad_centro else 80
        
        # Calcular distancia al centro (0 = centro, 1 = extremo)
        distancia_normalizada = abs(edad - edad_centro) / (rango / 2)
        
        # Score: 100% en el centro, decrece hacia extremos
        score = 100 * (1 - distancia_normalizada * 0.3)
        
        return max(0, min(100, score))
    
    def _calcular_diferencia_edad(self, paciente, grupo):
        """
        Calcula la diferencia de edad con el promedio del grupo
        """
        # Obtener edad promedio de pacientes en el grupo
        asignaciones = grupo.asignaciones.filter(estado='ACTIVA')
        
        if not asignaciones.exists():
            # Si el grupo está vacío, usar el centro del rango
            return abs(paciente.edad - (grupo.edad_minima + grupo.edad_maxima) / 2)
        
        edad_promedio = asignaciones.aggregate(
            promedio=Avg('paciente__edad')
        )['promedio']
        
        return abs(paciente.edad - edad_promedio) if edad_promedio else 0
    
    def _calcular_ocupacion(self, grupo):
        """
        Calcula el porcentaje de ocupación del grupo
        """
        if grupo.capacidad_maxima == 0:
            return 0
        
        ocupados = grupo.capacidad_maxima - grupo.cupos_disponibles
        return (ocupados / grupo.capacidad_maxima) * 100
    
    def _calcular_disponibilidad_score(self, grupo):
        """
        Score basado en disponibilidad
        100% = tiene cupos disponibles
        50% = lleno pero acepta lista de espera
        0% = no disponible
        """
        if grupo.cupos_disponibles > 0:
            # Bonus si tiene varios cupos
            if grupo.cupos_disponibles >= 3:
                return 100
            else:
                return 85  # Pocos cupos pero disponibles
        
        # Sin cupos
        if hasattr(grupo, 'acepta_lista_espera') and grupo.acepta_lista_espera:
            return 50  # Lista de espera
        
        return 0  # No disponible
    
    def _calcular_tasa_exito(self, grupo):
        """
        Calcula tasa de éxito basada en asignaciones históricas
        Éxito = permanencia >6 meses
        """
        from datetime import timedelta
        from django.utils import timezone
        
        asignaciones = grupo.asignaciones.all()
        
        if not asignaciones.exists():
            return 50  # Valor neutro para grupos nuevos
        
        exitosas = 0
        total_evaluables = 0
        
        for asignacion in asignaciones:
            # Solo evaluar asignaciones con al menos 6 meses
            if asignacion.fecha_inicio:
                fecha_limite = timezone.now().date() - timedelta(days=180)
                
                if asignacion.fecha_inicio <= fecha_limite:
                    total_evaluables += 1
                    
                    # Considerar exitosa si sigue activa o duró >6 meses
                    if asignacion.estado == 'ACTIVA':
                        exitosas += 1
                    elif asignacion.estado == 'FINALIZADA' and asignacion.fecha_fin:
                        dias = (asignacion.fecha_fin - asignacion.fecha_inicio).days
                        if dias >= 180:
                            exitosas += 1
        
        if total_evaluables == 0:
            return 50  # Valor neutro
        
        return (exitosas / total_evaluables) * 100
    
    def _calcular_experiencia_grupo(self, grupo):
        """
        Calcula la experiencia del grupo (cuánto tiempo lleva activo)
        """
        if not grupo.fecha_inicio:
            return 0
        
        from django.utils import timezone
        dias_activo = (timezone.now().date() - grupo.fecha_inicio).days
        meses = dias_activo / 30
        
        # Score basado en meses (máximo 100 a los 12 meses)
        return min(100, (meses / 12) * 100)
    
    def _calcular_balance_genero(self, grupo, paciente):
        """
        Calcula si agregar este paciente mejora el balance de género
        """
        asignaciones = grupo.asignaciones.filter(estado='ACTIVA')
        
        if not asignaciones.exists():
            return 100  # Grupo vacío, cualquier género está bien
        
        # Contar por género
        total = asignaciones.count()
        masculinos = asignaciones.filter(paciente__genero='M').count()
        femeninos = asignaciones.filter(paciente__genero='F').count()
        
        # Calcular balance actual
        if total == 0:
            balance_actual = 50
        else:
            balance_actual = min(masculinos, femeninos) / total * 100
        
        # Simular balance después de agregar este paciente
        if paciente.genero == 'M':
            masculinos_nuevo = masculinos + 1
            femeninos_nuevo = femeninos
        else:
            masculinos_nuevo = masculinos
            femeninos_nuevo = femeninos + 1
        
        total_nuevo = total + 1
        balance_nuevo = min(masculinos_nuevo, femeninos_nuevo) / total_nuevo * 100
        
        # Si mejora el balance, bonus
        if balance_nuevo >= balance_actual:
            return 100
        else:
            return 80  # Empeora ligeramente, pero aceptable
    
    def _calcular_nivel_match(self, valoracion, grupo):
        """
        Score de compatibilidad de nivel de funcionamiento
        """
        # Si alguno no tiene nivel definido, retornar neutro
        if not hasattr(grupo, 'nivel_funcionamiento') or grupo.nivel_funcionamiento is None:
            return 75
        if not hasattr(valoracion, 'nivel_funcionamiento') or valoracion.nivel_funcionamiento is None:
            return 75
        
        # Mapeo de niveles
        niveles_map = {
            'LEVE': 1,
            'MODERADO': 2,
            'SEVERO': 3,
            'PROFUNDO': 4
        }
        
        nivel_paciente = niveles_map.get(valoracion.nivel_funcionamiento, 2)
        nivel_grupo = niveles_map.get(grupo.nivel_funcionamiento, 2)
        
        diferencia = abs(nivel_paciente - nivel_grupo)
        
        # Score según diferencia
        if diferencia == 0:
            return 100  # Nivel exacto
        elif diferencia == 1:
            return 70   # Diferencia de 1 nivel
        else:
            return 30   # Diferencia mayor
    
    def _calcular_areas_overlap(self, valoracion, grupo):
        """
        Calcula el overlap entre áreas afectadas y áreas de enfoque del grupo
        (Implementar según estructura de tu modelo)
        """
        # Si no hay información de áreas, retornar neutro
        if not hasattr(valoracion, 'areas_afectadas') or not valoracion.areas_afectadas:
            return 75
        
        if not hasattr(grupo, 'areas_enfoque') or not grupo.areas_enfoque:
            return 75
        
        # Convertir a sets para calcular overlap
        try:
            # Si son strings separados por comas
            areas_paciente = set([a.strip().lower() for a in valoracion.areas_afectadas.split(',')])
            areas_grupo = set([a.strip().lower() for a in grupo.areas_enfoque.split(',')])
            
            if not areas_paciente:
                return 75
            
            # Calcular overlap
            overlap = len(areas_paciente & areas_grupo)
            total = len(areas_paciente)
            
            return (overlap / total) * 100 if total > 0 else 50
        
        except:
            return 75  # En caso de error, retornar neutro
