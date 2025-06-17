from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

router = APIRouter()

rooms: Dict[str, List[WebSocket]] = {}

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()

    if room_id not in rooms:
        rooms[room_id] = []
    rooms[room_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            if data == "__exit__":
                await websocket.close()
                rooms[room_id].remove(websocket)
                if not rooms[room_id]:
                    del rooms[room_id]
                break
                    

            for connection in rooms[room_id]:
                if connection != websocket:
                    await connection.send_text(data)

    except WebSocketDisconnect:
        if websocket in rooms.get(room_id, []):
            rooms[room_id].remove(websocket)
        if room_id in rooms and not rooms[room_id]:
            del rooms[room_id]
