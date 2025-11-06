# backend/main.py
from fastapi import FastAPI, Request
import os
import httpx

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN no está configurado en las variables de entorno.")

TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}"
client = httpx.AsyncClient()

# --- Datos simulados ---
MENU = [
    {"id": 1, "nombre": "Pizza Margarita", "precio": 7.5},
    {"id": 2, "nombre": "Pizza Pepperoni", "precio": 8.5},
    {"id": 3, "nombre": "Refresco de Cola", "precio": 2.0},
]

# --- Endpoint para menú (para React) ---
@app.get("/menu")
def get_menu():
    return {"menu": MENU}

# --- Endpoint para crear pedido (desde React) ---
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

    # --- Mensajes normales ---
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.lower() == "/start":
            # Imagen promocional
            await client.post(f"{TELEGRAM_URL}/sendPhoto", json={
                "chat_id": chat_id,
                "photo": "https://cdn.pixabay.com/photo/2015/08/19/02/27/restaurant-895427_1280.png",  # URL pública de tu imagen
                "caption": (
                    "🍕 *Pizzería Nova* 🍕\n\n"
                    "Donde cada pizza es una obra de arte 🎨.\n"
                    "Explora nuestro menú, crea tu propia pizza o pide tus favoritas.\n\n"
                    "✨ ¡Todo a un toque de distancia!"
                ),
                "parse_mode": "Markdown"
            })

            # Botón inline
            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "Haz tu pedido ahora con un solo toque 👇",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "Hacer Mi Pedido 🍕", "callback_data": "ver_menu"}]
                    ]
                }
            })

        elif text.lower() in ["/menu", "/menú"]:
            # Construir menú como texto
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

    # --- Botones inline (callback_query) ---
    if "callback_query" in data:
        query = data["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        data_id = query["data"]

        if data_id == "ver_menu":
            keyboard = [
                [{"text": "Pizza Margarita 🍕 - $7.50", "callback_data": "prod_margarita"}],
                [{"text": "Pizza Pepperoni 🍕 - $8.50", "callback_data": "prod_pepperoni"}],
                [{"text": "Refresco 🥤 - $2.00", "callback_data": "prod_refresco"}]
            ]
            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "Selecciona tu producto:",
                "reply_markup": {"inline_keyboard": keyboard}
            })

        elif data_id.startswith("prod_"):
            producto = data_id.replace("prod_", "")
            resumen = {
                "margarita": "Pizza Margarita x1 $7.50",
                "pepperoni": "Pizza Pepperoni x1 $8.50",
                "refresco": "Refresco de Cola x1 $2.00"
            }
            texto = f"Resumen de tu pedido:\n{resumen.get(producto)}\n¿Confirmas?"
            keyboard = [
                [{"text": "Sí, Confirmar ✅", "callback_data": "confirmar"}],
                [{"text": "No, Modificar ❌", "callback_data": "modificar"}]
            ]
            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": texto,
                "reply_markup": {"inline_keyboard": keyboard}
            })

        elif data_id == "confirmar":
            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "¡Pedido confirmado! 🛵📍"
            })

        elif data_id == "modificar":
            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "Perfecto, vuelve a elegir desde el menú 🍽️"
            })

    return {"ok": True}