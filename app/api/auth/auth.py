from fastapi import APIRouter, Depends, HTTPException, Request, Response
from jose.exceptions import ExpiredSignatureError, JWTError
from sqlalchemy.orm import Session
from sqlalchemy import or_
from core.security import (
    create_access_token, 
    verify_password, 
    get_password_hash, 
    create_refresh_token, 
    decode_refresh_token
)
from db.session import get_db
from models.auth import User
from models.email_verification import EmailVerification
from schemas.auth import UserCreate, Token, UserResponse, UserLogin
from models.token import RefreshToken
from core.config import REFRESH_TOKEN_EXPIRE_DAYS

router = APIRouter()

def set_refresh_token_cookie(response: Response, token: str):
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400
    )

@router.post("/signup", response_model=UserResponse, tags=["Auth"])
def signup(user: UserCreate, db: Session = Depends(get_db)):

    verification = db.query(EmailVerification).filter(
        EmailVerification.email == user.email,
        EmailVerification.is_verified == True
    ).first()

    if not verification:
        raise HTTPException(status_code=400, detail="이메일 인증이 완료되지 않았습니다.")
    
    existing_user = db.query(User).filter(
        or_(User.username == user.username, User.email == user.email)
    ).first()

    if existing_user:
        if existing_user.username == user.username:
            raise HTTPException(status_code=400, detail="이미 등록된 닉네임 입니다.")
        else:
            raise HTTPException(status_code=400, detail="이미 등록된 이메일 입니다.")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password, username=user.username)
    db.add(new_user)
    db.delete(verification)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login", response_model=Token, tags=["Auth"])
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="잘못된 아이디 또는 비밀번호 입니다.")

    if not db_user.is_active:
        raise HTTPException(status_code=403, detail="이 계정은 정지되었습니다.")
    
    access_token = create_access_token(data={"sub": db_user.email})
    refresh_token = create_refresh_token(data={"sub": db_user.email})

    db.query(RefreshToken).filter(RefreshToken.user_id == db_user.id).delete()
    db.add(RefreshToken(user_id=db_user.id, token=refresh_token))
    db.commit()

    set_refresh_token_cookie(response, refresh_token)

    return {"access_token": access_token, "token_type": "Bearer"}

@router.post("/refresh", response_model=Token, tags=["Auth"])
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Refresh Token이 없습니다.")
    
    db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    
    try:
        payload = decode_refresh_token(token)
        email = payload.get("sub")
    except ExpiredSignatureError:
        db.delete(db_token)
        db.commit()
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
    except JWTError:
        db.delete(db_token)
        db.commit()
        raise HTTPException(status_code=401, detail="토큰 검증에 실패했습니다.")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    
    new_access = create_access_token(data={"sub": user.email})
    new_refresh = create_refresh_token(data={"sub": user.email})

    db.delete(db_token)
    db.add(RefreshToken(user_id=user.id, token=new_refresh))
    db.commit()

    set_refresh_token_cookie(response, new_refresh)

    return {"access_token": new_access, "token_type": "Bearer"}

@router.post("/logout", tags=["Auth"])
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if token:
        db.query(RefreshToken).filter(RefreshToken.token == token).delete()
        db.commit()
    response.delete_cookie("refresh_token")
    return {"message": "로그아웃 되었습니다."}