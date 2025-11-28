# models/driver.py
import enum
from datetime import datetime 
from sqlalchemy import Column, Integer, String, Float,Enum,DateTime
from app.db.session import Base
from sqlalchemy.orm import relationship


# 1. Definimos tus estados estrictos
class ConductorEstado(enum.Enum):
    DESCONECTADO = "DESCONECTADO" # El conductor cerró sesión o "se apagó"
    CONECTADO = "CONECTADO"       # Disponible para recibir pedidos
    OCUPADO = "OCUPADO"           # Llevando un pedido actualmente

class Conductor(Base):
    __tablename__ = "conductores"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    # NUEVO CAMPO IMPORTANTE:
    # Registra la última vez que el conductor envió su ubicación.
    # Si pasó más de 10 min, lo ignoramos aunque diga "CONECTADO".
    last_update = Column(DateTime, default=datetime.utcnow)

    estado = Column(Enum(ConductorEstado), default=ConductorEstado.DESCONECTADO)
    # Relación con orders
    orders = relationship("Order", back_populates="conductor")
