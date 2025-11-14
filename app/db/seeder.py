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