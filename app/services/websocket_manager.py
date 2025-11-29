from fastapi import HTTPException
from app.routers.websocket import active_connections
from app.services.asignacion_orden import calcular_distancia_km, RESTAURANTE_LAT, RESTAURANTE_LNG

async def notify_conductor(order, conductor_id: int, conductor=None):
    ws = active_connections.get(conductor_id)
    if not ws:
        raise HTTPException(status_code=404, detail=f"Conductor {conductor_id} no tiene WebSocket activo")

    # Calcular distancia entre conductor y restaurante
    distancia_restaurante = None
    tiempo_estimado = None
    # Usar el conductor pasado como parámetro o intentar obtenerlo de la orden
    conductor_obj = conductor if conductor else order.conductor
    
    if conductor_obj and conductor_obj.latitude and conductor_obj.longitude:
        distancia_restaurante = calcular_distancia_km(
            conductor_obj.latitude, 
            conductor_obj.longitude,
            RESTAURANTE_LAT, 
            RESTAURANTE_LNG
        )
        
        # Calcular tiempo estimado en minutos
        # Asumiendo velocidad promedio de 30 km/h en ciudad
        VELOCIDAD_PROMEDIO_KMH = 30
        if distancia_restaurante:
            tiempo_estimado = (distancia_restaurante / VELOCIDAD_PROMEDIO_KMH) * 60  # convertir a minutos

    data = {
        "order_id": order.id,
        "comentario": order.comentario,
        "lat": float(order.lat) if order.lat else None,
        "lng": float(order.lng) if order.lng else None,
        "precio": float(order.total_price) if order.total_price else None,
        "distancia_restaurante": round(distancia_restaurante, 2) if distancia_restaurante else None,
        "tiempo_estimado": round(tiempo_estimado) if tiempo_estimado else None
    }

    try:
        await ws.send_json(data)   #  envío directo en el loop
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando al conductor {conductor_id}: {str(e)}")