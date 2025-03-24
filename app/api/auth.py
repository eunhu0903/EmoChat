from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.security import create_access_token, verify_password, get_password_hash
from db.session import get_db
from models.auth import User
from schemas.auth import UserCreate, Token, UserResponse, UserLogin

router = APIRouter()

@router.post("/signup", response_model=UserResponse, tags=["Auth"])
def signup(user: UserCreate, db: Session = Depends(get_db)):

    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="이미 등록된 닉네임입니다.")
    
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password, username=user.username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

