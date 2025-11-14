from fastapi import APIRouter, Request
import json
import httpx
from app.core.config import settings

router = APIRouter()

TOKEN = settings.TELEGRAM_BOT_TOKEN
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}"

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

client = httpx.AsyncClient()

@router.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    print("Webhook recibido:", data)

    message = data.get("message", {})
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "")

    if not chat_id:
        # No hay chat_id → no podemos responder
        return {"ok": True}

    # --- /start ---
    if text.lower() == "/start":
        resp1 = await client.post(f"{TELEGRAM_URL}/sendPhoto", json={
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
        print("Respuesta sendPhoto:", resp1.text)

        resp2 = await client.post(f"{TELEGRAM_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": "Haz tu pedido ahora con un solo toque 👇",
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "Abrir Menú 🍽️", "web_app": {"url": "https://frontend-mini-app-telegram.vercel.app/"}}]
                ]
            }
        })
        print("Respuesta sendMessage:", resp2.text)

    # --- /menu ---
    elif text.lower() in ["/menu", "/menú"]:
        resp = await client.post(f"{TELEGRAM_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": "🍽️ Abre nuestro menú interactivo 👇",
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "Abrir Menú 🍽️", "web_app": {"url": "https://frontend-mini-app-telegram.vercel.app/"}}]
                ]
            }
        })
        print("Respuesta sendMessage:", resp.text)

    # --- Datos enviados desde el WebApp ---
    if "web_app_data" in message:
        try:
            order_data = message["web_app_data"]["data"]
            items = json.loads(order_data)

            total = sum(item.get("precio", 0) for item in items)
            texto = "✅ Pedido confirmado:\n"
            for item in items:
                texto += f"- {item.get('nombre')} ${item.get('precio')}\n"
            texto += f"\nTotal: ${total:.2f}\n\n¡Tu pedido está en camino! 🛵📍"

            resp = await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": texto
            })
            print("Respuesta pedido:", resp.text)
        except Exception as e:
            print("Error procesando web_app_data:", e)

    return {"ok": True}