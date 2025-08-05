from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List, Tuple
from db.session import get_db
from core.token import verify_token
from core.nickname import generate_random_name
from api.chat.chat_cleanup import delete_chat_after_timeout, deletion_tasks
from models.auth.auth import User
from models.report.report import Report
from models.emotion.emotion import Emotion
from models.chat.matching import Matching
from models.chat.chat import ChatMessage
from datetime import datetime
from zoneinfo import ZoneInfo
import asyncio

router = APIRouter()
KST = ZoneInfo("Asia/Seoul")

def get_user_from_token(token: str, db: Session) -> User:
    email = verify_token(token, db)
    user = db.query(User).filter(User.email == email).one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    return user

def get_blocked_user_ids(user_id: int, db: Session) -> set:
    reported = db.query(Report.reported_id).filter(Report.reporter_id == user_id)
    reported_by = db.query(Report.reporter_id).filter(Report.reported_id == user_id)
    return set(uid for (uid,) in reported.union(reported_by).all())

class MatchManager:
    def __init__(self):
        self.waiting_users: Dict[str, List[Tuple[str, WebSocket, str]]] = {}
        self.active_pairs: Dict[WebSocket, WebSocket] = {}
        self.nicknames: Dict[WebSocket, str] = {}
        self.match_ids: Dict[WebSocket, int] = {}

    async def match(self, mood: str, websocket: WebSocket, user: User, nickname: str, db: Session) -> Tuple[bool, int | None]:
        if mood not in self.waiting_users:
            self.waiting_users[mood] = []

        blocked_ids = get_blocked_user_ids(user.id, db)

        for idx, (other_email, other_ws, other_nick) in enumerate(self.waiting_users[mood]):
            other_user = db.query(User).filter(User.email == other_email).one_or_none()
            if other_user and other_user.id not in blocked_ids:
                del self.waiting_users[mood][idx]
                self.active_pairs[websocket] = other_ws
                self.active_pairs[other_ws] = websocket
                self.nicknames[websocket] = nickname
                self.nicknames[other_ws] = other_nick

                match = Matching(user1_id=user.id, user2_id=other_user.id, created_at=datetime.now(KST))
                db.add(match)
                db.commit()

                self.match_ids[websocket] = match.id
                self.match_ids[other_ws] = match.id

                await websocket.send_text(f"✅ 매칭되었습니다. 당신의 이름은 '{nickname}'입니다.")
                await other_ws.send_text(f"✅ 매칭되었습니다. 당신의 이름은 '{other_nick}'입니다.")
                return True, match.id

        self.waiting_users[mood].append((user.email, websocket, nickname))
        self.nicknames[websocket] = nickname
        await websocket.send_text(f"⌛ 매칭 대기 중입니다...\n당신의 이름은 '{nickname}'입니다.")
        return False, None

    async def cleanup(self, websocket: WebSocket, mood: str):
        if websocket in self.active_pairs:
            partner = self.active_pairs.pop(websocket, None)
            if partner:
                self.active_pairs.pop(partner, None)
                self.nicknames.pop(partner, None)
                self.match_ids.pop(partner, None)
                try:
                    await partner.close()
                except Exception:
                    pass
        else:
            self.waiting_users[mood] = [
                (e, ws, n) for (e, ws, n) in self.waiting_users.get(mood, []) if ws != websocket
            ]
        self.nicknames.pop(websocket, None)
        self.match_ids.pop(websocket, None)

async def end_chat_session(websocket: WebSocket, partner: WebSocket | None, manager: MatchManager):
    if partner:
        try:
            await partner.send_text("❌ 상대방이 채팅을 종료했습니다.")
        except Exception:
            pass
        try:
            await partner.close()
        except Exception:
            pass
        manager.active_pairs.pop(partner, None)
        manager.nicknames.pop(partner, None)
        manager.match_ids.pop(partner, None)
    
    manager.active_pairs.pop(websocket, None)
    manager.nicknames.pop(websocket, None)
    manager.match_ids.pop(websocket, None)
    try:
        await websocket.close()
    except Exception:
        pass

match_manager = MatchManager()

@router.websocket("/ws/match")
async def websocket_match(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    try:
        user = get_user_from_token(token, db)
    except Exception:
        await websocket.close(code=4401)
        return

    recent_emotion = (
        db.query(Emotion)
        .filter(Emotion.user_id == user.id)
        .order_by(Emotion.created_at.desc())
        .first()
    )
    if not recent_emotion:
        await websocket.accept()
        await websocket.send_text("❌ 감정을 먼저 선택하세요.")
        await websocket.close(code=4403)
        return

    mood = recent_emotion.mood
    nickname = generate_random_name()

    await websocket.accept()
    matched, _ = await match_manager.match(mood, websocket, user, nickname, db)

    match_id = match_manager.match_ids.get(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            if data == "__cancel__":
                if websocket not in match_manager.active_pairs:
                    await websocket.send_text("❌ 매칭이 취소되었습니다.")
                    await websocket.close()
                    break

            elif data == "__exit__":
                partner = match_manager.active_pairs.get(websocket)
                await end_chat_session(websocket, partner, match_manager)
                break

            elif websocket in match_manager.active_pairs:
                partner = match_manager.active_pairs[websocket]
                current_match_id = match_manager.match_ids.get(websocket)

                if current_match_id:
                    db.add(ChatMessage(
                        match_id=current_match_id,
                        sender_id=user.id,
                        content=data,
                        created_at=datetime.now(KST)
                    ))
                    db.commit()

                await partner.send_text(f"{match_manager.nicknames[websocket]}: {data}")

    except WebSocketDisconnect:
        pass

    finally:
        await match_manager.cleanup(websocket, mood)

        if match_id:
            if match_id in deletion_tasks:
                deletion_tasks[match_id].cancel()
            deletion_tasks[match_id] = asyncio.create_task(delete_chat_after_timeout(db, match_id, 300))
            
