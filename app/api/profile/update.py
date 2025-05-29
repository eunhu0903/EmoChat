from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.token import verify_token, get_token_from_header
from core.security import verify_password, get_password_hash
from models.auth import User
from schemas.profile import UsernameUpdate, PasswordChangeRequest

router = APIRouter()

@router.put("/change-username", tags=["Profile"])
def update_username(username: UsernameUpdate, token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    
    existing = db.query(User).filter(User.username == username.new_username).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 사용 중인 닉네임입니다.")
    
    user.username = username.new_username
    db.commit()

    return {"message": "닉네임이 성공적으로 변경되었습니다."}

@router.put("/change-password", tags=["Profile"])
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

@router.delete("/delete-user", tags=["Profile"])
def delete_user(token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    
    db.delete(user)
    db.commit()
    return {"message": "계정이 성공적으로 삭제되었습니다."}