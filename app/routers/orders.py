# routers/orders.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.schemas.order import OrderCreate, AcceptOrderPayload
from app.db.session import get_db
from datetime import datetime
from app.services.asignacion_orden import asignar_conductor_automatico

from app.services.websocket_manager import notify_conductor  # tu manejador de WS


router = APIRouter()

@router.post("/orders")
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    # Crear la orden con datos de Telegram
    order = Order(
        telegram_user_id=order_data.telegram_user_id,
        telegram_username=order_data.telegram_username,
        direccion_envio=order_data.direccion_envio,
        total_price=order_data.total_price,
        comentario=order_data.comentario,
        created_at=datetime.utcnow(),
        is_paid=order_data.is_paid,
        lat=order_data.lat,
        lng=order_data.lng
    )
    db.add(order)
    db.flush()  # obtener order.id antes de commit

    # Crear items (sin validar ni modificar stock)
    for item_data in order_data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item_data.quantity,
            price=item_data.price
        )
        db.add(order_item)

    db.commit()
    db.refresh(order)
    return order




@router.post("/orders/{order_id}/dispatch")
async def dispatch_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    if order.estado != OrderStatus.PENDIENTE:
        raise HTTPException(status_code=400, detail="La orden ya fue procesada")

    conductor_cercano = asignar_conductor_automatico(db)
    if not conductor_cercano:
        raise HTTPException(status_code=404, detail="No hay conductores disponibles")

    # Avisar al conductor por WebSocket
    await notify_conductor(order, conductor_cercano.id, conductor_cercano)

    return {
        "message": "Orden enviada al conductor más cercano",
        "order_id": order.id,
        "conductor_id": conductor_cercano.id
    }


@router.put("/orders/{order_id}/accept")
async def accept_order(order_id: int, payload: AcceptOrderPayload, db: Session = Depends(get_db)):
    conductor_id = payload.conductor_id
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    if order.estado != OrderStatus.PENDIENTE:
        raise HTTPException(status_code=400, detail="La orden ya fue procesada")

    order.estado = OrderStatus.ASIGNADO
    order.conductor_id = conductor_id
    db.commit()
    db.refresh(order)

    return {
        "message": "Orden aceptada por el conductor",
        "order_id": order.id,
        "conductor_id": conductor_id
    }

 @router.put("/{order_id}/reject")
async def reject_order(order_id: int, payload: RejectOrderPayload, db: Session = Depends(get_db)):
    conductor_id = payload.conductor_id

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    #order.estado = OrderStatus.RECHAZADA
    db.commit()
    db.refresh(order)

    #  ahora excluimos al conductor que rechazó
    nuevo_conductor = asignar_conductor_automatico(db, excluidos=[conductor_id])
    if not nuevo_conductor:
        raise HTTPException(status_code=404, detail="No hay conductores disponibles")

    await notify_conductor(order, nuevo_conductor.id)

    return {
        "message": "Orden rechazada, enviada a otro conductor",
        "order_id": order.id,
        "conductor_id": nuevo_conductor.id
    }
