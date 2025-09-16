from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal


class CreatePortfolioSchema(BaseModel):
    """Schema for creating a portfolio"""
    name: str = Field(..., min_length=1, max_length=100, description="Portfolio name")
    description: Optional[str] = Field(None, max_length=500, description="Portfolio description")

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Portfolio name cannot be empty')
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "name": "My Crypto Portfolio",
                "description": "Long-term cryptocurrency investment portfolio"
            }
        }


class UpdatePortfolioSchema(BaseModel):
    """Schema for updating a portfolio"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Portfolio name")
    description: Optional[str] = Field(None, max_length=500, description="Portfolio description")

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Portfolio name cannot be empty')
        return v.strip() if v else v

    class Config:
        schema_extra = {
            "example": {
                "name": "Updated Portfolio Name",
                "description": "Updated description"
            }
        }


class AssetHoldingResponseSchema(BaseModel):
    """Schema for asset holding response"""
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

    class Config:
        schema_extra = {
            "example": {
                "asset_id": "60d5ecb54f8b4c001f8b4568",
                "symbol": "BTC",
                "name": "Bitcoin",
                "total_quantity": 0.5,
                "average_cost": 45000.0,
                "current_price": 47000.0,
                "current_value": 23500.0,
                "cost_basis": 22500.0,
                "profit_loss": 1000.0,
                "profit_loss_percentage": 4.44,
                "transaction_count": 3
            }
        }


class PortfolioSummaryResponseSchema(BaseModel):
    """Schema for portfolio summary response"""
    total_value: float
    total_cost_basis: float
    total_profit_loss: float
    total_profit_loss_percentage: float
    asset_count: int
    last_updated: datetime

    class Config:
        schema_extra = {
            "example": {
                "total_value": 75000.0,
                "total_cost_basis": 70000.0,
                "total_profit_loss": 5000.0,
                "total_profit_loss_percentage": 7.14,
                "asset_count": 5,
                "last_updated": "2023-06-25T10:30:00Z"
            }
        }


class PortfolioResponseSchema(BaseModel):
    """Schema for portfolio response"""
    id: str
    user_id: str
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        schema_extra = {
            "example": {
                "id": "60d5ecb54f8b4c001f8b4567",
                "user_id": "60d5ecb54f8b4c001f8b4566",
                "name": "My Crypto Portfolio",
                "description": "Long-term cryptocurrency investment portfolio",
                "created_at": "2023-06-25T10:30:00Z",
                "updated_at": "2023-06-25T12:00:00Z"
            }
        }


class PortfolioDetailResponseSchema(BaseModel):
    """Schema for detailed portfolio response"""
    id: str
    user_id: str
    name: str
    description: Optional[str]
    holdings: List[AssetHoldingResponseSchema]
    summary: PortfolioSummaryResponseSchema
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        schema_extra = {
            "example": {
                "id": "60d5ecb54f8b4c001f8b4567",
                "user_id": "60d5ecb54f8b4c001f8b4566",
                "name": "My Crypto Portfolio",
                "description": "Long-term cryptocurrency investment portfolio",
                "holdings": [
                    {
                        "asset_id": "60d5ecb54f8b4c001f8b4568",
                        "symbol": "BTC",
                        "name": "Bitcoin",
                        "total_quantity": 0.5,
                        "average_cost": 45000.0,
                        "current_price": 47000.0,
                        "current_value": 23500.0,
                        "cost_basis": 22500.0,
                        "profit_loss": 1000.0,
                        "profit_loss_percentage": 4.44,
                        "transaction_count": 3
                    }
                ],
                "summary": {
                    "total_value": 75000.0,
                    "total_cost_basis": 70000.0,
                    "total_profit_loss": 5000.0,
                    "total_profit_loss_percentage": 7.14,
                    "asset_count": 5,
                    "last_updated": "2023-06-25T10:30:00Z"
                },
                "created_at": "2023-06-25T10:30:00Z",
                "updated_at": "2023-06-25T12:00:00Z"
            }
        }


class PortfolioPerformanceResponseSchema(BaseModel):
    """Schema for portfolio performance metrics"""
    summary: PortfolioSummaryResponseSchema
    transaction_stats: Dict[str, Any]
    pnl_breakdown: Dict[str, float]
    top_performers: List[AssetHoldingResponseSchema]
    worst_performers: List[AssetHoldingResponseSchema]

    class Config:
        schema_extra = {
            "example": {
                "summary": {
                    "total_value": 75000.0,
                    "total_cost_basis": 70000.0,
                    "total_profit_loss": 5000.0,
                    "total_profit_loss_percentage": 7.14,
                    "asset_count": 5,
                    "last_updated": "2023-06-25T10:30:00Z"
                },
                "transaction_stats": {
                    "total_transactions": 25,
                    "completed_transactions": 23,
                    "buy_transactions": 15,
                    "sell_transactions": 8,
                    "total_fees": 125.50
                },
                "pnl_breakdown": {
                    "realized_pnl": 2000.0,
                    "unrealized_pnl": 3000.0,
                    "total_pnl": 5000.0
                },
                "top_performers": [],
                "worst_performers": []
            }
        }


class PortfolioFilterSchema(BaseModel):
    """Schema for filtering portfolios"""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records to return")

    class Config:
        schema_extra = {
            "example": {
                "skip": 0,
                "limit": 50
            }
        }


class PortfolioOverviewResponseSchema(BaseModel):
    """Schema for user portfolio overview"""
    total_portfolios: int
    total_value: float
    total_cost_basis: float
    total_profit_loss: float
    total_profit_loss_percentage: float
    total_assets: int
    portfolios: List[Dict[str, Any]]

    class Config:
        schema_extra = {
            "example": {
                "total_portfolios": 3,
                "total_value": 150000.0,
                "total_cost_basis": 140000.0,
                "total_profit_loss": 10000.0,
                "total_profit_loss_percentage": 7.14,
                "total_assets": 15,
                "portfolios": [
                    {
                        "id": "60d5ecb54f8b4c001f8b4567",
                        "name": "Main Portfolio",
                        "summary": {
                            "total_value": 75000.0,
                            "total_cost_basis": 70000.0,
                            "total_profit_loss": 5000.0,
                            "total_profit_loss_percentage": 7.14,
                            "asset_count": 5,
                            "last_updated": "2023-06-25T10:30:00Z"
                        }
                    }
                ]
            }
        }
