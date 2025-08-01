import asyncio
from sqlalchemy.orm import Session
from models.chat import ChatMessage

deletion_tasks = {}

async def delete_chat_after_timeout(db: Session, match_id: int, timeout_sec: int = 300):
    await asyncio.sleep(timeout_sec)

    chat_exists = db.query(ChatMessage).filter(ChatMessage.match_id == match_id).first()
    if chat_exists and not chat_exists.keep_log:
        db.query(ChatMessage).filter(ChatMessage.match_id == match_id).delete()
        db.commit()

    deletion_tasks.pop(match_id, None)