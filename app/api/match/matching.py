from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.token import get_token_from_header, verify_token
from models.auth import User
from models.emotion import Emotion
from models.matching import Matching, MatchingQueue
from models.block import Block
import random

router = APIRouter()

@router.post("/match", tags=["Matching"])
def match_user(
    token: str = Depends(get_token_from_header),
    db: Session = Depends(get_db)
):
    email = verify_token(token, db)
    user = db.query(User).filter(User.email == email).first()

    today_emotion = (
        db.query(Emotion)
          .filter(Emotion.user_id == user.id)
          .order_by(Emotion.created_at.desc())
          .first()
    )
    if not today_emotion:
        raise HTTPException(400, "감정을 먼저 선택하세요.")
    
    blocked_user_id = db.query(Block.blocked_id).filter(Block.blocker_id == user.id).all()
    blocked_me_id = db.query(Block.blocker_id).filter(Block.blocked_id == user.id).all()
    block_id = {id for (id, ) in blocked_user_id + blocked_me_id}

    waiting_users = (
        db.query(MatchingQueue)
          .filter(MatchingQueue.user_id != user.id)
          .all()
    )
    random.shuffle(waiting_users)

    for waiting in waiting_users:
        if waiting.user_id in block_id:
            continue

        other_emotion = (
            db.query(Emotion)
              .filter(Emotion.user_id == waiting.user_id)
              .order_by(Emotion.created_at.desc())
              .first()
        )
        if other_emotion and other_emotion.mood == today_emotion.mood:
            matched_id = waiting.user_id
            new_match = Matching(user1_id=user.id, user2_id=matched_id)
            db.add(new_match)

            db.query(MatchingQueue).filter(
                MatchingQueue.user_id.in_([user.id, matched_id])
            ).delete(synchronize_session=False)
            db.commit()
            return {"message": "매칭이 완료되었습니다.", "matched_with": matched_id}

    in_queue = db.query(MatchingQueue).filter(MatchingQueue.user_id == user.id).first()
    if in_queue:
        return {"message": "이미 매칭 대기중입니다."}

    db.add(MatchingQueue(user_id=user.id))
    db.commit()
    return {"message": "매칭 대기중입니다."}
