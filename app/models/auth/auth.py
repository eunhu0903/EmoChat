from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from db.session import Base

class User(Base):
    __tablename__="users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(10), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    emotions = relationship("Emotion", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete")

