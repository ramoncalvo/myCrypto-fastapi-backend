#!/usr/bin/env python3
"""
Automated Endpoint Testing Script
Runs each endpoint test in isolation with full Docker lifecycle management
"""

import sys
import os
import subprocess
import time
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.unit.test_endpoints import (
    TestAuthEndpoints, 
    TestCryptoAssetEndpoints, 
    TestPortfolioEndpoints, 
    TestTransactionEndpoints
)

class TestRunner:
    """Orchestrates the execution of all endpoint tests"""
    
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
    
    def run_test_method(self, test_class, method_name: str) -> dict:
        """Run a single test method"""
        print(f"\n{'='*60}")
        print(f"🧪 Running: {test_class.__name__}.{method_name}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Create test instance and run method
            test_instance = test_class()
            test_method = getattr(test_instance, method_name)
            test_method()
            
            duration = time.time() - start_time
            result = {
                'test': f"{test_class.__name__}.{method_name}",
                'status': 'PASSED',
                'duration': duration,
                'error': None
            }
            print(f"✅ PASSED in {duration:.2f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            result = {
                'test': f"{test_class.__name__}.{method_name}",
                'status': 'FAILED',
                'duration': duration,
                'error': str(e)
            }
            print(f"❌ FAILED in {duration:.2f}s")
            print(f"Error: {e}")
        
        return result
    
    def run_all_tests(self):
        """Run all endpoint tests"""
        print("🚀 Starting Automated Endpoint Testing")
        print(f"Start time: {self.start_time}")
        
        # Define test cases to run
        test_cases = [
            # Authentication tests
            (TestAuthEndpoints, 'test_auth_register'),
            (TestAuthEndpoints, 'test_auth_login'),
            
            # Crypto asset tests
            (TestCryptoAssetEndpoints, 'test_crypto_assets_list'),
            (TestCryptoAssetEndpoints, 'test_crypto_assets_create'),
            
            # Portfolio tests
            (TestPortfolioEndpoints, 'test_portfolios_list'),
            (TestPortfolioEndpoints, 'test_portfolios_create'),
            
            # Transaction tests
            (TestTransactionEndpoints, 'test_transactions_list'),
            (TestTransactionEndpoints, 'test_transaction_buy_flow'),
            (TestTransactionEndpoints, 'test_transaction_stats'),
        ]
        
        # Run each test
        for test_class, method_name in test_cases:
            result = self.run_test_method(test_class, method_name)
            self.results.append(result)
            
            # Small delay between tests
            time.sleep(2)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test execution summary"""
        end_time = datetime.now()
        total_duration = end_time - self.start_time
        
        passed = len([r for r in self.results if r['status'] == 'PASSED'])
        failed = len([r for r in self.results if r['status'] == 'FAILED'])
        total = len(self.results)
        
        print(f"\n{'='*80}")
        print(f"📊 TEST EXECUTION SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print(f"Total Duration: {total_duration}")
        print(f"End time: {end_time}")
        
        if failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if result['status'] == 'FAILED':
                    print(f"  - {result['test']}: {result['error']}")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.results:
            status_icon = "✅" if result['status'] == 'PASSED' else "❌"
            print(f"  {status_icon} {result['test']} ({result['duration']:.2f}s)")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        print(f"Running specific test: {test_name}")
        
        # Map test names to classes and methods
        test_map = {
            'auth_register': (TestAuthEndpoints, 'test_auth_register'),
            'auth_login': (TestAuthEndpoints, 'test_auth_login'),
            'crypto_list': (TestCryptoAssetEndpoints, 'test_crypto_assets_list'),
            'crypto_create': (TestCryptoAssetEndpoints, 'test_crypto_assets_create'),
            'portfolio_list': (TestPortfolioEndpoints, 'test_portfolios_list'),
            'portfolio_create': (TestPortfolioEndpoints, 'test_portfolios_create'),
            'transaction_list': (TestTransactionEndpoints, 'test_transactions_list'),
            'transaction_buy': (TestTransactionEndpoints, 'test_transaction_buy_flow'),
            'transaction_stats': (TestTransactionEndpoints, 'test_transaction_stats'),
        }
        
        if test_name in test_map:
            runner = TestRunner()
            test_class, method_name = test_map[test_name]
            result = runner.run_test_method(test_class, method_name)
            runner.results.append(result)
            runner.print_summary()
        else:
            print(f"Unknown test: {test_name}")
            print(f"Available tests: {', '.join(test_map.keys())}")
            sys.exit(1)
    else:
        # Run all tests
        runner = TestRunner()
        runner.run_all_tests()

if __name__ == "__main__":
    main()
