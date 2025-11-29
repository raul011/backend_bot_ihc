import asyncio
from fastapi import HTTPException
from app.routers.websocket import active_connections

def notify_conductor(order, conductor_id: int):
    """Envía la orden al conductor por WebSocket si está conectado"""
    ws = active_connections.get(conductor_id)
    if not ws:
        # No hay conexión activa para ese conductor
        raise HTTPException(status_code=404, detail=f"Conductor {conductor_id} no tiene WebSocket activo")

    try:
        data = {
            "order_id": order.id,
            "comentario": order.comentario,
            "lat": float(order.lat) if order.lat is not None else None,
            "lng": float(order.lng) if order.lng is not None else None,
            "precio": float(order.total_price) if order.total_price is not None else None
        }
        asyncio.create_task(ws.send_json(data))
    except Exception as e:
        # Captura cualquier error de envío y devuelve un mensaje claro
        raise HTTPException(status_code=500, detail=f"Error enviando al conductor {conductor_id}: {str(e)}")