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
def match_user(
    token: str = Depends(get_token_from_header),
    db: Session = Depends(get_db)
):
    email = verify_token(token, db)
    user = db.query(User).filter(User.email == email).first()

    # 1) 오늘 감정 가져오기
    today_emotion = (
        db.query(Emotion)
          .filter(Emotion.user_id == user.id)
          .order_by(Emotion.created_at.desc())
          .first()
    )
    if not today_emotion:
        raise HTTPException(400, "감정을 먼저 선택하세요.")

    # 2) 매칭 시도 (대기열에 있는 사람 중)
    waiting_users = (
        db.query(MatchingQueue)
          .filter(MatchingQueue.user_id != user.id)
          .all()
    )
    random.shuffle(waiting_users)

    for waiting in waiting_users:
        other_emotion = (
            db.query(Emotion)
              .filter(Emotion.user_id == waiting.user_id)
              .order_by(Emotion.created_at.desc())
              .first()
        )
        if other_emotion and other_emotion.mood == today_emotion.mood:
            # 매칭 성사!
            matched_id = waiting.user_id
            new_match = Matching(user1_id=user.id, user2_id=matched_id)
            db.add(new_match)
            # 둘 다 대기열에서 제거
            db.query(MatchingQueue).filter(
                MatchingQueue.user_id.in_([user.id, matched_id])
            ).delete(synchronize_session=False)
            db.commit()
            return {"message": "매칭이 완료되었습니다.", "matched_with": matched_id}

    # 3) 아직 매칭 상대가 없으면
    #   a) 이미 대기열에 있었으면 "대기중" 리턴
    in_queue = db.query(MatchingQueue).filter(MatchingQueue.user_id == user.id).first()
    if in_queue:
        return {"message": "매칭 대기중입니다."}

    #   b) 처음 대기열에 올리는 경우
    db.add(MatchingQueue(user_id=user.id))
    db.commit()
    return {"message": "매칭 대기중입니다."}
