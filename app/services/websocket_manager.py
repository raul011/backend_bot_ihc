import asyncio
from app.routers.websocket import active_connections

def notify_conductor(order, conductor_id: int):
    """Envía la orden al conductor por WebSocket si está conectado"""
    ws = active_connections.get(conductor_id)
    if ws:
        data = {
            "order_id": order.id,
            "comentario": order.comentario,
            "lat": order.lat,
            "lng": order.lng,
            "precio": str(order.total_price)
        }
        asyncio.create_task(ws.send_json(data))