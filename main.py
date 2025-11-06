from fastapi import FastAPI, Request
import httpx  # Importamos httpx en lugar de requests
from dotenv import load_dotenv
import os

app = FastAPI()

# load_dotenv() # Descomenta esto para pruebas locales
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Verificación de que el token existe
if TOKEN is None:
    raise ValueError("TELEGRAM_BOT_TOKEN no está configurado en las variables de entorno.")

TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}"

# Creamos un cliente httpx que se reutilizará en toda la aplicación
# Esto es mucho más eficiente que crear uno nuevo en cada petición
client = httpx.AsyncClient()

@app.on_event("startup")
async def startup_event():
    # Podemos verificar el webhook al iniciar (opcional pero recomendado)
    try:
        response = await client.get(f"{TELEGRAM_URL}/getMe")
        print(f"Bot info: {response.json()}")
    except httpx.RequestError as e:
        print(f"Error connecting to Telegram API: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    # Cerramos el cliente httpx de forma elegante al apagar la app
    await client.aclose()


@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "¡Hola! Bienvenido a Restaurant Aguilar. ¿Qué se te antoja hoy?",
                "reply_markup": {
                    "keyboard": [["Ver Menú"]],
                    "resize_keyboard": True
                }
            })
            return {"ok": True}

        elif text == "Ver Menú":
            keyboard = [
                [{"text": "Pizzas", "callback_data": "cat_pizzas"}],
                [{"text": "Bebidas", "callback_data": "cat_bebidas"}]
            ]
            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "Selecciona una categoría:",
                "reply_markup": {"inline_keyboard": keyboard}
            })
            return {"ok": True}

        else:
            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"Recibí tu mensaje: {text}. Usa /start o el botón 'Ver Menú'."
            })
            return {"ok": True}

    elif "callback_query" in data:
        query = data["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        data_id = query["data"]

        if data_id == "cat_pizzas":
            keyboard = [
                [{"text": "Margarita - $7.50", "callback_data": "prod_margarita"}],
                [{"text": "Pepperoni - $8.50", "callback_data": "prod_pepperoni"}]
            ]
            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "Elige tu pizza favorita 🍕",
                "reply_markup": {"inline_keyboard": keyboard}
            })
            return {"ok": True}

        elif data_id.startswith("prod_"):
            producto = data_id.replace("prod_", "")
            resumen = {
                "margarita": "Margarita x1 $7.50",
                "pepperoni": "Pepperoni x1 $8.50"
            }
            texto = f"Resumen de tu pedido:\n{resumen.get(producto)}\n¿Confirmas?"
            keyboard = [
                [{"text": "Sí, Confirmar", "callback_data": "confirmar"}],
                [{"text": "No, Modificar", "callback_data": "modificar"}]
            ]
            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": texto,
                "reply_markup": {"inline_keyboard": keyboard}
            })
            return {"ok": True}

        elif data_id == "confirmar":
            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "¡Pedido confirmado! 🛵📍"
            })
            return {"ok": True}

        elif data_id == "modificar":
            await client.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "Perfecto, vuelve a elegir desde el menú 🍽️"
            })
            return {"ok": True}

    return {"ok": True}