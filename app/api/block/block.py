from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.token import verify_token, get_token_from_header
from models.auth import User
from models.block import Block
from schemas.block import BlockCreate
from datetime import datetime

router = APIRouter()

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