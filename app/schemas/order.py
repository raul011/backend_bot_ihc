from pydantic import BaseModel
from typing import List, Optional

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
    items: List[OrderItemCreate]