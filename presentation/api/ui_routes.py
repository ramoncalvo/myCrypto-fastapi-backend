from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from config import settings

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve the login page"""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "use_minified_assets": settings.use_minified_assets
    })

@router.get("/login", response_class=HTMLResponse)
async def login_page_explicit(request: Request):
    """Serve the login page explicitly"""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "use_minified_assets": settings.use_minified_assets
    })

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Serve the dashboard page"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "use_minified_assets": settings.use_minified_assets
    })

@router.get("/app", response_class=HTMLResponse)
async def app_page(request: Request):
    """Serve the main app page (alias for dashboard)"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "use_minified_assets": settings.use_minified_assets
    })
