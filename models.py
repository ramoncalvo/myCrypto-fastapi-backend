from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Database-agnostic models (DTOs)
class UserBase(BaseModel):
    email: str
    name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class CryptoAssetBase(BaseModel):
    symbol: str
    name: str
    current_price: Optional[float] = None

class CryptoAssetCreate(CryptoAssetBase):
    pass

class CryptoAssetUpdate(BaseModel):
    symbol: Optional[str] = None
    name: Optional[str] = None
    current_price: Optional[float] = None

class CryptoAssetResponse(CryptoAssetBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class PortfolioBase(BaseModel):
    user_id: str
    asset_id: str
    quantity: float
    purchase_price: float

class PortfolioCreate(PortfolioBase):
    pass

class PortfolioUpdate(BaseModel):
    user_id: Optional[str] = None
    asset_id: Optional[str] = None
    quantity: Optional[float] = None
    purchase_price: Optional[float] = None

class PortfolioResponse(PortfolioBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Database entity models (for internal use)
class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    email: str
    name: str
    password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True

class CryptoAsset(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    symbol: str
    name: str
    current_price: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True

class Portfolio(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    asset_id: str
    quantity: float
    purchase_price: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
