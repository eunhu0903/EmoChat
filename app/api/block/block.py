from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.token import verify_token, get_token_from_header
from models.auth.auth import User
from models.block.block import Block
from schemas.block.block import BlockCreate, BlockUser
from datetime import datetime
from zoneinfo import ZoneInfo

router = APIRouter()
KST = ZoneInfo("Asia/Seoul")

def get_user_by_email(db: Session, email: str) -> User:
    user = db.query(User).filter(User.email == email).one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return user

@router.get("/block", tags=["Block"], response_model=list[BlockUser])
def block_get_user(authorization: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(authorization, db)
    user = get_user_by_email(db, email)

    blocked = (
        db.query(Block, User)
        .join(User, Block.blocked_id == User.id)
        .filter(Block.blocker_id == user.id)
        .all()
    )

    return [
        BlockUser(
            blocked_id=blocked_user.id,
            blocked_username=blocked_user.username,
            blocked_email=blocked_user.email,
            created_at=block.created_at
        )
        for block, blocked_user in blocked
    ]


@router.post("/block", tags=["Block"])
def block_user(block: BlockCreate, authorization: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(authorization, db)
    blocker = get_user_by_email(db, email)

    if blocker.id == block.blocked_id:
        raise HTTPException(status_code=400, detail="자기 자신은 차단할 수 없습니다.")
    
    blocked_user = db.query(User).filter(User.id == block.blocked_id).one_or_none()
    if not blocked_user:
        raise HTTPException(status_code=404, detail="차단할 사용자를 찾을 수 없습니다.")
    
    existing = db.query(Block).filter(
        Block.blocker_id == blocker.id,
        Block.blocked_id == block.blocked_id
    ).one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="이미 차단한 사용자 입니다.")
    
    new_block = Block(
        blocker_id = blocker.id,
        blocked_id = block.blocked_id,
        created_at = datetime.now(KST)
    )

    db.add(new_block)
    db.commit()

    return {"message": f"{blocked_user.username}님을 차단했습니다."}

@router.delete("/block", tags=["Block"])
def unblock_user(unblock: BlockCreate, authorization: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(authorization, db)
    blocker = get_user_by_email(db, email)

    block = db.query(Block).filter(
        Block.blocker_id == blocker.id,
        Block.blocked_id == unblock.blocked_id
    ).one_or_none()

    if not block:
        raise HTTPException(status_code=404, detail="차단 기록이 없습니다.")
    
    db.delete(block)
    db.commit()

    return {"message": "차단이 해제되었습니다."}