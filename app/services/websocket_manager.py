from fastapi import HTTPException
from app.routers.websocket import active_connections
from app.services.asignacion_orden import calcular_distancia_km, RESTAURANTE_LAT, RESTAURANTE_LNG

async def notify_conductor(order, conductor_id: int):
    ws = active_connections.get(conductor_id)
    if not ws:
        raise HTTPException(status_code=404, detail=f"Conductor {conductor_id} no tiene WebSocket activo")

    # Calcular distancia entre conductor y restaurante
    distancia_restaurante = None
    if order.conductor and order.conductor.latitude and order.conductor.longitude:
        distancia_restaurante = calcular_distancia_km(
            order.conductor.latitude, 
            order.conductor.longitude,
            RESTAURANTE_LAT, 
            RESTAURANTE_LNG
        )

    data = {
        "order_id": order.id,
        "comentario": order.comentario,
        "lat": float(order.lat) if order.lat else None,
        "lng": float(order.lng) if order.lng else None,
        "precio": float(order.total_price) if order.total_price else None,
        "distancia_restaurante": round(distancia_restaurante, 2) if distancia_restaurante else None
    }

    try:
        await ws.send_json(data)   # 👈 envío directo en el loop
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando al conductor {conductor_id}: {str(e)}")