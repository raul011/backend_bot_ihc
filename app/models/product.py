# app/models/product.py
from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    image = Column(String, nullable=True)  # aquí guardas la ruta/URL de la imagen
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Product {self.name}>"


