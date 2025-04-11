from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.security import create_access_token, verify_password, get_password_hash
from db.session import get_db
from models.auth import User
from schemas.auth import UserCreate, Token, UserResponse, UserLogin, PasswordChangeRequest
from core.token import verify_token, get_token_from_header

router = APIRouter()

@router.post("/signup", response_model=UserResponse, tags=["User"])
def signup(user: UserCreate, db: Session = Depends(get_db)):

    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="이미 등록된 닉네임 입니다.")
    
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일 입니다.")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password, username=user.username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token, tags=["User"])
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="잘못된 아이디 또는 비밀번호 입니다.")

    if not db_user.is_active:
        raise HTTPException(status_code=403, detail="이 계정은 정지되었습니다.")
     
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "Bearer"}

@router.put("/user/change-password", tags=["User"])
def change_password(request: PasswordChangeRequest, token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    user = db.query(User).filter(User.email == email).first()

    if not verify_password(request.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="현재 비밀번호가 올바르지 않습니다.")
    
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")
    
    user.hashed_password = get_password_hash(request.new_password)
    db.commit()

    return {"message": "비밀번호가 성공적으로 변경되었습니다."}