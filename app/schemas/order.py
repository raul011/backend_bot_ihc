from pydantic import BaseModel
from typing import List, Optional
from app.models.order import OrderStatus

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderCreate(BaseModel):
    telegram_user_id: int
    telegram_username: Optional[str]
    direccion_envio: Optional[str]
    comentario: Optional[str]
    total_price: float
    estado: Optional[OrderStatus]
    #conductor_id: Optional[int]
    items: List[OrderItemCreate]
    lat: float | None
    lng: float | None
    is_paid: bool = False


class AcceptOrderPayload(BaseModel):
    conductor_id: int
