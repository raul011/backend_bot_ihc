from fastapi import FastAPI, Request
import os
import httpx

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN no está configurado en las variables de entorno.")

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

# --- Carritos en memoria por usuario ---
CARRITOS = {}

# --- Webhook principal ---
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
                "photo": "https://cdn.pixabay.com/photo/2015/08/19/02/27/restaurant-895427_1280.png",
                "caption": (
                    "🍕 *Restaurante Aguilar* 🍕\n\n"
                    "Donde cada comida es una obra de arte 🎨.\n"
                    "Explora nuestro menú y pide tus favoritas.\n\n"
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
            await mostrar_menu(chat_id)

    # --- Botones inline (callback_query) ---
    if "callback_query" in data:
        query = data["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        data_id = query["data"]

        if data_id == "ver_menu":
            await mostrar_menu(chat_id)

        elif data_id.startswith("prod_"):
            producto = data_id.replace("prod_", "")
            item = MENU.get(producto)

            if not item:
                await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": "Producto no encontrado ❌"
                })
                return {"ok": True}

            # Inicializar carrito si no existe
            if chat_id not in CARRITOS:
                CARRITOS[chat_id] = []

            # Agregar producto
            CARRITOS[chat_id].append(item)

            await mostrar_carrito(chat_id)

        elif data_id == "ver_carrito":
            await mostrar_carrito(chat_id)

        elif data_id == "confirmar":
            await confirmar_pedido(chat_id)

        elif data_id == "vaciar":
            CARRITOS[chat_id] = []
            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "🗑️ Carrito vaciado. Vuelve a elegir desde el menú 🍽️"
            })

    return {"ok": True}

# --- Funciones auxiliares ---
async def mostrar_menu(chat_id):
    keyboard = []
    for key, item in MENU.items():
        keyboard.append([{
            "text": f"{item['nombre']} - ${item['precio']}",
            "callback_data": f"prod_{key}"
        }])
    keyboard.append([{"text": "🛒 Ver Pedido", "callback_data": "ver_carrito"}])

    await client.post(f"{TELEGRAM_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": "🍽️ *Nuestro Menú*:\nSelecciona un producto para agregarlo a tu pedido 👇",
        "parse_mode": "Markdown",
        "reply_markup": {"inline_keyboard": keyboard}
    })

async def mostrar_carrito(chat_id):
    if chat_id in CARRITOS and CARRITOS[chat_id]:
        total = sum(p["precio"] for p in CARRITOS[chat_id])
        texto = "🛒 Tu pedido actual:\n"
        for p in CARRITOS[chat_id]:
            texto += f"- {p['nombre']} ${p['precio']}\n"
        texto += f"\nTotal: ${total:.2f}"

        keyboard = [
            [{"text": "Confirmar ✅", "callback_data": "confirmar"}],
            [{"text": "Vaciar ❌", "callback_data": "vaciar"}],
            [{"text": "Agregar más ➕", "callback_data": "ver_menu"}]
        ]

        await client.post(f"{TELEGRAM_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": texto,
            "reply_markup": {"inline_keyboard": keyboard}
        })
    else:
        await client.post(f"{TELEGRAM_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": "Tu carrito está vacío ❌"
        })

async def confirmar_pedido(chat_id):
    if chat_id in CARRITOS and CARRITOS[chat_id]:
        total = sum(p["precio"] for p in CARRITOS[chat_id])
        texto = "✅ Pedido confirmado:\n"
        for p in CARRITOS[chat_id]:
            texto += f"- {p['nombre']} ${p['precio']}\n"
        texto += f"\nTotal: ${total:.2f}\n\n¡Tu pedido está en camino! 🛵📍"

        await client.post(f"{TELEGRAM_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": texto
        })

        CARRITOS[chat_id] = []
    else:
        await client.post(f"{TELEGRAM_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": "Tu carrito está vacío ❌"
        })