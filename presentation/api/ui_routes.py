from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login/registro"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_redirect(request: Request):
    """Redirección a la página de login"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Página principal del dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/app", response_class=HTMLResponse)
async def app_redirect(request: Request):
    """Redirección a la aplicación principal"""
    return templates.TemplateResponse("dashboard.html", {"request": request})
