from fastapi import FastAPI, Request
import requests
from dotenv import load_dotenv # Importa load_dotenv
import os # Importa os para acceder a las variables de entorno

app = FastAPI()

# --- Cargar variables de entorno desde .env ---
#load_dotenv()
# --- Obtener el token de las variables de entorno ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}"

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    # Validar que el mensaje existe
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            requests.post(f"{TELEGRAM_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "¡Hola! Bienvenido a DELIVEROO. ¿Qué se te antoja hoy para disfrutar una comida deliciosa?",
                "reply_markup": {
                    "keyboard": [["Ver Menú"]],
                    "resize_keyboard": True
                }
            })


        # Responder al usuario
        requests.post(f"{TELEGRAM_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": f"Recibí tu mensaje: {text}"
        })

    return {"ok": True}