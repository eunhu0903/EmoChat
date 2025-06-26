from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.session import get_db
from core.token import get_token_from_header, verify_token
from models.auth import User
from models.follow import Follow 

router = APIRouter()

@router.get("/users/search", tags=["User"])
def search_users(
    q: str = Query(..., min_length=1),
    token: str = Depends(get_token_from_header),
    db: Session = Depends(get_db)
):
    email = verify_token(token, db)
    current_user = db.query(User).filter(User.email == email).first()

    users = db.query(User).filter(
        User.username.ilike(f"%{q}%"),
        User.is_active == True,
        User.id != current_user.id 
    ).all()

    result = []
    for u in users:
        is_following = db.query(Follow).filter(
            Follow.follower_id == current_user.id,
            Follow.following_id == u.id
        ).first() is not None

        result.append({
            "id": u.id,
            "username": u.username,
            "is_following": is_following
        })

    return result
