import math
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.conductor import Conductor, ConductorEstado

# COORDENADAS DE TU LOCAL (Punto de partida del conductor)
# Reemplaza con las coordenadas reales de tu cocina
RESTAURANTE_LAT = -17.7833 
RESTAURANTE_LNG = -63.1821 

def calcular_distancia_km(lat1, lon1, lat2, lon2):
    # Fórmula de Haversine
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def asignar_conductor_automatico(db: Session):
    """
    Busca al conductor CONECTADO más cercano al restaurante
    que haya dado señales de vida en los últimos 15 min.
    """
    tiempo_limite = datetime.utcnow() - timedelta(minutes=15)
    
    # 1. Filtro inicial en Base de Datos (Rápido)
    candidatos = db.query(Conductor).filter(
        Conductor.estado == ConductorEstado.CONECTADO,
        Conductor.last_update >= tiempo_limite,
        Conductor.latitude.isnot(None),
        Conductor.longitude.isnot(None)
    ).all()
    
    if not candidatos:
        return None

    mejor_conductor = None
    menor_distancia = float('inf')

    # 2. Cálculo matemático fino (Preciso)
    for conductor in candidatos:
        distancia = calcular_distancia_km(
            RESTAURANTE_LAT, RESTAURANTE_LNG,
            conductor.latitude, conductor.longitude
        )
        
        if distancia < menor_distancia:
            menor_distancia = distancia
            mejor_conductor = conductor

    return mejor_conductor