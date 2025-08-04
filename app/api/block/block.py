from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.token import verify_token, get_token_from_header
from models.auth.auth import User
from models.block.block import Block
from schemas.block.block import BlockCreate, BlockUser
from datetime import datetime

router = APIRouter()

@router.get("/block", tags=["Block"], response_model=list[BlockUser])
def block_get_user(token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    user = db.query(User).filter(User.email == email).first()

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
def block_user(block: BlockCreate, token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    blocker = db.query(User).filter(User.email == email).first()

    if blocker.id == block.blocked_id:
        raise HTTPException(status_code=400, detail="자기 자신은 차단할 수 없습니다.")
    
    existing = db.query(Block).filter(
        Block.blocker_id == blocker.id,
        Block.blocked_id == block.blocked_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="이미 차단한 사용자 입니다.")
    
    new_block = Block(
        blocker_id = blocker.id,
        blocked_id = block.blocked_id,
        created_at = datetime.utcnow()
    )

    db.add(new_block)
    db.commit()

    return {"message": "사용자를 차단했습니다."}

@router.delete("/block", tags=["Block"])
def unblock_user(unblock: BlockCreate, token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    blocker = db.query(User).filter(User.email == email).first()

    block = db.query(Block).filter(
        Block.blocker_id == blocker.id,
        Block.blocked_id == unblock.blocked_id
    ).first()

    if not block:
        raise HTTPException(status_code=404, detail="차단 기록이 없습니다.")
    
    db.delete(block)
    db.commit()

    return {"message": "차단이 해제되었습니다."}