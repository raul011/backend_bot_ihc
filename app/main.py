from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, Base, engine

from app.models import user, order,conductor,product
from app.db.seeder import seed_users, seed_conductores
from app.routers import auth,orders,webhook,products,websocket,conductor
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción mejor usar ["https://tu-frontend.onrender.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(products.router)
app.include_router(webhook.router)
# Router WebSocket
app.include_router(websocket.router)
app.include_router(conductor.router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    seed_users()
    seed_conductores()
