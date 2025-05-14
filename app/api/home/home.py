from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from core.token import verify_token, get_token_from_header
from models.auth import User

router = APIRouter()

@router.get("/", tags=["Home"])
def home(authorization: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(authorization, db)

    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"message": "유저를 찾을 수 없습니다."}
    return {"message": f"{user.username}님 환영합니다."}