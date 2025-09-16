from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from domain.entities.portfolio import Portfolio


@dataclass
class CreatePortfolioRequest:
    """DTO for creating a new portfolio entry"""
    user_id: str
    asset_id: str
    quantity: float
    purchase_price: float


@dataclass
class UpdatePortfolioRequest:
    """DTO for updating portfolio entry information"""
    quantity: Optional[float] = None
    purchase_price: Optional[float] = None


@dataclass
class PortfolioResponse:
    """DTO for portfolio response"""
    id: str
    user_id: str
    asset_id: str
    quantity: float
    purchase_price: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_entity(cls, portfolio: Portfolio) -> 'PortfolioResponse':
        """Create DTO from domain entity"""
        return cls(
            id=str(portfolio.id),
            user_id=str(portfolio.user_id),
            asset_id=str(portfolio.asset_id),
            quantity=portfolio.quantity_as_float,
            purchase_price=portfolio.purchase_price_as_float,
            created_at=portfolio.created_at,
            updated_at=portfolio.updated_at
        )
