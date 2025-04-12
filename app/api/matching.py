from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.token import get_token_from_header, verify_token
from models.auth import User
from models.emotion import Emotion
from models.matching import Matching, MatchingQueue
import random

router = APIRouter()

@router.post("/match", tags=["Matching"])
def match_user(token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    user = db.query(User).filter(User.email == email).first()

    in_queue = db.query(MatchingQueue).filter(MatchingQueue.user_id == user.id).first()
    if in_queue:
        raise HTTPException(status_code=400, detail="이미 매칭 대기중입니다.")
    
    today_emotion = db.query(Emotion).filter(Emotion.user_id == user.id).order_by(Emotion.created_at.desc()).first()

    waiting_users = db.query(MatchingQueue).join(User, MatchingQueue.user_id == User.id).filter(MatchingQueue.user_id != user.id).all()

    random.shuffle(waiting_users)

    for waiting in waiting_users:
        user_emotion = db.query(Emotion).filter(Emotion.user_id == waiting.user_id).order_by(Emotion.created_at.desc()).first()

        if user_emotion and user_emotion.mood == today_emotion.mood:
            matched_user_id = waiting.user_id

            new_match = Matching(user1_id=user.id, user2_id=matched_user_id)
            db.add(new_match)

            db.query(MatchingQueue).filter(MatchingQueue.user_id.in_([user.id, matched_user_id])).delete(synchronize_session=False)
            db.commit()

            return {"message": "매칭이 완료되었습니다.", "matched_with": matched_user_id}
        
    new_queue = MatchingQueue(user_id=user.id)
    db.add(new_queue)
    db.commit()
    return {"message": "매칭 대기중입니다."}
