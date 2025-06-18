from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.get("/signup", response_class=HTMLResponse)
async def singup_page(request: Request):
    return templates.TemplateResponse("auth/signup.html", {"request": request})