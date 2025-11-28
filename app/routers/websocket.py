from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict

router = APIRouter()
active_connections: Dict[int, WebSocket] = {}  # conductor_id -> websocket

@router.websocket("/ws/conductor/{conductor_id}")
async def websocket_endpoint(websocket: WebSocket, conductor_id: int):
    await websocket.accept()
    active_connections[conductor_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            # aquí podrías manejar mensajes del conductor (ej: "acepto orden")
            print(f"Conductor {conductor_id} envió:", data)

    except WebSocketDisconnect:
        del active_connections[conductor_id]