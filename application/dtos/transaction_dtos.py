from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal
from domain.entities.transaction import TransactionType, TransactionStatus


@dataclass
class CreateTransactionRequest:
    """DTO for creating a transaction"""
    portfolio_id: str
    asset_id: str
    transaction_type: str  # "buy" or "sell"
    quantity: float
    price: float
    fees: float = 0.0
    notes: Optional[str] = None


@dataclass
class UpdateTransactionRequest:
    """DTO for updating a transaction"""
    quantity: Optional[float] = None
    price: Optional[float] = None
    fees: Optional[float] = None
    notes: Optional[str] = None


@dataclass
class ExecuteTransactionRequest:
    """DTO for executing a transaction"""
    transaction_id: str


@dataclass
class CancelTransactionRequest:
    """DTO for cancelling a transaction"""
    transaction_id: str
    reason: Optional[str] = None


@dataclass
class TransactionResponse:
    """DTO for transaction response"""
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


@dataclass
class TransactionStatsResponse:
    """DTO for transaction statistics"""
    total_transactions: int
    completed_transactions: int
    buy_transactions: int
    sell_transactions: int
    total_fees: float
    total_buy_amount: float
    total_sell_amount: float


@dataclass
class TransactionFilterRequest:
    """DTO for filtering transactions"""
    asset_id: Optional[str] = None
    transaction_type: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = 0
    limit: int = 100
