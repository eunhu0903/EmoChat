from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from models.auth import User
from models.follow import Follow
from core.token import verify_token, get_token_from_header

router = APIRouter()

@router.post("/follow/{user_id}", tags=["Follow"])
def follow_user(user_id: int, token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    user = db.query(User).filter(User.email == email).first()

    if user.id == user_id:
        raise HTTPException(status_code=400, detail="자기 자신을 팔로우할 수 없습니다.")
    
    already_following = db.query(Follow).filter(
        Follow.follower_id == user.id,
        Follow.following_id == user_id
    ).first()

    if already_following:
        raise HTTPException(status_code=400, detail="이미 팔로우한 사용자입니다.")
    
    follow = Follow(follower_id = user.id, following_id=user_id)
    db.add(follow)
    db.commit()

    return {"message": "팔로우 성공!"}

@router.get("/followers", tags=["Follow"])
def get_followers(token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    user = db.query(User).filter(User.email == email).first()

    followers = db.query(Follow).filter(Follow.following_id == user.id).all()
    follower_list = [db.query(User).filter(User.id == f.follower_id).first().username for f in followers] 

    return {"followers": follower_list}

@router.get("/following", tags=["Follow"])
def get_following(token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    user = db.query(User).filter(User.email == email).first()

    following = db.query(Follow).filter(Follow.follower_id == user.id).all()
    following_list = [db.query(User).filter(User.id == f.following_id).first().username for f in following]

    return {"following": following_list}
    
@router.delete("/unfollow/{user_id}", tags=["Follow"])
def unfollow_user(user_id: int, token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    current_user = db.query(User).filter(User.email == email).first()

    follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    ).first()

    if not follow:
        raise HTTPException(status_code=404, detail="팔로우하지 않은 사용자입니다.")

    db.delete(follow)
    db.commit()
    return {"message": "언팔로우 완료!"}