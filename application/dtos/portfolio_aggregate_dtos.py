from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from decimal import Decimal


@dataclass
class CreatePortfolioRequest:
    """DTO for creating a portfolio"""
    name: str
    description: Optional[str] = None


@dataclass
class UpdatePortfolioRequest:
    """DTO for updating a portfolio"""
    name: Optional[str] = None
    description: Optional[str] = None


@dataclass
class AssetHoldingResponse:
    """DTO for asset holding response"""
    asset_id: str
    symbol: str
    name: str
    total_quantity: float
    average_cost: float
    current_price: float
    current_value: float
    cost_basis: float
    profit_loss: float
    profit_loss_percentage: float
    transaction_count: int


@dataclass
class PortfolioSummaryResponse:
    """DTO for portfolio summary response"""
    total_value: float
    total_cost_basis: float
    total_profit_loss: float
    total_profit_loss_percentage: float
    asset_count: int
    last_updated: datetime


@dataclass
class PortfolioResponse:
    """DTO for portfolio response"""
    id: str
    user_id: str
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


@dataclass
class PortfolioDetailResponse:
    """DTO for detailed portfolio response"""
    id: str
    user_id: str
    name: str
    description: Optional[str]
    holdings: List[AssetHoldingResponse]
    summary: PortfolioSummaryResponse
    created_at: datetime
    updated_at: Optional[datetime]


@dataclass
class PortfolioPerformanceResponse:
    """DTO for portfolio performance metrics"""
    summary: PortfolioSummaryResponse
    transaction_stats: Dict[str, any]
    pnl_breakdown: Dict[str, float]
    top_performers: List[AssetHoldingResponse]
    worst_performers: List[AssetHoldingResponse]


@dataclass
class PortfolioFilterRequest:
    """DTO for filtering portfolios"""
    skip: int = 0
    limit: int = 100
