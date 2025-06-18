from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def singup_page(request: Request):
    return templates.TemplateResponse("home/home.html", {"request": request})