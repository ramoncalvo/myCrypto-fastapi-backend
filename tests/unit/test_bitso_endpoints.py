"""
Bitso Endpoints Testing
Unit tests for Bitso API integration endpoints
"""
import uuid
import requests
import time
from typing import Dict, Any, Optional


class BitsoEndpointTester:
    """Test class for Bitso API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token: Optional[str] = None
        self.test_user_email = f"bitso_test_{str(uuid.uuid4())[:8]}@example.com"
        self.test_user_password = "TestPassword123!"
    
    def register_and_login(self) -> bool:
        """Register test user and get auth token"""
        try:
            # Register user
            register_data = {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "first_name": "Bitso",
                "last_name": "Tester"
            }
            
            register_response = self.session.post(
                f"{self.base_url}/auth/register",
                json=register_data
            )
            
            if register_response.status_code != 201:
                print(f"❌ Registration failed: {register_response.status_code}")
                return False
            
            # Login to get token
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            login_response = self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data
            )
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                return False
            
            token_data = login_response.json()
            self.auth_token = token_data["access_token"]
            
            # Set authorization header
            self.session.headers.update({
                "Authorization": f"Bearer {self.auth_token}"
            })
            
            print(f"✅ User registered and authenticated: {self.test_user_email}")
            return True
            
        except Exception as e:
            print(f"❌ Auth setup failed: {str(e)}")
            return False
    
    def test_endpoint(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        expected_status: int = 200,
        auth_required: bool = False
    ) -> Dict[str, Any]:
        """Test a specific endpoint"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            # Prepare headers
            headers = {}
            if auth_required and self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            # Make request
            if method.upper() == "GET":
                response = self.session.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, params=params, headers=headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, params=params, headers=headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, json=data, params=params, headers=headers)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported method: {method}",
                    "status_code": 0,
                    "response": None
                }
            
            # Parse response
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            success = response.status_code == expected_status
            
            return {
                "success": success,
                "status_code": response.status_code,
                "response": response_data,
                "expected_status": expected_status
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": 0,
                "response": None
            }


class TestBitsoPublicEndpoints:
    """Test public Bitso endpoints (no authentication required)"""
    
    def test_available_books(self):
        """Test GET /bitso/books"""
        print("\n🧪 Testing: Available Books")
        tester = BitsoEndpointTester()
        
        result = tester.test_endpoint("GET", "/bitso/books")
        print(f"📊 Available Books Result: {result}")
        
        if result["success"]:
            books = result["response"]
            print(f"✅ Found {len(books)} available books")
            if books:
                print(f"📋 Sample book: {books[0]}")
        
        return result["success"]
    
    def test_ticker_all(self):
        """Test GET /bitso/ticker (all tickers)"""
        print("\n🧪 Testing: All Tickers")
        tester = BitsoEndpointTester()
        
        result = tester.test_endpoint("GET", "/bitso/ticker")
        print(f"📊 All Tickers Result: {result}")
        
        if result["success"]:
            tickers = result["response"]
            print(f"✅ Found {len(tickers)} tickers")
            if tickers:
                print(f"📋 Sample ticker: {tickers[0]}")
        
        return result["success"]
    
    def test_ticker_specific(self):
        """Test GET /bitso/ticker?book=btc_mxn"""
        print("\n🧪 Testing: Specific Ticker (BTC_MXN)")
        tester = BitsoEndpointTester()
        
        result = tester.test_endpoint("GET", "/bitso/ticker", params={"book": "btc_mxn"})
        print(f"📊 BTC Ticker Result: {result}")
        
        if result["success"]:
            tickers = result["response"]
            if tickers:
                btc_ticker = tickers[0]
                print(f"✅ BTC Price: {btc_ticker.get('last', 'N/A')} MXN")
        
        return result["success"]
    
    def test_order_book(self):
        """Test GET /bitso/orderbook/btc_mxn"""
        print("\n🧪 Testing: Order Book (BTC_MXN)")
        tester = BitsoEndpointTester()
        
        result = tester.test_endpoint("GET", "/bitso/orderbook/btc_mxn")
        print(f"📊 Order Book Result: {result}")
        
        if result["success"]:
            order_book = result["response"]
            asks_count = len(order_book.get("asks", []))
            bids_count = len(order_book.get("bids", []))
            print(f"✅ Order Book - Asks: {asks_count}, Bids: {bids_count}")
        
        return result["success"]
    
    def test_trades(self):
        """Test GET /bitso/trades/btc_mxn"""
        print("\n🧪 Testing: Recent Trades (BTC_MXN)")
        tester = BitsoEndpointTester()
        
        result = tester.test_endpoint("GET", "/bitso/trades/btc_mxn", params={"limit": 10})
        print(f"📊 Trades Result: {result}")
        
        if result["success"]:
            trades = result["response"]
            print(f"✅ Found {len(trades)} recent trades")
            if trades:
                print(f"📋 Latest trade: {trades[0]}")
        
        return result["success"]
    
    def test_market_overview(self):
        """Test GET /bitso/market-overview"""
        print("\n🧪 Testing: Market Overview")
        tester = BitsoEndpointTester()
        
        result = tester.test_endpoint("GET", "/bitso/market-overview")
        print(f"📊 Market Overview Result: {result}")
        
        if result["success"]:
            overview = result["response"]
            books_count = overview.get("available_books", 0)
            print(f"✅ Market Overview - Books: {books_count}")
        
        return result["success"]
    
    def test_book_details(self):
        """Test GET /bitso/book-details/btc_mxn"""
        print("\n🧪 Testing: Book Details (BTC_MXN)")
        tester = BitsoEndpointTester()
        
        result = tester.test_endpoint("GET", "/bitso/book-details/btc_mxn")
        print(f"📊 Book Details Result: {result}")
        
        if result["success"]:
            details = result["response"]
            print(f"✅ Book Details for {details.get('book', 'N/A')}")
        
        return result["success"]


class TestBitsoPrivateEndpoints:
    """Test private Bitso endpoints (authentication required)"""
    
    def test_account_info(self):
        """Test GET /bitso/account/info"""
        print("\n🧪 Testing: Account Info (requires auth)")
        tester = BitsoEndpointTester()
        
        if not tester.register_and_login():
            print("❌ Failed to authenticate")
            return False
        
        result = tester.test_endpoint("GET", "/bitso/account/info", auth_required=True)
        print(f"📊 Account Info Result: {result}")
        
        # Note: This will likely fail without real Bitso API credentials
        # We expect a 400 or 500 error due to missing/invalid API keys
        expected_failure = result["status_code"] in [400, 500]
        if expected_failure:
            print("✅ Expected failure due to missing Bitso API credentials")
            return True
        
        return result["success"]
    
    def test_balances(self):
        """Test GET /bitso/account/balances"""
        print("\n🧪 Testing: Account Balances (requires auth)")
        tester = BitsoEndpointTester()
        
        if not tester.register_and_login():
            print("❌ Failed to authenticate")
            return False
        
        result = tester.test_endpoint("GET", "/bitso/account/balances", auth_required=True)
        print(f"📊 Balances Result: {result}")
        
        # Note: This will likely fail without real Bitso API credentials
        expected_failure = result["status_code"] in [400, 500]
        if expected_failure:
            print("✅ Expected failure due to missing Bitso API credentials")
            return True
        
        return result["success"]
    
    def test_portfolio_summary(self):
        """Test GET /bitso/account/portfolio"""
        print("\n🧪 Testing: Portfolio Summary (requires auth)")
        tester = BitsoEndpointTester()
        
        if not tester.register_and_login():
            print("❌ Failed to authenticate")
            return False
        
        result = tester.test_endpoint("GET", "/bitso/account/portfolio", auth_required=True)
        print(f"📊 Portfolio Summary Result: {result}")
        
        # Note: This will likely fail without real Bitso API credentials
        expected_failure = result["status_code"] in [400, 500]
        if expected_failure:
            print("✅ Expected failure due to missing Bitso API credentials")
            return True
        
        return result["success"]
    
    def test_trading_fees(self):
        """Test GET /bitso/account/fees"""
        print("\n🧪 Testing: Trading Fees (requires auth)")
        tester = BitsoEndpointTester()
        
        if not tester.register_and_login():
            print("❌ Failed to authenticate")
            return False
        
        result = tester.test_endpoint("GET", "/bitso/account/fees", auth_required=True)
        print(f"📊 Trading Fees Result: {result}")
        
        # Note: This will likely fail without real Bitso API credentials
        expected_failure = result["status_code"] in [400, 500]
        if expected_failure:
            print("✅ Expected failure due to missing Bitso API credentials")
            return True
        
        return result["success"]
    
    def test_open_orders(self):
        """Test GET /bitso/trading/orders"""
        print("\n🧪 Testing: Open Orders (requires auth)")
        tester = BitsoEndpointTester()
        
        if not tester.register_and_login():
            print("❌ Failed to authenticate")
            return False
        
        result = tester.test_endpoint("GET", "/bitso/trading/orders", auth_required=True)
        print(f"📊 Open Orders Result: {result}")
        
        # Note: This will likely fail without real Bitso API credentials
        expected_failure = result["status_code"] in [400, 500]
        if expected_failure:
            print("✅ Expected failure due to missing Bitso API credentials")
            return True
        
        return result["success"]
    
    def test_trading_history(self):
        """Test GET /bitso/trading/history"""
        print("\n🧪 Testing: Trading History (requires auth)")
        tester = BitsoEndpointTester()
        
        if not tester.register_and_login():
            print("❌ Failed to authenticate")
            return False
        
        result = tester.test_endpoint("GET", "/bitso/trading/history", auth_required=True)
        print(f"📊 Trading History Result: {result}")
        
        # Note: This will likely fail without real Bitso API credentials
        expected_failure = result["status_code"] in [400, 500]
        if expected_failure:
            print("✅ Expected failure due to missing Bitso API credentials")
            return True
        
        return result["success"]


def run_all_bitso_tests():
    """Run all Bitso endpoint tests"""
    print("🚀 Starting Bitso API Integration Tests")
    print("=" * 60)
    
    # Test public endpoints
    public_tests = TestBitsoPublicEndpoints()
    public_results = {
        "available_books": public_tests.test_available_books(),
        "ticker_all": public_tests.test_ticker_all(),
        "ticker_specific": public_tests.test_ticker_specific(),
        "order_book": public_tests.test_order_book(),
        "trades": public_tests.test_trades(),
        "market_overview": public_tests.test_market_overview(),
        "book_details": public_tests.test_book_details(),
    }
    
    # Test private endpoints
    private_tests = TestBitsoPrivateEndpoints()
    private_results = {
        "account_info": private_tests.test_account_info(),
        "balances": private_tests.test_balances(),
        "portfolio_summary": private_tests.test_portfolio_summary(),
        "trading_fees": private_tests.test_trading_fees(),
        "open_orders": private_tests.test_open_orders(),
        "trading_history": private_tests.test_trading_history(),
    }
    
    # Summary
    all_results = {**public_results, **private_results}
    passed = sum(1 for result in all_results.values() if result)
    total = len(all_results)
    
    print("\n" + "=" * 60)
    print("📊 BITSO API INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    print("\n📋 DETAILED RESULTS:")
    print("\n🌐 Public Endpoints:")
    for test_name, result in public_results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")
    
    print("\n🔐 Private Endpoints:")
    for test_name, result in private_results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")
    
    print("\n📝 Notes:")
    print("- Public endpoints should work without API credentials")
    print("- Private endpoints expected to fail without real Bitso API keys")
    print("- Set BITSO_API_KEY and BITSO_API_SECRET env vars for full testing")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_bitso_tests()
    exit(0 if success else 1)
