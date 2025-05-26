from pydantic import BaseModel

class BlockCreate(BaseModel):
    blocked_id: int