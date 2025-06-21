from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from db.session import get_db
from core.token import verify_token, get_token_from_header
from models.auth import User
from models.emotion import Emotion

router = APIRouter()

@router.get("/", tags=["Home"])
def home(authorization: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(authorization, db)

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="유저를 찾을 수 없습니다.")
    
    today_start = datetime.combine(date.today(), datetime.min.time())

    emotion_counts = (
        db.query(Emotion.mood, func.count(Emotion.id).label("count"))
        .filter(Emotion.created_at >= today_start)
        .group_by(Emotion.mood)
        .order_by(func.count(Emotion.id).desc())
        .limit(3)
        .all()
    )

    top_emotions = [{"emotion": mood, "count": count} for mood, count in emotion_counts]


    return {
        "message": f"{user.username}님 환영합니다.",
        "top_emotions_today": top_emotions
    }