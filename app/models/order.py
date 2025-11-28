# app/models/order.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Numeric, Text,BigInteger,Float,Enum

from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base
import enum

# 1. Definimos los estados estrictos para evitar errores en el flujo
class OrderStatus(enum.Enum):
    PENDIENTE = "PENDIENTE"
    ASIGNADO = "ASIGNADO"     # <--- NUEVO: Ya tiene conductor, él va al restaurante
    EN_CAMINO = "EN_CAMINO"           # El conductor activa esto
    ENTREGADO = "ENTREGADO"           # Fin del flujo
    CANCELADO = "CANCELADO"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(BigInteger, nullable=False)
    telegram_username = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_paid = Column(Boolean, default=False)
    total_price = Column(Numeric(12, 2), default=0.00)
    comentario = Column(Text)
    direccion_envio = Column(Text)
    lat = Column(Float, nullable=True) 
    lng = Column(Float, nullable=True)     
    estado = Column(Enum(OrderStatus), default=OrderStatus.PENDIENTE)
    conductor_id = Column(Integer, ForeignKey("conductores.id"), nullable=True)

    # relación con items
    items = relationship("OrderItem", back_populates="order")
    # relación con conductor
    conductor = relationship("Conductor", back_populates="orders") # Asumiendo que tu clase conductor se llama "Driver"
    def __repr__(self):
        return f"<Order #{self.id} estado={self.estado}>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    # relaciones
    order = relationship("Order", back_populates="items")
    product = relationship("Product")

    def __repr__(self):
        return f"<OrderItem {self.quantity}x product={self.product_id}>"