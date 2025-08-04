from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.token import verify_token, get_token_from_header
from models.auth.auth import User

router = APIRouter()

@router.put("/admin/ban-user/{user_id}", tags=["Admin-User"])
def ban_user(user_id: int, token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    admin_user = db.query(User).filter(User.email == email).first()

    if not admin_user or not admin_user.is_admin:
        raise HTTPException(status_code=403, detail="관리자 권한이 없습니다.")
    
    user_to_ban = db.query(User).filter(User.id == user_id).first()
    if not user_to_ban:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    
    if not user_to_ban.is_active:
        raise HTTPException(status_code=400, detail="이미 정지된 유저입니다.")
    
    user_to_ban.is_active = False
    db.commit()

    return {"message": f"{user_to_ban.username} 계정이 정지되었습니다."}

@router.put("/admin/unban-user/{user_id}", tags=["Admin-User"])
def unban_user(user_id: int, token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    admin_user = db.query(User).filter(User.email == email).first()

    if not admin_user or not admin_user.is_admin:
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    
    user_to_unban = db.query(User).filter(User.id == user_id).first() 

    if not user_to_unban:
        raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없습니다.")
    
    if user_to_unban.is_active:
        return {"message": "해당 계정은 이미 활성 상태입니다."}
    
    user_to_unban.is_active = True
    db.commit()

    return {"message": f"{user_to_unban.username} 계정이 정지 해제되었습니다."}
