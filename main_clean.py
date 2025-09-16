from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import db_factory
from presentation.api.user_routes import router as user_router
from presentation.api.crypto_asset_routes import router as crypto_asset_router
from presentation.api.portfolio_routes import router as portfolio_router
from auth.routes import router as auth_router


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

# Include routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(crypto_asset_router)
app.include_router(portfolio_router)


@app.get("/")
async def root():
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
