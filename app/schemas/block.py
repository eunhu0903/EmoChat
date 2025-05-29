from pydantic import BaseModel
from datetime import datetime

class BlockCreate(BaseModel):
    blocked_id: int

class BlockUser(BaseModel):
    blocked_id: int
    blocked_username: str
    blocked_email: str
    created_at: datetime

    class Config:
        from_attributes = True