from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.token import get_token_from_header, verify_token
from models.auth import User
from models.follow import Follow 

router = APIRouter()

@router.get("/users/search", tags=["User"])
def search_users(
    q: str = Query(..., min_length=1),
    authorization: str = Depends(get_token_from_header),
    db: Session = Depends(get_db)
):
    email = verify_token(authorization, db)
    user = db.query(User).filter(User.email == email).one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="유저를 찾을 수 없습니다.")

    users = db.query(User).filter(
        User.username.ilike(f"%{q}%"),
        User.is_active == True,
        User.id != user.id 
    ).all()

    following_ids = {f[0] for f in db.query(Follow.following_id).filter(Follow.follower_id == user.id).all()}

    return [
        {
            "id": u.id,
            "username": u.username,
            "is_following": u.id in following_ids
        }
        for u in users
    ]
