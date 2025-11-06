# backend/main.py
from fastapi import FastAPI, Request
import os
import httpx

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}"
client = httpx.AsyncClient()

MENU = [
    {"id": 1, "nombre": "Pizza Margarita", "precio": 7.5},
    {"id": 2, "nombre": "Pizza Pepperoni", "precio": 8.5},
    {"id": 3, "nombre": "Refresco de Cola", "precio": 2.0},
]

@app.get("/menu")
def get_menu():
    return {"menu": MENU}

@app.post("/pedido")
async def crear_pedido(req: Request):
    data = await req.json()
    chat_id = data.get("chat_id")
    items = data.get("items", [])

    total = sum(item["precio"] for item in items)

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

# --- Webhook para Telegram ---
@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.lower() in ["/menu", "/menú"]:
            # Construir el menú como texto
            texto = "🍽️ Nuestro menú:\n"
            for item in MENU:
                texto += f"- {item['nombre']} ${item['precio']}\n"

            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": texto
            })
        else:
            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"Recibí tu mensaje: {text}"
            })

    return {"ok": True}