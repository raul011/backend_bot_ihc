from fastapi import APIRouter, Request
import os, json
import httpx
from app.core.config import settings

router = APIRouter()

TOKEN = settings.TELEGRAM_BOT_TOKEN
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}"
client = httpx.AsyncClient()

# --- Menú de productos ---
MENU = {
    "burger": {"nombre": "Burger 🍔", "precio": 4.99},
    "fries": {"nombre": "Fries 🍟", "precio": 1.49},
    "hotdog": {"nombre": "Hotdog 🌭", "precio": 3.49},
    "taco": {"nombre": "Taco 🌮", "precio": 3.99},
    "pizza": {"nombre": "Pizza 🍕", "precio": 7.99},
    "donut": {"nombre": "Donut 🍩", "precio": 1.49},
    "popcorn": {"nombre": "Popcorn 🍿", "precio": 1.99},
    "soda": {"nombre": "Soda 🥤", "precio": 1.50}
}

# Carritos en memoria
CARRITOS = {}

@router.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    print("Webhook recibido:", data)
    # --- Mensajes normales ---
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # /start
        if text.lower() == "/start":
            await client.post(f"{TELEGRAM_URL}/sendPhoto", json={
                "chat_id": chat_id,
                "photo": "https://cdn.pixabay.com/photo/2015/08/19/02/27/restaurant-895427_1280.png",
                "caption": (
                    "Restaurante Aguilar\n\n"
                    "Donde cada comida es una obra de arte 🎨.\n"
                    "Explora nuestro menú y pide tus favoritas.\n\n"
                    "✨ ¡Todo a un toque de distancia!"
                ),
                "parse_mode": "Markdown"
            })

            # Botón para abrir mini‑app
            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "Haz tu pedido ahora con un solo toque 👇",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "Abrir Menú 🍽️", "web_app": {"url": "https://frontend-mini-app-telegram.vercel.app/"}}]
                    ]
                }
            })

        # /menú → también abre mini‑app
        elif text.lower() in ["/menu", "/menú"]:
            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "🍽️ Abre nuestro menú interactivo 👇",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "Abrir Menú 🍽️", "web_app": {"url": "https://frontend-mini-app-telegram.vercel.app/"}}]
                    ]
                }
            })

        # Datos enviados desde el WebApp (React)
        if "web_app_data" in data["message"]:
            order_data = data["message"]["web_app_data"]["data"]
            items = json.loads(order_data)

            total = sum(item["precio"] for item in items)
            texto = "✅ Pedido confirmado:\n"
            for item in items:
                texto += f"- {item['nombre']} ${item['precio']}\n"
            texto += f"\nTotal: ${total:.2f}\n\n¡Tu pedido está en camino! 🛵📍"

            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": texto
            })

    return {"ok": True}