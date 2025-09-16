"""
Bitso API Routes - FastAPI endpoints for Bitso integration
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
import os
from decimal import Decimal

from presentation.api.auth_routes import get_current_user
from presentation.schemas.auth_schemas import AuthUserResponseSchema
from presentation.schemas.bitso_schemas import (
    TickerRequestSchema, OrderBookRequestSchema, TradesRequestSchema,
    PlaceOrderRequestSchema, CancelOrderRequestSchema,
    MarketBuyRequestSchema, MarketSellRequestSchema, LimitOrderRequestSchema,
    TickerResponseSchema, OrderBookResponseSchema, TradeResponseSchema,
    BalanceResponseSchema, OrderResponseSchema, MarketOverviewResponseSchema,
    BookDetailsResponseSchema, PortfolioSummaryResponseSchema,
    TradingOperationResponseSchema, TradingHistoryResponseSchema,
    OpenOrdersSummaryResponseSchema, AccountInfoResponseSchema,
    AvailableBooksResponseSchema, TradingFeesResponseSchema
)
from trading.trading_service import TradingService
from integrations.bitso.bitso_service import BitsoService, BitsoApiError
from integrations.bitso.models import (
    TickerRequest, OrderBookRequest, TradesRequest, PlaceOrderRequest,
    BalanceRequest, CancelOrderRequest
)

router = APIRouter(prefix="/bitso", tags=["Bitso Integration"])


def get_trading_service() -> TradingService:
    """Get trading service with Bitso credentials"""
    api_key = os.getenv("BITSO_API_KEY")
    api_secret = os.getenv("BITSO_API_SECRET")
    return TradingService(api_key, api_secret)


def get_bitso_service() -> BitsoService:
    """Get Bitso service with credentials"""
    api_key = os.getenv("BITSO_API_KEY")
    api_secret = os.getenv("BITSO_API_SECRET")
    return BitsoService(api_key, api_secret)


# Public Market Data Endpoints

@router.get("/books", response_model=List[dict])
async def get_available_books():
    """Get list of available trading books"""
    try:
        bitso_service = get_bitso_service()
        books = await bitso_service.get_available_books()
        return books
    except BitsoApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bitso API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available books"
        )


@router.get("/ticker", response_model=List[TickerResponseSchema])
async def get_ticker(book: Optional[str] = Query(None, description="Trading book (e.g., 'btc_mxn')")):
    """Get ticker information for one or all books"""
    try:
        bitso_service = get_bitso_service()
        request = TickerRequest(book=book)
        tickers = await bitso_service.get_ticker(request)
        return tickers
    except BitsoApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bitso API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get ticker information"
        )


@router.get("/orderbook/{book}", response_model=OrderBookResponseSchema)
async def get_order_book(
    book: str,
    aggregate: bool = Query(True, description="Aggregate orders at same price level")
):
    """Get order book for a specific trading book"""
    try:
        bitso_service = get_bitso_service()
        request = OrderBookRequest(book=book, aggregate=aggregate)
        order_book = await bitso_service.get_order_book(request)
        return order_book
    except BitsoApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bitso API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get order book"
        )


@router.get("/trades/{book}", response_model=List[TradeResponseSchema])
async def get_trades(
    book: str,
    limit: int = Query(100, ge=1, le=1000, description="Number of trades to return"),
    marker: Optional[str] = Query(None, description="Marker for pagination"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc'")
):
    """Get recent trades for a trading book"""
    try:
        bitso_service = get_bitso_service()
        request = TradesRequest(book=book, limit=limit, marker=marker, sort=sort)
        trades = await bitso_service.get_trades(request)
        return trades
    except BitsoApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bitso API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trades"
        )


@router.get("/market-overview", response_model=MarketOverviewResponseSchema)
async def get_market_overview():
    """Get comprehensive market overview"""
    try:
        trading_service = get_trading_service()
        overview = await trading_service.get_market_overview()
        return overview
    except BitsoApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bitso API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get market overview"
        )


@router.get("/book-details/{book}", response_model=BookDetailsResponseSchema)
async def get_book_details(book: str):
    """Get detailed information for a specific trading book"""
    try:
        trading_service = get_trading_service()
        details = await trading_service.get_book_details(book)
        return details
    except BitsoApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bitso API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get book details"
        )


# Private Account Endpoints

@router.get("/account/info", response_model=AccountInfoResponseSchema)
async def get_account_info(current_user: AuthUserResponseSchema = Depends(get_current_user)):
    """Get account information"""
    try:
        bitso_service = get_bitso_service()
        account_info = await bitso_service.get_account_info()
        return account_info
    except BitsoApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bitso API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get account information"
        )


@router.get("/account/balances", response_model=List[BalanceResponseSchema])
async def get_balances(
    current_user: AuthUserResponseSchema = Depends(get_current_user),
    currency: Optional[str] = Query(None, description="Filter by specific currency")
):
    """Get account balances"""
    try:
        bitso_service = get_bitso_service()
        request = BalanceRequest(currency=currency)
        balances = await bitso_service.get_balances(request)
        return balances
    except BitsoApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bitso API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get balances"
        )


@router.get("/account/portfolio", response_model=PortfolioSummaryResponseSchema)
async def get_portfolio_summary(current_user: AuthUserResponseSchema = Depends(get_current_user)):
    """Get complete portfolio summary with valuations"""
    try:
        trading_service = get_trading_service()
        portfolio = await trading_service.get_portfolio_summary()
        return portfolio
    except BitsoApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bitso API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get portfolio summary"
        )


@router.get("/account/fees", response_model=List[dict])
async def get_trading_fees(current_user: AuthUserResponseSchema = Depends(get_current_user)):
    """Get trading fees for all books"""
    try:
        bitso_service = get_bitso_service()
        fees = await bitso_service.get_trading_fees()
        return fees
    except BitsoApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bitso API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trading fees"
        )


# Trading Endpoints

@router.post("/trading/market-buy", response_model=TradingOperationResponseSchema)
async def market_buy(
    order_data: MarketBuyRequestSchema,
    current_user: AuthUserResponseSchema = Depends(get_current_user)
):
    """Execute a market buy order"""
    try:
        trading_service = get_trading_service()
        result = await trading_service.execute_market_buy(order_data.book, order_data.amount_mxn)
        return result
    except BitsoApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bitso API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute market buy"
        )


@router.post("/trading/market-sell", response_model=TradingOperationResponseSchema)
async def market_sell(
    order_data: MarketSellRequestSchema,
    current_user: AuthUserResponseSchema = Depends(get_current_user)
):
    """Execute a market sell order"""
    try:
        trading_service = get_trading_service()
        result = await trading_service.execute_market_sell(order_data.book, order_data.amount)
        return result
    except BitsoApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bitso API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute market sell"
        )


@router.post("/trading/limit-order", response_model=TradingOperationResponseSchema)
async def place_limit_order(
    order_data: LimitOrderRequestSchema,
    current_user: AuthUserResponseSchema = Depends(get_current_user)
):
    """Place a limit order"""
    try:
        trading_service = get_trading_service()
        result = await trading_service.place_limit_order(
            order_data.book, order_data.side, order_data.amount, order_data.price
        )
        return result
    except BitsoApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bitso API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to place limit order"
        )


@router.delete("/trading/orders/{order_id}", response_model=TradingOperationResponseSchema)
async def cancel_order(
    order_id: str,
    current_user: AuthUserResponseSchema = Depends(get_current_user)
):
    """Cancel an existing order"""
    try:
        trading_service = get_trading_service()
        result = await trading_service.cancel_order(order_id)
        return result
    except BitsoApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bitso API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel order"
        )


@router.get("/trading/orders", response_model=OpenOrdersSummaryResponseSchema)
async def get_open_orders(current_user: AuthUserResponseSchema = Depends(get_current_user)):
    """Get summary of all open orders"""
    try:
        trading_service = get_trading_service()
        orders = await trading_service.get_open_orders_summary()
        return orders
    except BitsoApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bitso API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get open orders"
        )


@router.get("/trading/history", response_model=TradingHistoryResponseSchema)
async def get_trading_history(
    current_user: AuthUserResponseSchema = Depends(get_current_user),
    book: Optional[str] = Query(None, description="Filter by trading book"),
    limit: int = Query(50, ge=1, le=1000, description="Number of trades to return")
):
    """Get trading history for the user"""
    try:
        trading_service = get_trading_service()
        history = await trading_service.get_trading_history(book=book, limit=limit)
        return history
    except BitsoApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bitso API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trading history"
        )
