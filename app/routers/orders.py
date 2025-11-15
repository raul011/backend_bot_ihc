# routers/orders.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate
from app.db.session import get_db
from datetime import datetime

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
        is_paid=False
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