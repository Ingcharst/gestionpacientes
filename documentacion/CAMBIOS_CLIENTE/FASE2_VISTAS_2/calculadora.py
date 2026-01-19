# CREAR: apps/procedimientos/calculadora.py

import math
from datetime import timedelta
from django.utils import timezone


class CalculadoraDistribucion:
    """Calcula distribución de terapias en 4 semanas (20 días hábiles)"""
    
    SEMANAS = 4
    DIAS_HABILES_SEMANA = 5  # Lunes a viernes
    MAX_TERAPIAS_SEMANA = 5
    TOTAL_DIAS_HABILES = 20
    
    def calcular(self, cantidad_terapias):
        """
        Calcula cómo distribuir las terapias
        
        Returns:
            {
                'grupos_necesarios': int,
                'terapias_por_dia': float,
                'distribucion_semanal': list,
                'requiere_multiples_grupos': bool,
                'descripcion': str
            }
        """
        if cantidad_terapias <= 0:
            return {
                'grupos_necesarios': 0,
                'terapias_por_dia': 0,
                'distribucion_semanal': [],
                'requiere_multiples_grupos': False,
                'descripcion': 'Sin terapias ordenadas'
            }
        
        # Caso 1: <= 20 terapias (un solo grupo)
        if cantidad_terapias <= self.TOTAL_DIAS_HABILES:
            return self._distribuir_un_grupo(cantidad_terapias)
        
        # Caso 2: > 20 terapias (múltiples grupos)
        return self._distribuir_multiples_grupos(cantidad_terapias)
    
    def _distribuir_un_grupo(self, cantidad):
        """Distribución para un solo grupo"""
        terapias_por_dia = cantidad / self.TOTAL_DIAS_HABILES
        
        # Distribuir equitativamente en 4 semanas
        base_por_semana = cantidad // self.SEMANAS
        resto = cantidad % self.SEMANAS
        
        distribucion = [base_por_semana] * self.SEMANAS
        for i in range(resto):
            distribucion[i] += 1
        
        return {
            'grupos_necesarios': 1,
            'terapias_por_dia': round(terapias_por_dia, 2),
            'distribucion_semanal': distribucion,
            'requiere_multiples_grupos': False,
            'descripcion': f'{cantidad} terapias en 1 grupo ({terapias_por_dia:.1f} por día)'
        }
    
    def _distribuir_multiples_grupos(self, cantidad):
        """Distribución para múltiples grupos"""
        grupos_necesarios = math.ceil(cantidad / self.TOTAL_DIAS_HABILES)
        terapias_por_dia = cantidad / self.TOTAL_DIAS_HABILES
        
        # Distribuir entre grupos
        terapias_por_grupo = []
        restante = cantidad
        
        for i in range(grupos_necesarios):
            if i == grupos_necesarios - 1:
                # Último grupo toma el resto
                terapias_por_grupo.append(restante)
            else:
                # Grupos anteriores toman 20
                terapias_por_grupo.append(self.TOTAL_DIAS_HABILES)
                restante -= self.TOTAL_DIAS_HABILES
        
        return {
            'grupos_necesarios': grupos_necesarios,
            'terapias_por_dia': round(terapias_por_dia, 2),
            'distribucion_por_grupo': terapias_por_grupo,
            'requiere_multiples_grupos': True,
            'descripcion': f'{cantidad} terapias en {grupos_necesarios} grupos'
        }
    
    def generar_calendario(self, fecha_inicio, cantidad_terapias):
        """
        Genera calendario de sesiones (solo días hábiles)
        
        Returns:
            list de fechas (datetime.date)
        """
        fechas = []
        fecha_actual = fecha_inicio
        dias_agregados = 0
        
        while dias_agregados < cantidad_terapias:
            # Solo días hábiles (lunes=0 a viernes=4)
            if fecha_actual.weekday() < 5:
                fechas.append(fecha_actual)
                dias_agregados += 1
            
            fecha_actual += timedelta(days=1)
            
            # Límite de seguridad (60 días naturales máximo)
            if (fecha_actual - fecha_inicio).days > 60:
                break
        
        return fechas
    
    def validar_distribucion(self, fecha_inicio, cantidad_terapias):
        """
        Valida si la distribución es viable
        
        Returns:
            {
                'valida': bool,
                'mensaje': str,
                'alertas': list
            }
        """
        alertas = []
        
        # Validar cantidad
        if cantidad_terapias <= 0:
            return {
                'valida': False,
                'mensaje': 'Cantidad de terapias debe ser mayor a 0',
                'alertas': []
            }
        
        if cantidad_terapias > 100:
            alertas.append('Cantidad inusualmente alta de terapias')
        
        # Validar fecha
        hoy = timezone.now().date()
        if fecha_inicio < hoy:
            return {
                'valida': False,
                'mensaje': 'Fecha de inicio no puede ser anterior a hoy',
                'alertas': []
            }
        
        # Calcular distribución
        dist = self.calcular(cantidad_terapias)
        
        if dist['requiere_multiples_grupos']:
            alertas.append(
                f"Se requieren {dist['grupos_necesarios']} grupos diferentes "
                f"para completar {cantidad_terapias} terapias en 4 semanas"
            )
        
        if dist['terapias_por_dia'] > 2:
            alertas.append(
                f"Requiere {dist['terapias_por_dia']:.1f} terapias por día "
                "(puede ser difícil de cumplir)"
            )
        
        return {
            'valida': True,
            'mensaje': 'Distribución viable',
            'alertas': alertas
        }
