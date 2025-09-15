from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

# Custom ObjectId type for Pydantic
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid objectid')
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')
    
    class Config:
        from_attributes = True

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

# Authentication Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True
