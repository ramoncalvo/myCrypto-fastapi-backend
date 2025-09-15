from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from contextlib import asynccontextmanager

from database import db_factory
from models import (
    UserCreate, UserUpdate, UserResponse,
    CryptoAssetCreate, CryptoAssetUpdate, CryptoAssetResponse,
    PortfolioCreate, PortfolioUpdate, PortfolioResponse
)
from auth.routes import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db_factory.connect()
    yield
    # Shutdown
    await db_factory.disconnect()

app = FastAPI(
    title="MyCrypto API",
    description="A FastAPI application for cryptocurrency portfolio management with pluggable database support",
    version="2.0.0",
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

# Include authentication routes
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Welcome to MyCrypto API v2.0 - Database Agnostic"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

# User endpoints
@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    try:
        user_data = user.model_dump()
        # In production, hash the password here
        result = await db_factory.user_repository.create(user_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 100):
    try:
        users = await db_factory.user_repository.get_all(skip=skip, limit=limit)
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    try:
        user = await db_factory.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate):
    try:
        update_data = user_update.model_dump(exclude_unset=True)
        user = await db_factory.user_repository.update(user_id, update_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    try:
        success = await db_factory.user_repository.delete(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str):
    try:
        user = await db_factory.user_repository.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Crypto Asset endpoints
@app.post("/crypto-assets/", response_model=CryptoAssetResponse)
async def create_crypto_asset(asset: CryptoAssetCreate):
    try:
        asset_data = asset.model_dump()
        result = await db_factory.crypto_repository.create(asset_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/crypto-assets/", response_model=List[CryptoAssetResponse])
async def get_crypto_assets(skip: int = 0, limit: int = 100):
    try:
        assets = await db_factory.crypto_repository.get_all(skip=skip, limit=limit)
        return assets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/crypto-assets/{asset_id}", response_model=CryptoAssetResponse)
async def get_crypto_asset(asset_id: str):
    try:
        asset = await db_factory.crypto_repository.get_by_id(asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Crypto asset not found")
        return asset
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/crypto-assets/{asset_id}", response_model=CryptoAssetResponse)
async def update_crypto_asset(asset_id: str, asset_update: CryptoAssetUpdate):
    try:
        update_data = asset_update.model_dump(exclude_unset=True)
        asset = await db_factory.crypto_repository.update(asset_id, update_data)
        if not asset:
            raise HTTPException(status_code=404, detail="Crypto asset not found")
        return asset
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/crypto-assets/{asset_id}")
async def delete_crypto_asset(asset_id: str):
    try:
        success = await db_factory.crypto_repository.delete(asset_id)
        if not success:
            raise HTTPException(status_code=404, detail="Crypto asset not found")
        return {"message": "Crypto asset deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/crypto-assets/symbol/{symbol}", response_model=CryptoAssetResponse)
async def get_crypto_asset_by_symbol(symbol: str):
    try:
        asset = await db_factory.crypto_repository.get_by_symbol(symbol)
        if not asset:
            raise HTTPException(status_code=404, detail="Crypto asset not found")
        return asset
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Portfolio endpoints
@app.post("/portfolio/", response_model=PortfolioResponse)
async def create_portfolio_entry(portfolio: PortfolioCreate):
    try:
        portfolio_data = portfolio.model_dump()
        result = await db_factory.portfolio_repository.create(portfolio_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/", response_model=List[PortfolioResponse])
async def get_all_portfolio_entries(skip: int = 0, limit: int = 100):
    try:
        entries = await db_factory.portfolio_repository.get_all(skip=skip, limit=limit)
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio_entry(portfolio_id: str):
    try:
        entry = await db_factory.portfolio_repository.get_by_id(portfolio_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Portfolio entry not found")
        return entry
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/portfolio/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio_entry(portfolio_id: str, portfolio_update: PortfolioUpdate):
    try:
        update_data = portfolio_update.model_dump(exclude_unset=True)
        entry = await db_factory.portfolio_repository.update(portfolio_id, update_data)
        if not entry:
            raise HTTPException(status_code=404, detail="Portfolio entry not found")
        return entry
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/portfolio/{portfolio_id}")
async def delete_portfolio_entry(portfolio_id: str):
    try:
        success = await db_factory.portfolio_repository.delete(portfolio_id)
        if not success:
            raise HTTPException(status_code=404, detail="Portfolio entry not found")
        return {"message": "Portfolio entry deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/user/{user_id}", response_model=List[PortfolioResponse])
async def get_user_portfolio(user_id: str):
    try:
        entries = await db_factory.portfolio_repository.get_by_user_id(user_id)
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
