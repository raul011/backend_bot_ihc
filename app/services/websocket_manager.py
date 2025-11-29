from fastapi import HTTPException
from app.routers.websocket import active_connections

async def notify_conductor(order, conductor_id: int):
    ws = active_connections.get(conductor_id)
    if not ws:
        raise HTTPException(status_code=404, detail=f"Conductor {conductor_id} no tiene WebSocket activo")

    data = {
        "order_id": order.id,
        "comentario": order.comentario,
        "lat": float(order.lat) if order.lat else None,
        "lng": float(order.lng) if order.lng else None,
        "precio": float(order.total_price) if order.total_price else None
    }

    try:
        await ws.send_json(data)   # 👈 envío directo en el loop
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando al conductor {conductor_id}: {str(e)}")