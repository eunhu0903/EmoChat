from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from db.session import get_db
from core.token import verify_token, get_token_from_header
from models.auth import User
from models.emotion import Emotion
from schemas.emotion import EmotionCreate, EmotionResponse

router = APIRouter()
KST = ZoneInfo("Asia/Seoul")

@router.post("/emotion", status_code=201, tags=["Emotion"])
def select_emotion(emotion: EmotionCreate, token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    user = db.query(User).filter(User.email == email).first()

    if emotion.mood not in ["기쁨", "슬픔", "분노"]:
        raise HTTPException(status_code=400, detail="올바르지 않은 감정입니다.")
    
    now_kst = datetime.now(KST)
    start_of_today = datetime(now_kst.year, now_kst.month, now_kst.day)
    start_of_tomorrow = start_of_today + timedelta(days=1)

    existing = db.query(Emotion).filter(
        Emotion.user_id == user.id,
        Emotion.created_at >= start_of_today,
        Emotion.created_at < start_of_tomorrow
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="이미 오늘 감정을 선택했습니다.")
    
    db_emotion = Emotion(user_id=user.id, mood=emotion.mood, created_at=now_kst)
    db.add(db_emotion)
    db.commit()
    db.refresh(db_emotion)

    return {"message": f"{user.username}님의 기분 '{emotion.mood}'이 저장되었습니다."}


@router.get("/emotion", response_model=List[EmotionResponse], tags=["Emotion"])
def get_emotions(token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    emotions = (
        db.query(Emotion)
        .filter(Emotion.user_id == user.id)
        .order_by(Emotion.created_at.desc())
        .all()
    )

    if not emotions:
        raise HTTPException(status_code=404, detail="감정 기록이 없습니다.")

    return emotions


@router.get("/emotion/today", tags=["Emotion"])
def check_today_emotion(token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자 없음")

    now_kst = datetime.now(KST)
    start_of_today = datetime(now_kst.year, now_kst.month, now_kst.day)
    start_of_tomorrow = start_of_today + timedelta(days=1)

    existing = db.query(Emotion).filter(
        Emotion.user_id == user.id,
        Emotion.created_at >= start_of_today,
        Emotion.created_at < start_of_tomorrow
    ).first()

    return {"selected": bool(existing)}
