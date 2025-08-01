from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from db.session import get_db
from core.token import verify_token, get_token_from_header
from models.auth import User
from models.emotion import Emotion
from schemas.profile import ProfileResponse

router = APIRouter()

@router.get("/profile", response_model=ProfileResponse, tags=["Profile"])
def get_my_profile(authorization: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(authorization, db)
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)

    emotion_logs = (
        db.query(Emotion.created_at, Emotion.mood)
        .filter(Emotion.user_id == user.id, Emotion.created_at >= thirty_days_ago)
        .order_by(Emotion.created_at.desc())
        .all()
    )

    emotion_data = [
        {
            "date": created_at.date().isoformat(),
            "mood": mood,
        }
        for created_at, mood in emotion_logs
    ]

    return {
        "username": user.username,
        "emotion_history": emotion_data
    }