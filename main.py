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
        
        # Preparamos el payload (el JSON que enviaremos)
        payload = {"chat_id": chat_id}

        # Lógica IF / ELIF / ELSE para manejar todos los casos
        if text == "/start":
            payload["text"] = "¡Hola! Bienvenido a Restaurant Aguilar. ¿Qué se te antoja hoy para disfrutar una comida deliciosa?"
            payload["reply_markup"] = {
                "keyboard": [
                    [{"text": "Ver Menú"}]  # Sintaxis JSON correcta
                ],
                "resize_keyboard": True
            }

        elif text == "Ver Menú":
            # Mostrar categorías
            keyboard = [
                [{"text": "Pizzas", "callback_data": "cat_pizzas"}],
                [{"text": "Bebidas", "callback_data": "cat_bebidas"}]
            ]
            requests.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "Selecciona una categoría:",
                "reply_markup": {"inline_keyboard": keyboard}
            })

       # --- Botones (callback_query) ---
    if "callback_query" in data:
        query = data["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        data_id = query["data"]

        if data_id == "cat_pizzas":
            keyboard = [
                [{"text": "Margarita - $7.50", "callback_data": "prod_margarita"}],
                [{"text": "Pepperoni - $8.50", "callback_data": "prod_pepperoni"}]
            ]
            requests.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "Elige tu pizza favorita 🍕",
                "reply_markup": {"inline_keyboard": keyboard}
            })

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
            requests.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": texto,
                "reply_markup": {"inline_keyboard": keyboard}
            })

        elif data_id == "confirmar":
            requests.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "¡Pedido confirmado! 🛵📍"
            })

        elif data_id == "modificar":
            requests.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "Perfecto, vuelve a elegir desde el menú "
            })

       

        # Enviamos la petición a Telegram de forma ASÍNCRONA
        try:
            await client.post(f"{TELEGRAM_URL}/sendMessage", json=payload, timeout=5.0)
        except httpx.RequestError as e:
            print(f"Error sending message to chat_id {chat_id}: {e}")

    return {"ok": True}