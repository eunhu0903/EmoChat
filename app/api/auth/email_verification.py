from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from models.auth.email_verification import EmailVerification
from schemas.auth.email_verification import EmailRequest, CodeVerifyRequest
from core.send_email import send_verification_email
from datetime import datetime, timedelta
import secrets

router = APIRouter()
CODE_EXPIRY_MINUTES = 5

def generate_verification_code() -> str:
    return "".join([str(secrets.randbelow(10)) for _ in range(6)])

@router.post("/send-code")
def send_code(payload: EmailRequest, db: Session = Depends(get_db)):
    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=CODE_EXPIRY_MINUTES)

    entry = db.query(EmailVerification).filter(EmailVerification.email == payload.email).first()
    if entry:
        entry.code = code
        entry.expires_at = expires_at
        entry.is_verified = False
    else:
        db.add(EmailVerification(email=payload.email, code=code, expires_at=expires_at))
    db.commit()

    try:
        send_verification_email(payload.email, code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이메일 전송 실패: {str(e)}")
    
    return {"message": "인증 코드가 전송되었습니다."}

@router.post("/verify-code")
def verify_code(payload: CodeVerifyRequest, db: Session = Depends(get_db)):
    entry = db.query(EmailVerification).filter(EmailVerification.email == payload.email).first()

    if not entry:
        raise HTTPException(status_code=404, detail="이메일 인증 요청이 없습니다.")
    if entry.is_verified:
        return {"message": "이미 인증된 메일입니다."}
    if entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="인증 코드가 만료되었습니다.")
    if entry.code != payload.code:
        raise HTTPException(status_code=400, detail="인증 코드가 일치하지 않습니다.")
    
    entry.is_verified = True
    db.commit()
    return {"message": "이메일 인증이 완료되었습니다."}