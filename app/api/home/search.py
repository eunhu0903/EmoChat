from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.token import get_token_from_header, verify_token
from models.auth import User

router = APIRouter()

@router.get("/users/search", tags=["User"])
def search_users(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):

    users = db.query(User).filter(
        User.username.ilike(f"%{q}%"),
        User.is_active == True
    ).all()

    return [{"id": u.id, "username": u.username} for u in users]
