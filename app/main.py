from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.admin import user_management, user_status, role
from api.auth import auth, email_verification
from api.home import home
from api.emotion import emotion
from api.follow import follow
from api.match import matching
from api.chat import websocket
from api.report import report
from api.profile import profile, update
from api.home import search
from api.block import block
from db.session import Base, engine
from views.auth import views_auth
from views.home import views_home
from views.profile import views_proflie

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Admin
app.include_router(user_management.router)
app.include_router(user_status.router)
app.include_router(role.router)

# Auth
app.include_router(auth.router)
app.include_router(email_verification.router)

# Chat
app.include_router(websocket.router)

# Emotion
app.include_router(emotion.router)

# follow
app.include_router(follow.router)

# Home
app.include_router(home.router)
app.include_router(search.router)

# Match
app.include_router(matching.router)

# Profile
app.include_router(profile.router)
app.include_router(update.router)

# Report
app.include_router(report.router)

# Block
app.include_router(block.router)

app.include_router(views_auth.router)
app.include_router(views_home.router)
app.include_router(views_proflie.router)