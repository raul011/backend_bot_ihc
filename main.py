# backend/main.py
from fastapi import FastAPI, Request
import os
import httpx

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}"
client = httpx.AsyncClient()

# --- Datos simulados ---
MENU = [
    {"id": 1, "nombre": "Pizza Margarita", "precio": 7.5},
    {"id": 2, "nombre": "Pizza Pepperoni", "precio": 8.5},
    {"id": 3, "nombre": "Refresco de Cola", "precio": 2.0},
]

# --- Endpoint para menú ---
@app.get("/menu")
def get_menu():
    return {"menu": MENU}

# --- Endpoint para crear pedido ---
@app.post("/pedido")
async def crear_pedido(req: Request):
    data = await req.json()
    chat_id = data.get("chat_id")
    items = data.get("items", [])

    total = sum(item["precio"] for item in items)

    # Notificar al bot en Telegram
    if chat_id:
        texto = "¡Excelente! Aquí está el resumen de tu pedido:\n"
        for item in items:
            texto += f"- {item['nombre']} ${item['precio']}\n"
        texto += f"Total: ${total:.2f}"

        await client.post(f"{TELEGRAM_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": texto
        })

    return {"ok": True, "total": total}