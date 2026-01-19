"""
Score Calculator - Calcula score final de compatibilidad
Combina múltiples features con pesos para obtener score 0-100
"""


class ScoreCalculator:
    """
    Calcula el score final de compatibilidad entre paciente y grupo
    """
    
    # Pesos para cada componente del score (deben sumar 1.0)
    PESOS = {
        'edad': 0.35,              # 35% - Factor más importante
        'disponibilidad': 0.25,    # 25% - Muy importante
        'nivel': 0.15,             # 15% - Importante si hay valoración
        'tasa_exito': 0.10,        # 10% - Historial del grupo
        'balance_genero': 0.05,    # 5% - Consideración secundaria
        'experiencia': 0.05,       # 5% - Madurez del grupo
        'areas': 0.05,             # 5% - Overlap de áreas
    }
    
    def calcular_score(self, grupo, features, score_ml=None):
        """
        Calcula el score final de compatibilidad
        
        Args:
            grupo: Instancia de GrupoTerapeutico
            features: Dict con features extraídas
            score_ml: Score del modelo ML (no usado en MVP)
            
        Returns:
            Float entre 0 y 100
        """
        # Componentes del score
        score_edad = features.get('edad_match_score', 50)
        score_disponibilidad = features.get('disponibilidad_score', 0)
        score_nivel = features.get('nivel_match_score', 75)
        score_tasa_exito = features.get('tasa_exito_grupo', 50)
        score_balance = features.get('balance_genero', 100)
        score_experiencia = features.get('experiencia_grupo', 50)
        score_areas = features.get('areas_overlap_score', 75)
        
        # Calcular score ponderado
        score_final = (
            score_edad * self.PESOS['edad'] +
            score_disponibilidad * self.PESOS['disponibilidad'] +
            score_nivel * self.PESOS['nivel'] +
            score_tasa_exito * self.PESOS['tasa_exito'] +
            score_balance * self.PESOS['balance_genero'] +
            score_experiencia * self.PESOS['experiencia'] +
            score_areas * self.PESOS['areas']
        )
        
        # Aplicar bonificaciones y penalizaciones
        score_final = self._aplicar_ajustes(score_final, grupo, features)
        
        # Asegurar que esté en rango 0-100
        score_final = max(0, min(100, score_final))
        
        return round(score_final, 2)
    
    def _aplicar_ajustes(self, score, grupo, features):
        """
        Aplica ajustes finales al score
        """
        # BONIFICACIÓN: Edad perfecta (+5%)
        if 95 <= features.get('edad_match_score', 0) <= 100:
            score += 5
        
        # BONIFICACIÓN: Grupo con alta tasa de éxito (+3%)
        if features.get('tasa_exito_grupo', 0) >= 85:
            score += 3
        
        # BONIFICACIÓN: Varios cupos disponibles (+2%)
        if features.get('cupos_disponibles', 0) >= 3:
            score += 2
        
        # PENALIZACIÓN: Sin cupos (-10%)
        if features.get('cupos_disponibles', 0) == 0:
            score -= 10
        
        # PENALIZACIÓN: Edad muy fuera de rango (-15%)
        if features.get('diferencia_edad', 0) > 3:
            score -= 15
        
        # PENALIZACIÓN: Grupo casi lleno (-5%)
        if features.get('porcentaje_ocupacion', 0) >= 90:
            score -= 5
        
        return score
    
    def ajustar_pesos(self, nuevos_pesos):
        """
        Permite ajustar los pesos dinámicamente
        
        Args:
            nuevos_pesos: Dict con nuevos valores de pesos
        """
        for key, valor in nuevos_pesos.items():
            if key in self.PESOS:
                self.PESOS[key] = valor
        
        # Normalizar para que sumen 1.0
        total = sum(self.PESOS.values())
        if total != 1.0:
            for key in self.PESOS:
                self.PESOS[key] /= total
    
    def explicar_score(self, features):
        """
        Genera explicación detallada del score
        
        Returns:
            Dict con desglose del score
        """
        return {
            'edad': {
                'score': features.get('edad_match_score', 50),
                'peso': self.PESOS['edad'],
                'contribucion': features.get('edad_match_score', 50) * self.PESOS['edad']
            },
            'disponibilidad': {
                'score': features.get('disponibilidad_score', 0),
                'peso': self.PESOS['disponibilidad'],
                'contribucion': features.get('disponibilidad_score', 0) * self.PESOS['disponibilidad']
            },
            'nivel': {
                'score': features.get('nivel_match_score', 75),
                'peso': self.PESOS['nivel'],
                'contribucion': features.get('nivel_match_score', 75) * self.PESOS['nivel']
            },
            'tasa_exito': {
                'score': features.get('tasa_exito_grupo', 50),
                'peso': self.PESOS['tasa_exito'],
                'contribucion': features.get('tasa_exito_grupo', 50) * self.PESOS['tasa_exito']
            }
        }
