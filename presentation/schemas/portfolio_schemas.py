from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from application.dtos.portfolio_dtos import PortfolioResponse


class PortfolioCreateSchema(BaseModel):
    """Schema for creating a new portfolio entry"""
    user_id: str
    asset_id: str
    quantity: float
    purchase_price: float


class PortfolioUpdateSchema(BaseModel):
    """Schema for updating portfolio entry information"""
    quantity: Optional[float] = None
    purchase_price: Optional[float] = None


class PortfolioResponseSchema(BaseModel):
    """Schema for portfolio response"""
    id: str
    user_id: str
    asset_id: str
    quantity: float
    purchase_price: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dto(cls, dto: PortfolioResponse) -> 'PortfolioResponseSchema':
        """Create schema from DTO"""
        return cls(
            id=dto.id,
            user_id=dto.user_id,
            asset_id=dto.asset_id,
            quantity=dto.quantity,
            purchase_price=dto.purchase_price,
            created_at=dto.created_at,
            updated_at=dto.updated_at
        )
    
    class Config:
        from_attributes = True
