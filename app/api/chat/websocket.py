from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Tuple
from db.session import get_db
from core.token import verify_token
from models.auth import User
from models.report import Report
from models.emotion import Emotion

router = APIRouter()

waiting_users: Dict[str, List[Tuple[str, WebSocket]]] = {}

active_pairs: Dict[WebSocket, WebSocket] = {}

@router.websocket("/ws/match")
async def websocket_match(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    try:
        email = verify_token(token, db)
    except:
        await websocket.close(code=4401)
        return

    user = db.query(User).filter(User.email == email).first()
    if not user:
        await websocket.close(code=4401)
        return

    recent_emotion = (
        db.query(Emotion)
        .filter(Emotion.user_id == user.id)
        .order_by(Emotion.created_at.desc())
        .first()
    )

    if not recent_emotion:
        await websocket.close(code=4403)
        return

    mood = recent_emotion.mood

    reported_ids = db.query(Report.reported_id).filter(Report.reporter_id == user.id).all()
    reported_by_ids = db.query(Report.reporter_id).filter(Report.reported_id == user.id).all()
    blocked_ids = set([uid for (uid,) in reported_ids + reported_by_ids])

    await websocket.accept()

    if mood not in waiting_users:
        waiting_users[mood] = []

    matched = False
    for idx, (other_email, other_ws) in enumerate(waiting_users[mood]):
        other_user = db.query(User).filter(User.email == other_email).first()
        if other_user and other_user.id not in blocked_ids and user.id not in (
            db.query(Report.reported_id).filter(Report.reporter_id == other_user.id).all()
        ):
            del waiting_users[mood][idx]
            active_pairs[websocket] = other_ws
            active_pairs[other_ws] = websocket
            await other_ws.send_text("✅ 매칭되었습니다.")
            await websocket.send_text("✅ 매칭되었습니다.")
            matched = True
            break

    if not matched:
        waiting_users[mood].append((email, websocket))
        await websocket.send_text("⌛ 매칭 대기 중입니다...")

    try:
        while True:
            data = await websocket.receive_text()

            if data == "__exit__":
                await websocket.close()
                break

            if websocket in active_pairs:
                await active_pairs[websocket].send_text(f"{user.username}: {data}")

    except WebSocketDisconnect:
        pass
    finally:
        if websocket in active_pairs:
            partner = active_pairs.pop(websocket)
            active_pairs.pop(partner, None)
            await partner.close()
        else:
            if mood in waiting_users:
                waiting_users[mood] = [
                    (e, ws) for (e, ws) in waiting_users[mood] if ws != websocket
                ]
