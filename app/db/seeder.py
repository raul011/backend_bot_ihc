# app/db/seeder.py
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.product import Product

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

def seed_products(db: Session):
    productos = [
        {"name": "Burger 🍔", "price": 4.99, "image": "https://cdn.pixabay.com/photo/2016/03/05/19/02/hamburger-1238246_1280.jpg"},
        {"name": "Fries 🍟", "price": 1.49, "image": "https://cdn.pixabay.com/photo/2017/01/10/19/05/french-fries-1966528_1280.jpg"},
        {"name": "Pizza 🍕", "price": 7.99, "image": "https://cdn.pixabay.com/photo/2017/01/22/19/20/pizza-1995434_1280.jpg"},
    ]
    for p in productos:
        exists = db.query(Product).filter_by(name=p["name"]).first()
        if not exists:
            db.add(Product(**p))
    db.commit()


def run_seeders():
    db: Session = SessionLocal()
    try:
        seed_users(db)
        seed_products(db)
        # aquí puedes agregar más seeders (drivers, orders, etc.)
    finally:
        db.close()
