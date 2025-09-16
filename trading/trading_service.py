"""
Trading Service - High-level trading operations using Bitso integration
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import logging

from integrations.bitso.bitso_service import BitsoService, BitsoApiError
from integrations.bitso.models import (
    TickerRequest, OrderBookRequest, TradesRequest, PlaceOrderRequest,
    BalanceRequest, CancelOrderRequest, OrderStatusRequest,
    MarketTickerResponseDto, MarketOrderBookResponseDto, MarketTradeResponseDto,
    AccountBalanceResponseDto, TradingOrderResponseDto
)

logger = logging.getLogger(__name__)


class TradingService:
    """High-level trading service that orchestrates Bitso operations"""
    
    def __init__(self, bitso_api_key: Optional[str] = None, bitso_api_secret: Optional[str] = None):
        self.bitso_service = BitsoService(bitso_api_key, bitso_api_secret)
    
    # Market Data Operations
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """Get comprehensive market overview"""
        try:
            # Get available books
            books = await self.bitso_service.get_available_books()
            
            # Get tickers for all books
            ticker_request = TickerRequest()
            tickers = await self.bitso_service.get_ticker(ticker_request)
            
            # Organize data
            market_data = {}
            for ticker in tickers:
                market_data[ticker.book] = {
                    "last_price": float(ticker.last),
                    "volume_24h": float(ticker.volume),
                    "high_24h": float(ticker.high),
                    "low_24h": float(ticker.low),
                    "price_change_24h": float(ticker.high) - float(ticker.low),
                    "bid": float(ticker.bid),
                    "ask": float(ticker.ask),
                    "spread": float(ticker.ask) - float(ticker.bid),
                    "updated_at": ticker.created_at.isoformat()
                }
            
            return {
                "available_books": len(books),
                "market_data": market_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        except BitsoApiError as e:
            logger.error(f"Failed to get market overview: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in market overview: {str(e)}")
            raise
    
    async def get_book_details(self, book: str) -> Dict[str, Any]:
        """Get detailed information for a specific trading book"""
        try:
            # Get ticker
            ticker_request = TickerRequest(book=book)
            tickers = await self.bitso_service.get_ticker(ticker_request)
            ticker = tickers[0] if tickers else None
            
            # Get order book
            orderbook_request = OrderBookRequest(book=book)
            order_book = await self.bitso_service.get_order_book(orderbook_request)
            
            # Get recent trades
            trades_request = TradesRequest(book=book, limit=20)
            trades = await self.bitso_service.get_trades(trades_request)
            
            result = {
                "book": book,
                "ticker": {
                    "last_price": float(ticker.last) if ticker else 0,
                    "volume_24h": float(ticker.volume) if ticker else 0,
                    "high_24h": float(ticker.high) if ticker else 0,
                    "low_24h": float(ticker.low) if ticker else 0,
                    "bid": float(ticker.bid) if ticker else 0,
                    "ask": float(ticker.ask) if ticker else 0,
                } if ticker else {},
                "order_book": {
                    "asks": order_book.asks[:10],  # Top 10 asks
                    "bids": order_book.bids[:10],  # Top 10 bids
                    "spread": float(order_book.asks[0]["price"]) - float(order_book.bids[0]["price"]) if order_book.asks and order_book.bids else 0,
                    "updated_at": order_book.updated_at.isoformat()
                },
                "recent_trades": [
                    {
                        "price": float(trade.price),
                        "amount": float(trade.amount),
                        "side": trade.maker_side,
                        "timestamp": trade.created_at.isoformat()
                    } for trade in trades[:10]
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return result
        except BitsoApiError as e:
            logger.error(f"Failed to get book details for {book}: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting book details: {str(e)}")
            raise
    
    # Account Operations
    
    async def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get complete portfolio summary with balances and valuations"""
        try:
            # Get balances
            balance_request = BalanceRequest()
            balances = await self.bitso_service.get_balances(balance_request)
            
            # Get current market prices for valuation
            ticker_request = TickerRequest()
            tickers = await self.bitso_service.get_ticker(ticker_request)
            
            # Create price lookup
            prices = {}
            for ticker in tickers:
                base, quote = ticker.book.split('_')
                prices[base] = float(ticker.last)
            
            # Calculate portfolio value
            total_value_mxn = Decimal('0')
            portfolio_balances = []
            
            for balance in balances:
                if balance.total > 0:  # Only include non-zero balances
                    current_price = prices.get(balance.currency.lower(), 0)
                    value_mxn = balance.total * Decimal(str(current_price))
                    total_value_mxn += value_mxn
                    
                    portfolio_balances.append({
                        "currency": balance.currency,
                        "available": float(balance.available),
                        "locked": float(balance.locked),
                        "total": float(balance.total),
                        "current_price_mxn": current_price,
                        "value_mxn": float(value_mxn)
                    })
            
            return {
                "total_value_mxn": float(total_value_mxn),
                "balances": portfolio_balances,
                "currencies_count": len(portfolio_balances),
                "timestamp": datetime.utcnow().isoformat()
            }
        except BitsoApiError as e:
            logger.error(f"Failed to get portfolio summary: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting portfolio summary: {str(e)}")
            raise
    
    # Trading Operations
    
    async def execute_market_buy(self, book: str, amount_mxn: Decimal) -> Dict[str, Any]:
        """Execute a market buy order"""
        try:
            order_request = PlaceOrderRequest(
                book=book,
                side="buy",
                order_type="market",
                minor=amount_mxn  # Amount in quote currency (MXN)
            )
            
            order = await self.bitso_service.place_order(order_request)
            
            return {
                "order_id": order.order_id,
                "book": order.book,
                "side": order.side,
                "type": order.order_type,
                "amount_mxn": float(amount_mxn),
                "status": order.status,
                "created_at": order.created_at.isoformat(),
                "message": f"Market buy order placed for {amount_mxn} MXN in {book}"
            }
        except BitsoApiError as e:
            logger.error(f"Failed to execute market buy: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error executing market buy: {str(e)}")
            raise
    
    async def execute_market_sell(self, book: str, amount: Decimal) -> Dict[str, Any]:
        """Execute a market sell order"""
        try:
            order_request = PlaceOrderRequest(
                book=book,
                side="sell",
                order_type="market",
                amount=amount  # Amount in base currency
            )
            
            order = await self.bitso_service.place_order(order_request)
            
            return {
                "order_id": order.order_id,
                "book": order.book,
                "side": order.side,
                "type": order.order_type,
                "amount": float(amount),
                "status": order.status,
                "created_at": order.created_at.isoformat(),
                "message": f"Market sell order placed for {amount} in {book}"
            }
        except BitsoApiError as e:
            logger.error(f"Failed to execute market sell: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error executing market sell: {str(e)}")
            raise
    
    async def place_limit_order(
        self, 
        book: str, 
        side: str, 
        amount: Decimal, 
        price: Decimal
    ) -> Dict[str, Any]:
        """Place a limit order"""
        try:
            order_request = PlaceOrderRequest(
                book=book,
                side=side,
                order_type="limit",
                amount=amount,
                price=price
            )
            
            order = await self.bitso_service.place_order(order_request)
            
            return {
                "order_id": order.order_id,
                "book": order.book,
                "side": order.side,
                "type": order.order_type,
                "amount": float(amount),
                "price": float(price),
                "status": order.status,
                "created_at": order.created_at.isoformat(),
                "message": f"Limit {side} order placed for {amount} at {price} in {book}"
            }
        except BitsoApiError as e:
            logger.error(f"Failed to place limit order: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error placing limit order: {str(e)}")
            raise
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an existing order"""
        try:
            cancel_request = CancelOrderRequest(order_id=order_id)
            success = await self.bitso_service.cancel_order(cancel_request)
            
            return {
                "order_id": order_id,
                "cancelled": success,
                "message": f"Order {order_id} {'cancelled successfully' if success else 'cancellation failed'}",
                "timestamp": datetime.utcnow().isoformat()
            }
        except BitsoApiError as e:
            logger.error(f"Failed to cancel order: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error cancelling order: {str(e)}")
            raise
    
    async def get_trading_history(self, book: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Get trading history for the user"""
        try:
            trades = await self.bitso_service.get_user_trades(book=book, limit=limit)
            
            trade_history = []
            for trade in trades:
                trade_history.append({
                    "book": trade.book,
                    "price": float(trade.price),
                    "amount": float(trade.amount),
                    "side": trade.maker_side,
                    "trade_id": trade.trade_id,
                    "timestamp": trade.created_at.isoformat()
                })
            
            return {
                "trades": trade_history,
                "total_trades": len(trade_history),
                "book_filter": book,
                "timestamp": datetime.utcnow().isoformat()
            }
        except BitsoApiError as e:
            logger.error(f"Failed to get trading history: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting trading history: {str(e)}")
            raise
    
    async def get_open_orders_summary(self) -> Dict[str, Any]:
        """Get summary of all open orders"""
        try:
            orders = await self.bitso_service.get_open_orders()
            
            orders_summary = []
            total_value = Decimal('0')
            
            for order in orders:
                order_value = order.original_amount * order.price
                total_value += order_value
                
                orders_summary.append({
                    "order_id": order.order_id,
                    "book": order.book,
                    "side": order.side,
                    "type": order.order_type,
                    "original_amount": float(order.original_amount),
                    "unfilled_amount": float(order.unfilled_amount),
                    "price": float(order.price),
                    "value": float(order_value),
                    "status": order.status,
                    "created_at": order.created_at.isoformat()
                })
            
            return {
                "open_orders": orders_summary,
                "total_orders": len(orders_summary),
                "total_value": float(total_value),
                "timestamp": datetime.utcnow().isoformat()
            }
        except BitsoApiError as e:
            logger.error(f"Failed to get open orders: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting open orders: {str(e)}")
            raise
