"""
Bitso API Client Implementation
"""
import asyncio
import hashlib
import hmac
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
from decimal import Decimal

from .models import (
    BitsoApiResponse, BitsoTickerResponse, BitsoOrderBookResponse, 
    BitsoTradeResponse, BitsoBalanceResponse, BitsoAccountInfoResponse,
    BitsoOrderResponse, BitsoWithdrawalResponse, BitsoFeeResponse
)


class BitsoApiError(Exception):
    """Bitso API specific error"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class BitsoRateLimiter:
    """Simple rate limiter for Bitso API"""
    def __init__(self, max_requests: int = 300, time_window: int = 600):  # 300 requests per 10 minutes
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            # Calculate wait time
            oldest_request = min(self.requests)
            wait_time = self.time_window - (now - oldest_request)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        self.requests.append(now)


class BitsoClient:
    """Bitso API Client with rate limiting and authentication"""
    
    BASE_URL = "https://api.bitso.com/v3"
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.rate_limiter = BitsoRateLimiter()
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _generate_signature(self, method: str, request_path: str, body: str = "") -> Dict[str, str]:
        """Generate authentication signature for private endpoints"""
        if not self.api_key or not self.api_secret:
            raise BitsoApiError("API key and secret required for authenticated requests")
        
        nonce = str(int(time.time() * 1000))
        message = nonce + method.upper() + request_path + body
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return {
            'Authorization': f'Bitso {self.api_key}:{nonce}:{signature}',
            'Content-Type': 'application/json'
        }
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        authenticated: bool = False
    ) -> Dict[str, Any]:
        """Make HTTP request to Bitso API"""
        if not self.session:
            raise BitsoApiError("Client session not initialized. Use async context manager.")
        
        await self.rate_limiter.wait_if_needed()
        
        url = f"{self.BASE_URL}{endpoint}"
        headers = {}
        
        if authenticated:
            body = json.dumps(data) if data else ""
            headers.update(self._generate_signature(method, endpoint, body))
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers
            ) as response:
                response_data = await response.json()
                
                if not response_data.get('success', False):
                    error_info = response_data.get('error', {})
                    raise BitsoApiError(
                        error_info.get('message', 'Unknown API error'),
                        error_info.get('code')
                    )
                
                return response_data.get('payload', {})
        
        except aiohttp.ClientError as e:
            raise BitsoApiError(f"HTTP request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise BitsoApiError(f"Invalid JSON response: {str(e)}")
    
    # Public Market Data Endpoints
    
    async def get_available_books(self) -> List[Dict[str, Any]]:
        """Get available trading books"""
        return await self._make_request('GET', '/available_books/')
    
    async def get_ticker(self, book: Optional[str] = None) -> List[BitsoTickerResponse]:
        """Get ticker information"""
        endpoint = f'/ticker/' if not book else f'/ticker/{book}/'
        data = await self._make_request('GET', endpoint)
        
        # Handle both single ticker and multiple tickers
        if isinstance(data, dict):
            data = [data]
        
        return [BitsoTickerResponse(**ticker) for ticker in data]
    
    async def get_order_book(self, book: str, aggregate: bool = True) -> BitsoOrderBookResponse:
        """Get order book for a specific book"""
        params = {'aggregate': str(aggregate).lower()}
        data = await self._make_request('GET', f'/order_book/{book}/', params=params)
        return BitsoOrderBookResponse(**data)
    
    async def get_trades(
        self, 
        book: str, 
        marker: Optional[str] = None, 
        sort: str = 'desc', 
        limit: int = 100
    ) -> List[BitsoTradeResponse]:
        """Get recent trades"""
        params = {'sort': sort, 'limit': limit}
        if marker:
            params['marker'] = marker
        
        data = await self._make_request('GET', f'/trades/{book}/', params=params)
        return [BitsoTradeResponse(**trade) for trade in data]
    
    # Private Account Endpoints
    
    async def get_account_status(self) -> BitsoAccountInfoResponse:
        """Get account information"""
        data = await self._make_request('GET', '/account_status/', authenticated=True)
        return BitsoAccountInfoResponse(**data)
    
    async def get_balances(self) -> List[BitsoBalanceResponse]:
        """Get account balances"""
        data = await self._make_request('GET', '/balance/', authenticated=True)
        balances = data.get('balances', [])
        return [BitsoBalanceResponse(**balance) for balance in balances]
    
    async def get_fees(self) -> List[BitsoFeeResponse]:
        """Get trading fees"""
        data = await self._make_request('GET', '/fees/', authenticated=True)
        fees = data.get('fees', [])
        return [BitsoFeeResponse(**fee) for fee in fees]
    
    # Trading Endpoints
    
    async def place_order(
        self,
        book: str,
        side: str,
        order_type: str,
        amount: Optional[str] = None,
        price: Optional[str] = None,
        minor: Optional[str] = None
    ) -> BitsoOrderResponse:
        """Place a buy or sell order"""
        data = {
            'book': book,
            'side': side,
            'type': order_type
        }
        
        if amount:
            data['amount'] = amount
        if price:
            data['price'] = price
        if minor:
            data['minor'] = minor
        
        response = await self._make_request('POST', '/orders/', data=data, authenticated=True)
        return BitsoOrderResponse(**response)
    
    async def cancel_order(self, order_id: str) -> List[str]:
        """Cancel an order"""
        data = {'oid': order_id}
        response = await self._make_request('DELETE', '/orders/', data=data, authenticated=True)
        return response
    
    async def get_open_orders(self, book: Optional[str] = None) -> List[BitsoOrderResponse]:
        """Get open orders"""
        params = {'book': book} if book else {}
        data = await self._make_request('GET', '/open_orders/', params=params, authenticated=True)
        orders = data if isinstance(data, list) else []
        return [BitsoOrderResponse(**order) for order in orders]
    
    async def get_order_trades(self, order_id: str) -> List[BitsoTradeResponse]:
        """Get trades for a specific order"""
        data = await self._make_request('GET', f'/order_trades/{order_id}/', authenticated=True)
        trades = data if isinstance(data, list) else []
        return [BitsoTradeResponse(**trade) for trade in trades]
    
    async def get_user_trades(
        self, 
        book: Optional[str] = None, 
        sort: str = 'desc', 
        limit: int = 100,
        marker: Optional[str] = None
    ) -> List[BitsoTradeResponse]:
        """Get user's trade history"""
        params = {'sort': sort, 'limit': limit}
        if book:
            params['book'] = book
        if marker:
            params['marker'] = marker
        
        data = await self._make_request('GET', '/user_trades/', params=params, authenticated=True)
        trades = data if isinstance(data, list) else []
        return [BitsoTradeResponse(**trade) for trade in trades]
    
    # Funding Endpoints
    
    async def get_funding_destination(self, currency: str) -> Dict[str, Any]:
        """Get funding destination for a currency"""
        data = await self._make_request('GET', f'/funding_destination/{currency}/', authenticated=True)
        return data
    
    async def withdraw_crypto(
        self, 
        currency: str, 
        amount: str, 
        address: str,
        destination_tag: Optional[str] = None
    ) -> BitsoWithdrawalResponse:
        """Withdraw cryptocurrency"""
        data = {
            'currency': currency,
            'amount': amount,
            'address': address
        }
        if destination_tag:
            data['destination_tag'] = destination_tag
        
        response = await self._make_request('POST', '/crypto_withdrawal/', data=data, authenticated=True)
        return BitsoWithdrawalResponse(**response)
    
    async def get_withdrawals(self, wid: Optional[str] = None) -> List[BitsoWithdrawalResponse]:
        """Get withdrawal history"""
        endpoint = f'/withdrawals/{wid}/' if wid else '/withdrawals/'
        data = await self._make_request('GET', endpoint, authenticated=True)
        
        if isinstance(data, dict):
            data = [data]
        
        return [BitsoWithdrawalResponse(**withdrawal) for withdrawal in data]
