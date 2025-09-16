from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from application.dtos.crypto_asset_dtos import CryptoAssetResponse


class CryptoAssetCreateSchema(BaseModel):
    """Schema for creating a new crypto asset"""
    symbol: str
    name: str
    current_price: Optional[float] = None


class CryptoAssetUpdateSchema(BaseModel):
    """Schema for updating crypto asset information"""
    name: Optional[str] = None
    current_price: Optional[float] = None


class CryptoAssetResponseSchema(BaseModel):
    """Schema for crypto asset response"""
    id: str
    symbol: str
    name: str
    current_price: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dto(cls, dto: CryptoAssetResponse) -> 'CryptoAssetResponseSchema':
        """Create schema from DTO"""
        return cls(
            id=dto.id,
            symbol=dto.symbol,
            name=dto.name,
            current_price=dto.current_price,
            created_at=dto.created_at,
            updated_at=dto.updated_at
        )
    
    class Config:
        from_attributes = True
