from fastapi import FastAPI, Request
import requests

app = FastAPI()

TOKEN = "8482705438:AAHkGyw-6g_uGmMdlci9pxGs8juuNjcwcfc"
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}"

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    # Validar que el mensaje existe
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # Responder al usuario
        requests.post(f"{TELEGRAM_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": f"Recibí tu mensaje: {text}"
        })

    return {"ok": True}