from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.token import verify_token, get_token_from_header
from core.security import verify_password, get_password_hash
from models.auth import User
from models.email_verification import EmailVerification
from schemas.profile import UsernameUpdate, PasswordChangeRequest, DeleteAccountRequest

router = APIRouter()

def get_user_by_email(db: Session, email: str) -> User:
    user = db.query(User).filter(User.email == email).one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    return user

@router.put("/change-username", tags=["Profile"])
def update_username(username: UsernameUpdate, authorization: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(authorization, db)
    user = get_user_by_email(db, email)
    
    existing = db.query(User).filter(User.username == username.new_username).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 사용 중인 닉네임입니다.")
    
    user.username = username.new_username
    db.commit()

    return {"message": "닉네임이 성공적으로 변경되었습니다."}

@router.put("/change-password", tags=["Profile"])
def change_password(request: PasswordChangeRequest, authorization: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(authorization, db)
    user = get_user_by_email(db, email)

    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")
    
    verification = db.query(EmailVerification).filter(
        EmailVerification.email == request.email,
        EmailVerification.is_verified == True
    ).first()

    if not verification:
        raise HTTPException(status_code=400, detail="이메일 인증이 완료되지 않았습니다.")
    
    user.hashed_password = get_password_hash(request.new_password)
    db.delete(verification)
    db.commit()

    return {"message": "비밀번호가 성공적으로 변경되었습니다."}

@router.delete("/delete-user", tags=["Profile"])
def delete_user(request: DeleteAccountRequest, authorization: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(authorization, db)
    user = get_user_by_email(db, email)
    
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")
    
    db.delete(user)
    db.commit()
    
    return {"message": "계정이 성공적으로 삭제되었습니다."}