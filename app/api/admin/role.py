from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.token import verify_token, get_token_from_header
from models.auth import User

router = APIRouter()

@router.post("/admin/grant-admin/{user_id}", tags=["Admin-Role"])
def grant_admin(user_id: int, token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    admin_user = db.query(User).filter(User.email == email).first()

    if not admin_user or not admin_user.is_admin:
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    if user.is_admin:
        return {"message": "이미 관리자입니다."}
    
    user.is_admin = True
    db.commit()

    return {"message": f"{user.username}님에게 관리자 권한을 부여했습니다."}

@router.post("/admin/revoke-admin/{user_id}", tags=["Admin-Role"])
def revoke_admin(user_id: int, token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    admin_user = db.query(User).filter(User.email == email).first()

    if not admin_user or not admin_user.is_admin:
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    if not user.is_admin:
        return {"message": "이미 관리자가 아닙니다."}
    
    user.is_admin = False
    db.commit()

    return {"message": f"{user.username}님의 관리자 권한을 제거했습니다."}