"""
Grupo Recomendador - Motor Principal
Sistema de recomendación basado en reglas para asignación de grupos
"""

from .reglas import FiltrosReglas
from .features import FeatureExtractor
from .scoring import ScoreCalculator


class GrupoRecomendador:
    """
    Sistema de recomendación de grupos terapéuticos
    MVP - Basado en reglas (sin ML)
    """
    
    def __init__(self):
        self.filtros = FiltrosReglas()
        self.feature_extractor = FeatureExtractor()
        self.score_calculator = ScoreCalculator()
    
    def recomendar_grupos(self, paciente, grupos_disponibles=None, valoracion=None, top_n=5):
        """
        Recomienda grupos para un paciente
        
        Args:
            paciente: Instancia de Paciente
            grupos_disponibles: QuerySet de GrupoTerapeutico (opcional)
            valoracion: Instancia de Valoracion (opcional)
            top_n: Número de recomendaciones a retornar
            
        Returns:
            Dict con recomendaciones y mensaje
        """
        # PASO 1: Obtener grupos disponibles
        if grupos_disponibles is None:
            from apps.grupos.models import GrupoTerapeutico
            grupos_disponibles = GrupoTerapeutico.objects.filter(estado='ACTIVO')
        
        # PASO 2: Aplicar filtros duros
        grupos_candidatos = self.filtros.aplicar_filtros(
            grupos_disponibles, 
            paciente, 
            valoracion
        )
        
        if not grupos_candidatos:
            return {
                'recomendaciones': [],
                'mensaje': 'No se encontraron grupos compatibles. Considere crear un nuevo grupo o ajustar los criterios.',
                'total_grupos_evaluados': grupos_disponibles.count(),
                'grupos_filtrados': 0
            }
        
        # PASO 3: Calcular scores para cada candidato
        recomendaciones = []
        
        for grupo in grupos_candidatos:
            # Extraer features
            features = self.feature_extractor.extraer_features(
                paciente, 
                grupo, 
                valoracion
            )
            
            # Calcular score
            score_final = self.score_calculator.calcular_score(
                grupo, 
                features
            )
            
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
                'features': features,  # Para debugging
            }
            
            recomendaciones.append(recomendacion)
        
        # PASO 4: Ordenar por score descendente
        recomendaciones.sort(key=lambda x: x['score'], reverse=True)
        
        # PASO 5: Retornar top N
        return {
            'recomendaciones': recomendaciones[:top_n],
            'mensaje': f'Se encontraron {len(recomendaciones)} grupos compatibles',
            'total_grupos_evaluados': grupos_disponibles.count(),
            'grupos_filtrados': len(grupos_candidatos),
            'paciente': {
                'nombre': paciente.nombre_completo,
                'edad': paciente.edad,
                'genero': paciente.genero
            }
        }
    
    def _generar_explicacion(self, features, score):
        """
        Genera explicación legible de por qué el grupo es compatible
        
        Args:
            features: Dict con features calculadas
            score: Score final
            
        Returns:
            Lista de strings con razones
        """
        razones = []
        
        # Explicación de edad
        edad_score = features.get('edad_match_score', 0)
        if edad_score >= 95:
            razones.append("✓ Edad perfectamente compatible con el grupo")
        elif edad_score >= 80:
            razones.append("✓ Edad muy compatible con el grupo")
        elif edad_score >= 60:
            razones.append("✓ Edad compatible con el grupo")
        else:
            razones.append("⚠ Edad ligeramente fuera del rango ideal")
        
        # Explicación de nivel
        nivel_score = features.get('nivel_match_score', 0)
        if nivel_score == 100:
            razones.append("✓ Nivel de funcionamiento ideal para el grupo")
        elif nivel_score >= 70:
            razones.append("✓ Nivel de funcionamiento adecuado")
        elif nivel_score >= 50:
            razones.append("⚠ Nivel de funcionamiento aceptable con supervisión")
        
        # Explicación de disponibilidad
        cupos = features.get('cupos_disponibles', 0)
        if cupos >= 3:
            razones.append(f"✓ Grupo con buena disponibilidad ({cupos} cupos)")
        elif cupos > 0:
            razones.append(f"✓ Cupo disponible ({cupos} restante{'s' if cupos > 1 else ''})")
        else:
            razones.append("⚠ Sin cupos actuales (lista de espera disponible)")
        
        # Explicación de tasa de éxito
        tasa_exito = features.get('tasa_exito_grupo', 0)
        if tasa_exito >= 80:
            razones.append("✓ Grupo con excelente historial de resultados")
        elif tasa_exito >= 60:
            razones.append("✓ Grupo con buen historial de resultados")
        elif tasa_exito < 40 and tasa_exito != 50:  # 50 = neutro
            razones.append("⚠ Grupo con historial limitado")
        
        # Explicación de áreas
        areas_score = features.get('areas_overlap_score', 0)
        if areas_score >= 80:
            razones.append("✓ Excelente alineación con áreas terapéuticas necesarias")
        elif areas_score >= 60:
            razones.append("✓ Buena alineación con áreas terapéuticas")
        
        # Explicación de experiencia del grupo
        experiencia = features.get('experiencia_grupo', 0)
        if experiencia >= 80:
            razones.append("✓ Grupo establecido con amplia trayectoria")
        elif experiencia >= 40:
            razones.append("✓ Grupo con experiencia moderada")
        
        # Si no hay razones, agregar al menos una genérica
        if not razones:
            razones.append(f"Grupo compatible con score de {score}%")
        
        return razones
    
    def _generar_alertas(self, grupo, paciente, features):
        """
        Genera alertas o consideraciones especiales
        
        Args:
            grupo: Instancia de GrupoTerapeutico
            paciente: Instancia de Paciente
            features: Dict con features calculadas
            
        Returns:
            Lista de dicts con alertas
        """
        alertas = []
        
        # Alerta de cupos
        cupos = features.get('cupos_disponibles', 0)
        if cupos == 0:
            alertas.append({
                'tipo': 'warning',
                'icono': 'bi-exclamation-triangle',
                'mensaje': 'Sin cupos disponibles - Se requiere lista de espera'
            })
        elif cupos == 1:
            alertas.append({
                'tipo': 'info',
                'icono': 'bi-info-circle',
                'mensaje': 'Último cupo disponible - Asignar pronto'
            })
        elif cupos == 2:
            alertas.append({
                'tipo': 'info',
                'icono': 'bi-info-circle',
                'mensaje': 'Solo 2 cupos disponibles'
            })
        
        # Alerta de edad
        diferencia_edad = features.get('diferencia_edad', 0)
        if diferencia_edad > 2:
            alertas.append({
                'tipo': 'warning',
                'icono': 'bi-calendar-x',
                'mensaje': f'Diferencia de edad significativa con el promedio del grupo ({diferencia_edad:.1f} años)'
            })
        
        # Alerta de nivel
        nivel_score = features.get('nivel_match_score', 100)
        if nivel_score < 50:
            alertas.append({
                'tipo': 'warning',
                'icono': 'bi-bar-chart',
                'mensaje': 'Nivel de funcionamiento diferente - Requiere evaluación del terapeuta'
            })
        
        # Alerta de ocupación
        ocupacion = features.get('porcentaje_ocupacion', 0)
        if ocupacion >= 95:
            alertas.append({
                'tipo': 'info',
                'icono': 'bi-people-fill',
                'mensaje': 'Grupo casi lleno - Dinámica grupal bien establecida'
            })
        elif ocupacion < 30 and grupo.cupos_disponibles > 0:
            alertas.append({
                'tipo': 'success',
                'icono': 'bi-people',
                'mensaje': 'Grupo con buen espacio - Oportunidad para integración gradual'
            })
        
        # Alerta de grupo nuevo
        experiencia = features.get('experiencia_grupo', 0)
        if experiencia < 20:
            alertas.append({
                'tipo': 'info',
                'icono': 'bi-star',
                'mensaje': 'Grupo nuevo - Excelente oportunidad para conformar dinámica'
            })
        
        return alertas
    
    def ajustar_pesos_scoring(self, nuevos_pesos):
        """
        Permite ajustar los pesos del scoring
        
        Args:
            nuevos_pesos: Dict con nuevos valores
            
        Example:
            recomendador.ajustar_pesos_scoring({
                'edad': 0.40,
                'disponibilidad': 0.30
            })
        """
        self.score_calculator.ajustar_pesos(nuevos_pesos)
    
    def obtener_pesos_actuales(self):
        """
        Retorna los pesos actuales del scoring
        """
        return self.score_calculator.PESOS.copy()
    
    def debug_recomendacion(self, paciente, grupo, valoracion=None):
        """
        Modo debug: muestra detalles completos de una recomendación
        
        Args:
            paciente: Instancia de Paciente
            grupo: Instancia de GrupoTerapeutico
            valoracion: Instancia de Valoracion
            
        Returns:
            Dict con todos los detalles
        """
        features = self.feature_extractor.extraer_features(
            paciente, grupo, valoracion
        )
        
        score = self.score_calculator.calcular_score(grupo, features)
        
        explicacion_detallada = self.score_calculator.explicar_score(features)
        
        return {
            'grupo': {
                'id': grupo.id,
                'nombre': grupo.nombre,
                'edad_rango': f"{grupo.edad_minima}-{grupo.edad_maxima}",
                'cupos': grupo.cupos_disponibles
            },
            'paciente': {
                'nombre': paciente.nombre_completo,
                'edad': paciente.edad,
                'genero': paciente.genero
            },
            'features': features,
            'score_final': score,
            'desglose_score': explicacion_detallada,
            'razones': self._generar_explicacion(features, score),
            'alertas': self._generar_alertas(grupo, paciente, features)
        }
