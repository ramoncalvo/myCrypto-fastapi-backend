"""
Bitso Service Layer - Business logic for Bitso API integration
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import logging

from .bitso_client import BitsoClient, BitsoApiError
from .models import (
    MarketTickerResponseDto, MarketOrderBookResponseDto, MarketTradeResponseDto,
    AccountBalanceResponseDto, TradingOrderResponseDto,
    TickerRequest, OrderBookRequest, TradesRequest, PlaceOrderRequest,
    BalanceRequest, CancelOrderRequest, OrderStatusRequest
)

logger = logging.getLogger(__name__)


class BitsoService:
    """Service layer for Bitso API operations"""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.api_key = api_key
        self.api_secret = api_secret
    
    async def _get_client(self) -> BitsoClient:
        """Get configured Bitso client"""
        return BitsoClient(self.api_key, self.api_secret)
    
    # Market Data Services
    
    async def get_available_books(self) -> List[Dict[str, Any]]:
        """Get list of available trading pairs"""
        try:
            async with await self._get_client() as client:
                books = await client.get_available_books()
                return books
        except BitsoApiError as e:
            logger.error(f"Failed to get available books: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting available books: {str(e)}")
            raise BitsoApiError(f"Service error: {str(e)}")
    
    async def get_ticker(self, request: TickerRequest) -> List[MarketTickerResponseDto]:
        """Get ticker information for one or all books"""
        try:
            async with await self._get_client() as client:
                tickers = await client.get_ticker(request.book)
                
                result = []
                for ticker in tickers:
                    result.append(MarketTickerResponseDto(
                        book=ticker.book,
                        volume=Decimal(ticker.volume),
                        high=Decimal(ticker.high),
                        last=Decimal(ticker.last),
                        low=Decimal(ticker.low),
                        vwap=Decimal(ticker.vwap),
                        ask=Decimal(ticker.ask),
                        bid=Decimal(ticker.bid),
                        created_at=ticker.created_at
                    ))
                
                return result
        except BitsoApiError as e:
            logger.error(f"Failed to get ticker: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting ticker: {str(e)}")
            raise BitsoApiError(f"Service error: {str(e)}")
    
    async def get_order_book(self, request: OrderBookRequest) -> MarketOrderBookResponseDto:
        """Get order book for a specific trading pair"""
        try:
            async with await self._get_client() as client:
                order_book = await client.get_order_book(request.book, request.aggregate)
                
                return MarketOrderBookResponseDto(
                    book=request.book,
                    asks=[{"price": ask.price, "amount": ask.amount} for ask in order_book.asks],
                    bids=[{"price": bid.price, "amount": bid.amount} for bid in order_book.bids],
                    updated_at=order_book.updated_at,
                    sequence=order_book.sequence
                )
        except BitsoApiError as e:
            logger.error(f"Failed to get order book: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting order book: {str(e)}")
            raise BitsoApiError(f"Service error: {str(e)}")
    
    async def get_trades(self, request: TradesRequest) -> List[MarketTradeResponseDto]:
        """Get recent trades for a trading pair"""
        try:
            async with await self._get_client() as client:
                trades = await client.get_trades(
                    request.book, 
                    request.marker, 
                    request.sort, 
                    request.limit
                )
                
                result = []
                for trade in trades:
                    result.append(MarketTradeResponseDto(
                        book=trade.book,
                        created_at=trade.created_at,
                        amount=Decimal(trade.amount),
                        maker_side=trade.maker_side,
                        price=Decimal(trade.price),
                        trade_id=trade.tid
                    ))
                
                return result
        except BitsoApiError as e:
            logger.error(f"Failed to get trades: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting trades: {str(e)}")
            raise BitsoApiError(f"Service error: {str(e)}")
    
    # Account Services
    
    async def get_balances(self, request: BalanceRequest) -> List[AccountBalanceResponseDto]:
        """Get account balances"""
        try:
            async with await self._get_client() as client:
                balances = await client.get_balances()
                
                result = []
                for balance in balances:
                    # Filter by currency if specified
                    if request.currency and balance.currency != request.currency:
                        continue
                    
                    result.append(AccountBalanceResponseDto(
                        currency=balance.currency,
                        available=Decimal(balance.available),
                        locked=Decimal(balance.locked),
                        total=Decimal(balance.total)
                    ))
                
                return result
        except BitsoApiError as e:
            logger.error(f"Failed to get balances: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting balances: {str(e)}")
            raise BitsoApiError(f"Service error: {str(e)}")
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        try:
            async with await self._get_client() as client:
                account_info = await client.get_account_status()
                return {
                    "client_id": account_info.client_id,
                    "first_name": account_info.first_name,
                    "last_name": account_info.last_name,
                    "status": account_info.status,
                    "daily_limit": account_info.daily_limit,
                    "monthly_limit": account_info.monthly_limit,
                    "daily_remaining": account_info.daily_remaining,
                    "monthly_remaining": account_info.monthly_remaining,
                    "email_stored": account_info.email_stored,
                    "cellphone_number_stored": account_info.cellphone_number_stored
                }
        except BitsoApiError as e:
            logger.error(f"Failed to get account info: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting account info: {str(e)}")
            raise BitsoApiError(f"Service error: {str(e)}")
    
    # Trading Services
    
    async def place_order(self, request: PlaceOrderRequest) -> TradingOrderResponseDto:
        """Place a buy or sell order"""
        try:
            async with await self._get_client() as client:
                order = await client.place_order(
                    book=request.book,
                    side=request.side,
                    order_type=request.order_type,
                    amount=str(request.amount) if request.amount else None,
                    price=str(request.price) if request.price else None,
                    minor=str(request.minor) if request.minor else None
                )
                
                return TradingOrderResponseDto(
                    order_id=order.oid,
                    book=order.book,
                    original_amount=Decimal(order.original_amount),
                    unfilled_amount=Decimal(order.unfilled_amount),
                    original_value=Decimal(order.original_value),
                    created_at=order.created_at,
                    updated_at=order.updated_at,
                    price=Decimal(order.price),
                    side=order.side,
                    status=order.status,
                    order_type=order.type
                )
        except BitsoApiError as e:
            logger.error(f"Failed to place order: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error placing order: {str(e)}")
            raise BitsoApiError(f"Service error: {str(e)}")
    
    async def cancel_order(self, request: CancelOrderRequest) -> bool:
        """Cancel an existing order"""
        try:
            async with await self._get_client() as client:
                result = await client.cancel_order(request.order_id)
                return len(result) > 0  # Returns list of cancelled order IDs
        except BitsoApiError as e:
            logger.error(f"Failed to cancel order: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error cancelling order: {str(e)}")
            raise BitsoApiError(f"Service error: {str(e)}")
    
    async def get_open_orders(self, book: Optional[str] = None) -> List[TradingOrderResponseDto]:
        """Get open orders"""
        try:
            async with await self._get_client() as client:
                orders = await client.get_open_orders(book)
                
                result = []
                for order in orders:
                    result.append(TradingOrderResponseDto(
                        order_id=order.oid,
                        book=order.book,
                        original_amount=Decimal(order.original_amount),
                        unfilled_amount=Decimal(order.unfilled_amount),
                        original_value=Decimal(order.original_value),
                        created_at=order.created_at,
                        updated_at=order.updated_at,
                        price=Decimal(order.price),
                        side=order.side,
                        status=order.status,
                        order_type=order.type
                    ))
                
                return result
        except BitsoApiError as e:
            logger.error(f"Failed to get open orders: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting open orders: {str(e)}")
            raise BitsoApiError(f"Service error: {str(e)}")
    
    async def get_order_status(self, request: OrderStatusRequest) -> Optional[TradingOrderResponseDto]:
        """Get status of a specific order"""
        try:
            # Get all open orders and find the specific one
            open_orders = await self.get_open_orders()
            for order in open_orders:
                if order.order_id == request.order_id:
                    return order
            
            # If not found in open orders, it might be completed/cancelled
            # For now, return None - in a real implementation, you'd check order history
            return None
        except BitsoApiError as e:
            logger.error(f"Failed to get order status: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting order status: {str(e)}")
            raise BitsoApiError(f"Service error: {str(e)}")
    
    async def get_user_trades(
        self, 
        book: Optional[str] = None, 
        limit: int = 100
    ) -> List[MarketTradeResponseDto]:
        """Get user's trade history"""
        try:
            async with await self._get_client() as client:
                trades = await client.get_user_trades(book=book, limit=limit)
                
                result = []
                for trade in trades:
                    result.append(MarketTradeResponseDto(
                        book=trade.book,
                        created_at=trade.created_at,
                        amount=Decimal(trade.amount),
                        maker_side=trade.maker_side,
                        price=Decimal(trade.price),
                        trade_id=trade.tid
                    ))
                
                return result
        except BitsoApiError as e:
            logger.error(f"Failed to get user trades: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting user trades: {str(e)}")
            raise BitsoApiError(f"Service error: {str(e)}")
    
    # Utility Services
    
    async def get_trading_fees(self) -> List[Dict[str, Any]]:
        """Get trading fees for all books"""
        try:
            async with await self._get_client() as client:
                fees = await client.get_fees()
                
                result = []
                for fee in fees:
                    result.append({
                        "book": fee.book,
                        "fee_decimal": fee.fee_decimal,
                        "fee_percent": fee.fee_percent
                    })
                
                return result
        except BitsoApiError as e:
            logger.error(f"Failed to get trading fees: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting trading fees: {str(e)}")
            raise BitsoApiError(f"Service error: {str(e)}")
