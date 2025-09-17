from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from pathlib import Path

from config import settings
from database import db_factory
from infrastructure.dependency_injection.container import DIContainer

# Import routers
from presentation.api.auth_routes import router as auth_router
from presentation.api.user_routes import router as user_router
from presentation.api.crypto_asset_routes import router as crypto_asset_router
from presentation.api.portfolio_routes import router as portfolio_router
from presentation.api.portfolio_aggregate_routes import router as portfolio_aggregate_router
from presentation.api.transaction_routes import router as transaction_router
from presentation.api.bitso_routes import router as bitso_router
# from presentation.api.websocket_routes import router as websocket_router
from presentation.api.ui_routes import router as ui_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db_factory.connect()
    yield
    # Shutdown
    await db_factory.disconnect()


app = FastAPI(
    title="MyCrypto API - Clean Architecture",
    description="A FastAPI application for cryptocurrency portfolio management using Clean Architecture principles",
    version="3.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files - serve minified assets in production
if settings.use_minified_assets and Path("static/dist").exists():
    app.mount("/static", StaticFiles(directory="static/dist"), name="static")
    print("🚀 Serving minified assets from static/dist/")
else:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    if settings.environment == "production":
        print("⚠️  Warning: Production mode but minified assets not found. Run 'python build.py' first.")

# Include routers
app.include_router(ui_router)  # UI routes first (for root path)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(crypto_asset_router)
app.include_router(portfolio_router)
app.include_router(transaction_router)
app.include_router(portfolio_aggregate_router)
app.include_router(bitso_router)
# app.include_router(websocket_router)  # WebSocket routes commented out for now


@app.get("/api")
async def api_info():
    return {
        "message": "Welcome to MyCrypto API v3.0 - Clean Architecture",
        "architecture": "Clean Architecture with Domain-Driven Design",
        "layers": [
            "Domain Layer - Core business entities and rules",
            "Application Layer - Use cases and business logic orchestration", 
            "Infrastructure Layer - Database implementations and external services",
            "Presentation Layer - FastAPI routes and DTOs"
        ]
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "database": "connected",
        "architecture": "clean"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
