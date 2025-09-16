#!/bin/bash

# MyCrypto API Endpoint Testing Script
# Automatically tests each endpoint with full Docker lifecycle management

set -e

echo "🧪 MyCrypto API Endpoint Testing Suite"
echo "======================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed"
    exit 1
fi

# Install test dependencies if needed
echo "📦 Installing test dependencies..."
pip3 install -r tests/requirements.txt

# Make the test runner executable
chmod +x tests/run_endpoint_tests.py

# Check if specific test is requested
if [ $# -eq 1 ]; then
    echo "🎯 Running specific test: $1"
    python3 tests/run_endpoint_tests.py $1
else
    echo "🚀 Running all endpoint tests..."
    python3 tests/run_endpoint_tests.py
fi

echo ""
echo "✨ Testing complete!"
