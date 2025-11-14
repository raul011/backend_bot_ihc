# app/models/order.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Numeric, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(Integer, nullable=False)
    telegram_username = Column(String, nullable=False)
    #user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_paid = Column(Boolean, default=False)
    total_price = Column(Numeric(12, 2), default=0.00)
    shipping_address = Column(Text)

    # relación con items
    items = relationship("OrderItem", back_populates="order")

    def __repr__(self):
        return f"<Order #{self.id} telegram_user={self.telegram_user_id}>"
        #return f"<Order #{self.id} user={self.user_id}>"


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