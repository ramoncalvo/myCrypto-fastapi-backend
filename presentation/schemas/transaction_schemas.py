from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from enum import Enum


class TransactionTypeEnum(str, Enum):
    """Transaction type enumeration for API"""
    BUY = "buy"
    SELL = "sell"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"


class TransactionStatusEnum(str, Enum):
    """Transaction status enumeration for API"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CreateTransactionSchema(BaseModel):
    """Schema for creating a transaction"""
    portfolio_id: str = Field(..., description="Portfolio ID")
    asset_id: str = Field(..., description="Asset ID")
    transaction_type: TransactionTypeEnum = Field(..., description="Transaction type")
    quantity: float = Field(..., gt=0, description="Quantity must be positive")
    price: float = Field(..., ge=0, description="Price cannot be negative")
    fees: float = Field(0.0, ge=0, description="Fees cannot be negative")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")

    class Config:
        schema_extra = {
            "example": {
                "portfolio_id": "60d5ecb54f8b4c001f8b4567",
                "asset_id": "60d5ecb54f8b4c001f8b4568",
                "transaction_type": "buy",
                "quantity": 0.5,
                "price": 45000.0,
                "fees": 25.0,
                "notes": "Initial BTC purchase"
            }
        }


class UpdateTransactionSchema(BaseModel):
    """Schema for updating a transaction"""
    quantity: Optional[float] = Field(None, gt=0, description="Quantity must be positive")
    price: Optional[float] = Field(None, ge=0, description="Price cannot be negative")
    fees: Optional[float] = Field(None, ge=0, description="Fees cannot be negative")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")

    class Config:
        schema_extra = {
            "example": {
                "quantity": 0.75,
                "price": 46000.0,
                "fees": 30.0,
                "notes": "Updated quantity and price"
            }
        }


class ExecuteTransactionSchema(BaseModel):
    """Schema for executing a transaction"""
    transaction_id: str = Field(..., description="Transaction ID to execute")

    class Config:
        schema_extra = {
            "example": {
                "transaction_id": "60d5ecb54f8b4c001f8b4569"
            }
        }


class CancelTransactionSchema(BaseModel):
    """Schema for cancelling a transaction"""
    transaction_id: str = Field(..., description="Transaction ID to cancel")
    reason: Optional[str] = Field(None, max_length=200, description="Cancellation reason")

    class Config:
        schema_extra = {
            "example": {
                "transaction_id": "60d5ecb54f8b4c001f8b4569",
                "reason": "Changed mind about purchase"
            }
        }


class TransactionResponseSchema(BaseModel):
    """Schema for transaction response"""
    id: str
    user_id: str
    portfolio_id: str
    asset_id: str
    transaction_type: str
    quantity: float
    price: float
    total_amount: float
    fees: float
    status: str
    created_at: datetime
    executed_at: Optional[datetime]
    updated_at: Optional[datetime]
    notes: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "id": "60d5ecb54f8b4c001f8b4569",
                "user_id": "60d5ecb54f8b4c001f8b4566",
                "portfolio_id": "60d5ecb54f8b4c001f8b4567",
                "asset_id": "60d5ecb54f8b4c001f8b4568",
                "transaction_type": "buy",
                "quantity": 0.5,
                "price": 45000.0,
                "total_amount": 22525.0,
                "fees": 25.0,
                "status": "completed",
                "created_at": "2023-06-25T10:30:00Z",
                "executed_at": "2023-06-25T10:31:00Z",
                "updated_at": "2023-06-25T10:31:00Z",
                "notes": "Initial BTC purchase"
            }
        }


class TransactionStatsResponseSchema(BaseModel):
    """Schema for transaction statistics response"""
    total_transactions: int
    completed_transactions: int
    buy_transactions: int
    sell_transactions: int
    total_fees: float
    total_buy_amount: float
    total_sell_amount: float

    class Config:
        schema_extra = {
            "example": {
                "total_transactions": 25,
                "completed_transactions": 23,
                "buy_transactions": 15,
                "sell_transactions": 8,
                "total_fees": 125.50,
                "total_buy_amount": 50000.0,
                "total_sell_amount": 30000.0
            }
        }


class TransactionFilterSchema(BaseModel):
    """Schema for filtering transactions"""
    asset_id: Optional[str] = Field(None, description="Filter by asset ID")
    transaction_type: Optional[TransactionTypeEnum] = Field(None, description="Filter by transaction type")
    status: Optional[TransactionStatusEnum] = Field(None, description="Filter by status")
    start_date: Optional[datetime] = Field(None, description="Start date for filtering")
    end_date: Optional[datetime] = Field(None, description="End date for filtering")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records to return")

    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('end_date must be after start_date')
        return v

    class Config:
        schema_extra = {
            "example": {
                "asset_id": "60d5ecb54f8b4c001f8b4568",
                "transaction_type": "buy",
                "status": "completed",
                "start_date": "2023-06-01T00:00:00Z",
                "end_date": "2023-06-30T23:59:59Z",
                "skip": 0,
                "limit": 50
            }
        }
