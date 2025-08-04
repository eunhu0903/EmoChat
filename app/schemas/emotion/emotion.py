from pydantic import BaseModel
from datetime import datetime

class EmotionCreate(BaseModel):
    mood: str

class EmotionResponse(BaseModel):
    id: int
    mood: str
    created_at: datetime

    class Config:
        from_attributes = True