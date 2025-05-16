from pydantic import BaseModel
from typing import List

class EmotionLog(BaseModel):
    date: str
    mood: str

class ProfileResponse(BaseModel):
    username: str
    emotion_history: List[EmotionLog]

class UsernameUpdate(BaseModel):
    new_username: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str