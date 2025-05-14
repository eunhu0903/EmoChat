from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.token import verify_token, get_token_from_header
from models.auth import User

router = APIRouter()

@router.get("/admin/user", tags=["Admin-Management"])
def get_user(token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    admin_user = db.query(User).filter(User.email == email).first()

    if not admin_user or not admin_user.is_admin:
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    
    users = db.query(User).all()
    result = [
        {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active,
            "is_admin": user.is_admin
        }
        for user in users
    ]
    return {"users": result}

@router.delete("/admin/delete-user/{user_id}", tags=["Admin-Management"])
def delete_user(user_id: int, token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    admin_user = db.query(User).filter(User.email == email).first()

    if not admin_user or not admin_user.is_admin:
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="해당 유저를 찾을 수 없습니다.")

    db.delete(user_to_delete)
    db.commit()

    return {"message": f"{user_to_delete.username} 계정이 삭제되었습니다."}

