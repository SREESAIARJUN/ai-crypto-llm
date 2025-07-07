#!/usr/bin/env python3
import requests
import json
import time
import sys
from datetime import datetime

# Backend API URL from frontend/.env
BACKEND_URL = "https://96404dba-2202-462b-a981-6d7109861d7a.preview.emergentagent.com/api"

def print_separator():
    print("\n" + "="*80 + "\n")

def test_api_health():
    """Test 1: Basic API Health Check - GET /api/"""
    print("\n🔍 Testing API Health Check...")
    try:
        response = requests.get(f"{BACKEND_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ API Health Check: SUCCESS")
            return True
        else:
            print("❌ API Health Check: FAILED")
            return False
    except Exception as e:
        print(f"❌ API Health Check: ERROR - {str(e)}")
        return False

def test_market_data():
    """Test 2: Market Data Endpoint - GET /api/market/data"""
    print("\n🔍 Testing Market Data Endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/market/data")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        # Validate response structure
        required_fields = ["price", "volume", "rsi", "news", "tweets", "timestamp"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if response.status_code == 200 and not missing_fields:
            print("✅ Market Data Endpoint: SUCCESS")
            return True
        else:
            if missing_fields:
                print(f"❌ Market Data Endpoint: FAILED - Missing fields: {missing_fields}")
            else:
                print("❌ Market Data Endpoint: FAILED")
            return False
    except Exception as e:
        print(f"❌ Market Data Endpoint: ERROR - {str(e)}")
        return False

def test_portfolio_status():
    """Test 3: Portfolio Status - GET /api/portfolio"""
    print("\n🔍 Testing Portfolio Status Endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/portfolio")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        # Validate response structure
        required_fields = ["usd_balance", "btc_amount", "last_trade_price"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if response.status_code == 200 and not missing_fields:
            print("✅ Portfolio Status Endpoint: SUCCESS")
            return True
        else:
            if missing_fields:
                print(f"❌ Portfolio Status Endpoint: FAILED - Missing fields: {missing_fields}")
            else:
                print("❌ Portfolio Status Endpoint: FAILED")
            return False
    except Exception as e:
        print(f"❌ Portfolio Status Endpoint: ERROR - {str(e)}")
        return False

def test_metrics_endpoint():
    """Test 4: Metrics Endpoint - GET /api/metrics"""
    print("\n🔍 Testing Metrics Endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/metrics")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        # Validate response structure
        required_fields = ["total_trades", "successful_trades", "total_profit_loss", "accuracy_percentage"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if response.status_code == 200 and not missing_fields:
            print("✅ Metrics Endpoint: SUCCESS")
            return True
        else:
            if missing_fields:
                print(f"❌ Metrics Endpoint: FAILED - Missing fields: {missing_fields}")
            else:
                print("❌ Metrics Endpoint: FAILED")
            return False
    except Exception as e:
        print(f"❌ Metrics Endpoint: ERROR - {str(e)}")
        return False

def test_trade_trigger():
    """Test 5: Trade Trigger - POST /api/trade/trigger"""
    print("\n🔍 Testing Trade Trigger Endpoint...")
    try:
        response = requests.post(f"{BACKEND_URL}/trade/trigger")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response (partial): {json.dumps({k: data[k] for k in ['id', 'decision', 'confidence', 'is_valid', 'verdict'] if k in data}, indent=2)}")
            
            # Check for Chain of Thought reasoning
            if 'chain_of_thought' in data:
                print("\nChain of Thought Reasoning:")
                cot = data['chain_of_thought']
                if isinstance(cot, dict):
                    for key, value in cot.items():
                        if isinstance(value, list):
                            print(f"\n{key}:")
                            for item in value:
                                print(f"  - {item}")
                        else:
                            print(f"\n{key}: {value}")
            
            # Validate response structure
            required_fields = ["id", "timestamp", "price", "decision", "confidence", 
                              "reasoning", "evidence", "is_valid", "verdict"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields and data.get('chain_of_thought'):
                print("✅ Trade Trigger Endpoint: SUCCESS")
                return True
            else:
                if missing_fields:
                    print(f"❌ Trade Trigger Endpoint: FAILED - Missing fields: {missing_fields}")
                if not data.get('chain_of_thought'):
                    print("❌ Trade Trigger Endpoint: FAILED - Missing Chain of Thought reasoning")
                return False
        else:
            print(f"❌ Trade Trigger Endpoint: FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Trade Trigger Endpoint: ERROR - {str(e)}")
        return False

def test_live_trade():
    """Test 6: Live Trade - GET /api/trade/live"""
    print("\n🔍 Testing Live Trade Endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/trade/live")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if we have a trade or just a message
            if 'message' in data and data['message'] == 'No trades found':
                print(f"Response: {json.dumps(data, indent=2)}")
                print("ℹ️ No trades found. This is expected if no trades have been made.")
                print("✅ Live Trade Endpoint: SUCCESS (No trades found)")
                return True
            else:
                print(f"Response (partial): {json.dumps({k: data[k] for k in ['id', 'decision', 'confidence', 'is_valid', 'verdict'] if k in data}, indent=2)}")
                
                # Validate response structure for a trade
                required_fields = ["id", "timestamp", "price", "decision", "confidence", 
                                  "reasoning", "evidence", "is_valid", "verdict"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    print("✅ Live Trade Endpoint: SUCCESS")
                    return True
                else:
                    print(f"❌ Live Trade Endpoint: FAILED - Missing fields: {missing_fields}")
                    return False
        else:
            print(f"❌ Live Trade Endpoint: FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Live Trade Endpoint: ERROR - {str(e)}")
        return False

def test_trade_history():
    """Test 7: Trade History - GET /api/trade/history"""
    print("\n🔍 Testing Trade History Endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/trade/history")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                print(f"Number of trades in history: {len(data)}")
                if data:
                    print(f"Sample trade (first in list): {json.dumps({k: data[0][k] for k in ['id', 'decision', 'confidence', 'is_valid', 'verdict'] if k in data[0]}, indent=2)}")
                else:
                    print("No trades in history.")
                
                print("✅ Trade History Endpoint: SUCCESS")
                return True
            else:
                print(f"❌ Trade History Endpoint: FAILED - Expected list response, got: {type(data)}")
                return False
        else:
            print(f"❌ Trade History Endpoint: FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Trade History Endpoint: ERROR - {str(e)}")
        return False

def run_all_tests():
    print_separator()
    print("🚀 STARTING CRYPTO TRADING AGENT BACKEND TESTS")
    print(f"🔗 Testing against: {BACKEND_URL}")
    print(f"⏱️ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_separator()
    
    # Dictionary to track test results
    results = {}
    
    # Run all tests
    results["API Health"] = test_api_health()
    results["Market Data"] = test_market_data()
    results["Portfolio Status"] = test_portfolio_status()
    results["Metrics"] = test_metrics_endpoint()
    results["Trade Trigger"] = test_trade_trigger()
    results["Live Trade"] = test_live_trade()
    results["Trade History"] = test_trade_history()
    
    # Print summary
    print_separator()
    print("📊 TEST SUMMARY")
    print_separator()
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print_separator()
    if all_passed:
        print("🎉 ALL TESTS PASSED! The Crypto Trading Agent backend is working correctly.")
    else:
        print("⚠️ SOME TESTS FAILED. Please check the detailed output above.")
    
    print_separator()
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)