from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, Base, engine

from app.models import user, order,driver,product
from app.db.seeder import seed_users
from app.routers import auth,orders,webhook,products


app = FastAPI()
app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(products.router)
app.include_router(webhook.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    seed_users()
