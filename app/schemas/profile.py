from pydantic import BaseModel
from typing import List

class EmotionLog(BaseModel):
    date: str
    mood: str

class ProfileResponse(BaseModel):
    username: str
    emotion_history: List[EmotionLog]