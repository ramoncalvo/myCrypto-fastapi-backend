"""
Bitso API Schemas for FastAPI endpoints
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


# Request Schemas
class TickerRequestSchema(BaseModel):
    """Ticker request schema"""
    book: Optional[str] = Field(None, description="Trading book (e.g., 'btc_mxn'). If not provided, returns all tickers")


class OrderBookRequestSchema(BaseModel):
    """Order book request schema"""
    book: str = Field(..., description="Trading book (e.g., 'btc_mxn')")
    aggregate: Optional[bool] = Field(True, description="Whether to aggregate orders at same price level")


class TradesRequestSchema(BaseModel):
    """Trades request schema"""
    book: str = Field(..., description="Trading book (e.g., 'btc_mxn')")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Number of trades to return")
    marker: Optional[str] = Field(None, description="Marker for pagination")
    sort: Optional[str] = Field("desc", description="Sort order: 'asc' or 'desc'")


class PlaceOrderRequestSchema(BaseModel):
    """Place order request schema"""
    book: str = Field(..., description="Trading book (e.g., 'btc_mxn')")
    side: str = Field(..., description="Order side: 'buy' or 'sell'")
    order_type: str = Field(..., alias="type", description="Order type: 'market' or 'limit'")
    amount: Optional[Decimal] = Field(None, description="Amount in base currency (for limit orders or market sell)")
    price: Optional[Decimal] = Field(None, description="Price per unit (for limit orders)")
    minor: Optional[Decimal] = Field(None, description="Amount in quote currency (for market buy orders)")


class CancelOrderRequestSchema(BaseModel):
    """Cancel order request schema"""
    order_id: str = Field(..., description="Order ID to cancel")


class MarketBuyRequestSchema(BaseModel):
    """Market buy request schema"""
    book: str = Field(..., description="Trading book (e.g., 'btc_mxn')")
    amount_mxn: Decimal = Field(..., gt=0, description="Amount in MXN to spend")


class MarketSellRequestSchema(BaseModel):
    """Market sell request schema"""
    book: str = Field(..., description="Trading book (e.g., 'btc_mxn')")
    amount: Decimal = Field(..., gt=0, description="Amount in base currency to sell")


class LimitOrderRequestSchema(BaseModel):
    """Limit order request schema"""
    book: str = Field(..., description="Trading book (e.g., 'btc_mxn')")
    side: str = Field(..., description="Order side: 'buy' or 'sell'")
    amount: Decimal = Field(..., gt=0, description="Amount in base currency")
    price: Decimal = Field(..., gt=0, description="Price per unit")


# Response Schemas
class TickerResponseSchema(BaseModel):
    """Ticker response schema"""
    book: str
    volume: Decimal
    high: Decimal
    last: Decimal
    low: Decimal
    vwap: Decimal
    ask: Decimal
    bid: Decimal
    created_at: datetime


class OrderBookResponseSchema(BaseModel):
    """Order book response schema"""
    book: str
    asks: List[Dict[str, str]]
    bids: List[Dict[str, str]]
    updated_at: datetime
    sequence: str


class TradeResponseSchema(BaseModel):
    """Trade response schema"""
    book: str
    created_at: datetime
    amount: Decimal
    maker_side: str
    price: Decimal
    trade_id: int


class BalanceResponseSchema(BaseModel):
    """Balance response schema"""
    currency: str
    available: Decimal
    locked: Decimal
    total: Decimal
    current_price_mxn: Optional[Decimal] = None
    value_mxn: Optional[Decimal] = None


class OrderResponseSchema(BaseModel):
    """Order response schema"""
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


class MarketOverviewResponseSchema(BaseModel):
    """Market overview response schema"""
    available_books: int
    market_data: Dict[str, Any]
    timestamp: str


class BookDetailsResponseSchema(BaseModel):
    """Book details response schema"""
    book: str
    ticker: Dict[str, Any]
    order_book: Dict[str, Any]
    recent_trades: List[Dict[str, Any]]
    timestamp: str


class PortfolioSummaryResponseSchema(BaseModel):
    """Portfolio summary response schema"""
    total_value_mxn: Decimal
    balances: List[Dict[str, Any]]
    currencies_count: int
    timestamp: str


class TradingOperationResponseSchema(BaseModel):
    """Trading operation response schema"""
    order_id: Optional[str] = None
    book: Optional[str] = None
    side: Optional[str] = None
    type: Optional[str] = None
    amount: Optional[Decimal] = None
    amount_mxn: Optional[Decimal] = None
    price: Optional[Decimal] = None
    status: Optional[str] = None
    cancelled: Optional[bool] = None
    created_at: Optional[str] = None
    message: str
    timestamp: Optional[str] = None


class TradingHistoryResponseSchema(BaseModel):
    """Trading history response schema"""
    trades: List[Dict[str, Any]]
    total_trades: int
    book_filter: Optional[str]
    timestamp: str


class OpenOrdersSummaryResponseSchema(BaseModel):
    """Open orders summary response schema"""
    open_orders: List[Dict[str, Any]]
    total_orders: int
    total_value: Decimal
    timestamp: str


class AccountInfoResponseSchema(BaseModel):
    """Account info response schema"""
    client_id: str
    first_name: str
    last_name: str
    status: str
    daily_limit: str
    monthly_limit: str
    daily_remaining: str
    monthly_remaining: str
    email_stored: str
    cellphone_number_stored: str


class AvailableBooksResponseSchema(BaseModel):
    """Available books response schema"""
    book: str
    minimum_amount: str
    maximum_amount: str
    minimum_price: str
    maximum_price: str
    minimum_value: str
    maximum_value: str


class TradingFeesResponseSchema(BaseModel):
    """Trading fees response schema"""
    book: str
    fee_decimal: str
    fee_percent: str
