"""
Bitso API Models and DTOs
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal


class BitsoTickerResponse(BaseModel):
    """Bitso ticker response model"""
    book: str
    volume: str
    high: str
    last: str
    low: str
    vwap: str
    ask: str
    bid: str
    created_at: datetime


class BitsoOrderBookEntry(BaseModel):
    """Order book entry model"""
    book: str
    price: str
    amount: str


class BitsoOrderBookResponse(BaseModel):
    """Bitso order book response model"""
    asks: List[BitsoOrderBookEntry]
    bids: List[BitsoOrderBookEntry]
    updated_at: datetime
    sequence: str


class BitsoTradeResponse(BaseModel):
    """Bitso trade response model"""
    book: str
    created_at: datetime
    amount: str
    maker_side: str
    price: str
    tid: int


class BitsoBalanceResponse(BaseModel):
    """Bitso balance response model"""
    currency: str
    available: str
    locked: str
    total: str


class BitsoAccountInfoResponse(BaseModel):
    """Bitso account info response model"""
    client_id: str
    first_name: str
    last_name: str
    status: str
    daily_limit: str
    monthly_limit: str
    daily_remaining: str
    monthly_remaining: str
    cellphone_number: str
    cellphone_number_stored: str
    email_stored: str
    official_id: str
    proof_of_residency: str
    signed_contract: str
    origin_of_funds: str


class BitsoOrderRequest(BaseModel):
    """Bitso order request model"""
    book: str
    side: str  # buy or sell
    type: str  # market or limit
    amount: Optional[str] = None
    price: Optional[str] = None
    minor: Optional[str] = None  # For market orders


class BitsoOrderResponse(BaseModel):
    """Bitso order response model"""
    oid: str
    book: str
    original_amount: str
    unfilled_amount: str
    original_value: str
    created_at: datetime
    updated_at: datetime
    price: str
    side: str
    status: str
    type: str


class BitsoWithdrawalRequest(BaseModel):
    """Bitso withdrawal request model"""
    currency: str
    amount: str
    address: str
    destination_tag: Optional[str] = None


class BitsoWithdrawalResponse(BaseModel):
    """Bitso withdrawal response model"""
    wid: str
    status: str
    created_at: datetime
    currency: str
    amount: str
    method: str
    details: Dict[str, Any]


class BitsoFeeResponse(BaseModel):
    """Bitso fee response model"""
    book: str
    fee_decimal: str
    fee_percent: str


class BitsoApiResponse(BaseModel):
    """Generic Bitso API response wrapper"""
    success: bool
    payload: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


# Market Data DTOs for internal use
class MarketDataRequest(BaseModel):
    """Market data request DTO"""
    book: str
    limit: Optional[int] = 100


class TickerRequest(BaseModel):
    """Ticker request DTO"""
    book: Optional[str] = None  # If None, get all tickers


class OrderBookRequest(BaseModel):
    """Order book request DTO"""
    book: str
    aggregate: Optional[bool] = True


class TradesRequest(BaseModel):
    """Trades request DTO"""
    book: str
    marker: Optional[str] = None
    sort: Optional[str] = "desc"
    limit: Optional[int] = 100


# Trading DTOs
class PlaceOrderRequest(BaseModel):
    """Place order request DTO"""
    book: str
    side: str  # buy or sell
    order_type: str = Field(alias="type")  # market or limit
    amount: Optional[Decimal] = None
    price: Optional[Decimal] = None
    minor: Optional[Decimal] = None  # For market buy orders


class CancelOrderRequest(BaseModel):
    """Cancel order request DTO"""
    order_id: str


class OrderStatusRequest(BaseModel):
    """Order status request DTO"""
    order_id: str


# Account DTOs
class BalanceRequest(BaseModel):
    """Balance request DTO"""
    currency: Optional[str] = None


class WithdrawRequest(BaseModel):
    """Withdraw request DTO"""
    currency: str
    amount: Decimal
    address: str
    destination_tag: Optional[str] = None


# Response DTOs for API endpoints
class MarketTickerResponseDto(BaseModel):
    """Market ticker response DTO"""
    book: str
    volume: Decimal
    high: Decimal
    last: Decimal
    low: Decimal
    vwap: Decimal
    ask: Decimal
    bid: Decimal
    created_at: datetime


class MarketOrderBookResponseDto(BaseModel):
    """Market order book response DTO"""
    book: str
    asks: List[Dict[str, str]]
    bids: List[Dict[str, str]]
    updated_at: datetime
    sequence: str


class MarketTradeResponseDto(BaseModel):
    """Market trade response DTO"""
    book: str
    created_at: datetime
    amount: Decimal
    maker_side: str
    price: Decimal
    trade_id: int


class AccountBalanceResponseDto(BaseModel):
    """Account balance response DTO"""
    currency: str
    available: Decimal
    locked: Decimal
    total: Decimal


class TradingOrderResponseDto(BaseModel):
    """Trading order response DTO"""
    order_id: str
    book: str
    original_amount: Decimal
    unfilled_amount: Decimal
    original_value: Decimal
    created_at: datetime
    updated_at: datetime
    price: Decimal
    side: str
    status: str
    order_type: str
