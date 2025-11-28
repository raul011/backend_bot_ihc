# app/db/seeder.py
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def seed_users():
    db: Session = SessionLocal()
    try:
        # Usuarios iniciales
        initial_users = [
            {"name": "Admin", "email": "admin@example.com", "password": "1234"},
            {"name": "User1", "email": "user1@example.com", "password": "1234"},
            {"name": "raul_alberto", "email": "raulalberto@gmail.com.com", "password": "1234"},
        ]

        for u in initial_users:
            # Verificar si ya existe
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                user = User(
                    name=u["name"],
                    email=u["email"],
                    password=get_password_hash(u["password"])  # 👈 se guarda hasheada
                )
                db.add(user)
        db.commit()
    finally:
        db.close()

def seed_conductores():
    db: Session = SessionLocal()
    try:
        from app.models.conductor import Conductor
        # Conductores iniciales
        initial_conductores = [
            {
                "name": "Juan Perez",
                "email": "juan.perez@example.com",
                "password": "password123",
                "latitude": -16.5000,
                "longitude": -68.1500
            },
            {
                "name": "Maria Lopez",
                "email": "maria.lopez@example.com",
                "password": "password123",
                "latitude": -16.5100,
                "longitude": -68.1600
            },
             {
                "name": "Carlos Gomez",
                "email": "carlos.gomez@example.com",
                "password": "password123",
                "latitude": -16.4900,
                "longitude": -68.1400
            }
        ]

        for c in initial_conductores:
            existing = db.query(Conductor).filter(Conductor.email == c["email"]).first()
            if not existing:
                conductor = Conductor(
                    name=c["name"],
                    email=c["email"],
                    password=get_password_hash(c["password"]),
                    latitude=c["latitude"],
                    longitude=c["longitude"]
                )
                db.add(conductor)
        db.commit()
    finally:
        db.close()