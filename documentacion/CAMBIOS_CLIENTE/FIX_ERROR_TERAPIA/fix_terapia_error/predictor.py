"""
Grupo Recomendador - VERSIÓN SIN FILTRO DE TERAPIA
Sistema de recomendación adaptado para grupos sin campo FK a Terapia
"""

from .reglas import FiltrosReglas
from .features import FeatureExtractor
from .scoring import ScoreCalculator


class GrupoRecomendador:
    """
    Sistema de recomendación de grupos terapéuticos
    VERSIÓN SIMPLIFICADA: No filtra por terapia específica
    """
    
    def __init__(self):
        self.filtros = FiltrosReglas()
        self.feature_extractor = FeatureExtractor()
        self.score_calculator = ScoreCalculator()
    
    def recomendar_grupos(self, paciente, grupos_disponibles=None, valoraciones=None, top_n=5):
        """
        Recomienda grupos para un paciente
        VERSIÓN SIN FILTRO DE TERAPIA
        """
        # PASO 1: Obtener valoraciones si no se pasan
        if valoraciones is None:
            from apps.procedimientos.models import ValoracionProfesional
            valoraciones = ValoracionProfesional.objects.filter(
                paciente=paciente
            ).select_related('terapia', 'terapeuta')
        
        # PASO 2: Verificar que existan valoraciones
        if not valoraciones.exists():
            return {
                'recomendaciones': [],
                'mensaje': 'El paciente no tiene valoraciones registradas. Debe completar al menos una valoración.',
                'total_grupos_evaluados': 0,
                'grupos_filtrados': 0,
                'error': True
            }
        
        # PASO 3: Obtener grupos disponibles (TODOS, sin filtrar por terapia)
        if grupos_disponibles is None:
            from apps.grupos.models import GrupoTerapeutico
            grupos_disponibles = GrupoTerapeutico.objects.filter(activo=True)
        
        if not grupos_disponibles.exists():
            return {
                'recomendaciones': [],
                'mensaje': 'No hay grupos activos disponibles',
                'total_grupos_evaluados': 0,
                'grupos_filtrados': 0
            }
        
        # PASO 4: Aplicar filtros duros
        grupos_candidatos = self.filtros.aplicar_filtros(
            grupos_disponibles, 
            paciente, 
            valoraciones=valoraciones
        )
        
        if not grupos_candidatos:
            return {
                'recomendaciones': [],
                'mensaje': 'No se encontraron grupos compatibles después de aplicar filtros',
                'total_grupos_evaluados': grupos_disponibles.count(),
                'grupos_filtrados': 0
            }
        
        # PASO 5: Calcular scores para cada candidato
        recomendaciones = []
        
        for grupo in grupos_candidatos:
            # Usar la primera valoración disponible
            # (No podemos filtrar por terapia si el grupo no tiene ese campo)
            valoracion_grupo = valoraciones.first()
            
            # Extraer features
            features = self.feature_extractor.extraer_features(
                paciente, 
                grupo, 
                valoracion=valoracion_grupo,
                valoraciones_todas=valoraciones
            )
            
            # Calcular score
            score_final = self.score_calculator.calcular_score(grupo, features)
            
            # Generar explicación
            razones = self._generar_explicacion(features, score_final)
            
            # Generar alertas
            alertas = self._generar_alertas(grupo, paciente, features)
            
            # Crear recomendación
            recomendacion = {
                'grupo': grupo,
                'score': score_final,
                'disponible': grupo.cupos_disponibles > 0,
                'cupos': grupo.cupos_disponibles,
                'razones': razones,
                'alertas': alertas,
                'features': features,
                'valoracion_usada': valoracion_grupo,
            }
            
            recomendaciones.append(recomendacion)
        
        # PASO 6: Ordenar por score descendente
        recomendaciones.sort(key=lambda x: x['score'], reverse=True)
        
        # PASO 7: Retornar top N
        return {
            'recomendaciones': recomendaciones[:top_n],
            'mensaje': f'Se encontraron {len(recomendaciones)} grupos compatibles',
            'total_grupos_evaluados': grupos_disponibles.count(),
            'grupos_filtrados': len(grupos_candidatos),
            'paciente': {
                'nombre': paciente.nombre_completo,
                'edad': paciente.edad_actual,
                'genero': paciente.genero
            },
            'valoraciones_count': valoraciones.count(),
        }
    
    def _generar_explicacion(self, features, score):
        """Genera explicación legible"""
        razones = []
        
        edad_score = features.get('edad_match_score', 0)
        if edad_score >= 95:
            razones.append("✓ Edad perfectamente compatible con el grupo")
        elif edad_score >= 80:
            razones.append("✓ Edad muy compatible con el grupo")
        elif edad_score >= 60:
            razones.append("✓ Edad compatible con el grupo")
        else:
            razones.append("⚠ Edad ligeramente fuera del rango ideal")
        
        nivel_score = features.get('nivel_match_score', 0)
        if nivel_score == 100:
            razones.append("✓ Nivel de funcionamiento ideal para el grupo")
        elif nivel_score >= 70:
            razones.append("✓ Nivel de funcionamiento adecuado")
        elif nivel_score >= 50:
            razones.append("⚠ Nivel de funcionamiento aceptable con supervisión")
        
        cupos = features.get('cupos_disponibles', 0)
        if cupos >= 3:
            razones.append(f"✓ Grupo con buena disponibilidad ({cupos} cupos)")
        elif cupos > 0:
            razones.append(f"✓ Cupo disponible ({cupos} restante{'s' if cupos > 1 else ''})")
        else:
            razones.append("⚠ Sin cupos actuales (lista de espera disponible)")
        
        tasa_exito = features.get('tasa_exito_grupo', 0)
        if tasa_exito >= 80:
            razones.append("✓ Grupo con excelente historial de resultados")
        elif tasa_exito >= 60:
            razones.append("✓ Grupo con buen historial de resultados")
        
        num_valoraciones = features.get('numero_valoraciones', 0)
        if num_valoraciones > 1:
            razones.append(f"✓ Paciente evaluado por {num_valoraciones} especialistas")
        
        if not razones:
            razones.append(f"Grupo compatible con score de {score}%")
        
        return razones
    
    def _generar_alertas(self, grupo, paciente, features):
        """Genera alertas"""
        alertas = []
        
        cupos = features.get('cupos_disponibles', 0)
        if cupos == 0:
            alertas.append({
                'tipo': 'warning',
                'icono': 'bi-exclamation-triangle',
                'mensaje': 'Sin cupos disponibles - Se requiere lista de espera'
            })
        elif cupos <= 2:
            alertas.append({
                'tipo': 'info',
                'icono': 'bi-info-circle',
                'mensaje': f'Solo {cupos} cupo(s) disponible(s)'
            })
        
        diferencia_edad = features.get('diferencia_edad', 0)
        if diferencia_edad > 2:
            alertas.append({
                'tipo': 'warning',
                'icono': 'bi-calendar-x',
                'mensaje': f'Diferencia de edad significativa ({diferencia_edad:.1f} años)'
            })
        
        nivel_score = features.get('nivel_match_score', 100)
        if nivel_score < 50:
            alertas.append({
                'tipo': 'warning',
                'icono': 'bi-bar-chart',
                'mensaje': 'Nivel de funcionamiento diferente - Requiere evaluación'
            })
        
        ocupacion = features.get('porcentaje_ocupacion', 0)
        if ocupacion >= 95:
            alertas.append({
                'tipo': 'info',
                'icono': 'bi-people-fill',
                'mensaje': 'Grupo casi lleno - Dinámica grupal establecida'
            })
        
        experiencia = features.get('experiencia_grupo', 0)
        if experiencia < 20:
            alertas.append({
                'tipo': 'info',
                'icono': 'bi-star',
                'mensaje': 'Grupo nuevo - Oportunidad para conformar dinámica'
            })
        
        return alertas
    
    def ajustar_pesos_scoring(self, nuevos_pesos):
        """Permite ajustar pesos del scoring"""
        self.score_calculator.ajustar_pesos(nuevos_pesos)
    
    def obtener_pesos_actuales(self):
        """Retorna pesos actuales"""
        return self.score_calculator.PESOS.copy()
    
    def debug_recomendacion(self, paciente, grupo, valoracion=None):
        """Modo debug"""
        features = self.feature_extractor.extraer_features(
            paciente, grupo, valoracion
        )
        
        score = self.score_calculator.calcular_score(grupo, features)
        explicacion_detallada = self.score_calculator.explicar_score(features)
        
        return {
            'grupo': {
                'id': grupo.id,
                'nombre': grupo.nombre,
                'cupos': grupo.cupos_disponibles
            },
            'paciente': {
                'nombre': paciente.nombre_completo,
                'edad': paciente.edad_actual,
                'genero': paciente.genero
            },
            'features': features,
            'score_final': score,
            'desglose_score': explicacion_detallada,
            'razones': self._generar_explicacion(features, score),
            'alertas': self._generar_alertas(grupo, paciente, features)
        }
