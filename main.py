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
MENU = {
    "margarita": {"nombre": "Pizza Margarita", "precio": 7.5},
    "pepperoni": {"nombre": "Pizza Pepperoni", "precio": 8.5},
    "refresco": {"nombre": "Refresco de Cola", "precio": 2.0},
}

# --- Carritos en memoria (por chat_id) ---
CARRITOS = {}

# --- Endpoint para menú (opcional, si quieres consumir desde React) ---
@app.get("/menu")
def get_menu():
    return {"menu": list(MENU.values())}

# --- Endpoint para crear pedido (opcional, si quieres consumir desde React) ---
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
                "photo": "https://cdn.pixabay.com/photo/2015/08/19/02/27/restaurant-895427_1280.png",
                "caption": (
                    "🍕 *Restaurante Aguilar* 🍕\n\n"
                    "Donde cada comida es una obra de arte 🎨.\n"
                    "Explora nuestro menú, crea tu propio pedido y pide tus favoritas.\n\n"
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
            # Mostrar menú como texto
            texto = "🍽️ Nuestro menú:\n"
            for key, item in MENU.items():
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
                [{"text": f"{MENU['margarita']['nombre']} 🍕 - ${MENU['margarita']['precio']}", "callback_data": "prod_margarita"}],
                [{"text": f"{MENU['pepperoni']['nombre']} 🍕 - ${MENU['pepperoni']['precio']}", "callback_data": "prod_pepperoni"}],
                [{"text": f"{MENU['refresco']['nombre']} 🥤 - ${MENU['refresco']['precio']}", "callback_data": "prod_refresco"}]
            ]
            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "Selecciona tu producto:",
                "reply_markup": {"inline_keyboard": keyboard}
            })

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

            # Agregar producto al carrito
            CARRITOS[chat_id].append(item)

            # Mostrar carrito actual
            total = sum(p["precio"] for p in CARRITOS[chat_id])
            texto = "🛒 Tu carrito actual:\n"
            for p in CARRITOS[chat_id]:
                texto += f"- {p['nombre']} ${p['precio']}\n"
            texto += f"\nTotal: ${total:.2f}"

            keyboard = [
                [{"text": "Agregar más productos ➕", "callback_data": "ver_menu"}],
                [{"text": "Confirmar pedido ✅", "callback_data": "confirmar"}],
                [{"text": "Vaciar carrito ❌", "callback_data": "vaciar"}]
            ]

            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": texto,
                "reply_markup": {"inline_keyboard": keyboard}
            })

        elif data_id == "confirmar":
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

                # Vaciar carrito
                CARRITOS[chat_id] = []
            else:
                await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": "Tu carrito está vacío ❌"
                })

        elif data_id == "vaciar":
            CARRITOS[chat_id] = []
            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "🗑️ Carrito vaciado. Vuelve a elegir desde el menú 🍽️"
            })

    return {"ok": True}