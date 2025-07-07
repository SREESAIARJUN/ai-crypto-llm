#!/usr/bin/env python3
import requests
import json
import time
import sys
from datetime import datetime

# Backend API URL from frontend/.env
BACKEND_URL = "https://008b3b73-fd2f-49ee-bd48-f80997b2a395.preview.emergentagent.com/api"

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

def test_real_market_data():
    """Test 2: Real Market Data Endpoint - GET /api/market/data"""
    print("\n🔍 Testing Real Market Data Endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/market/data")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        # Validate response structure
        required_fields = ["price", "volume", "rsi", "news", "tweets", "news_sentiment", "twitter_sentiment", "timestamp"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if response.status_code == 200 and not missing_fields:
            # Verify real Bitcoin price (should be a reasonable value)
            if data["price"] < 1000 or data["price"] > 200000:
                print(f"❌ Market Data Endpoint: FAILED - Bitcoin price seems unrealistic: ${data['price']}")
                return False
                
            # Verify news data
            if not data["news"] or not isinstance(data["news"], list) or len(data["news"]) == 0:
                print("❌ Market Data Endpoint: FAILED - No news data available")
                return False
                
            # Verify sentiment data
            if data["news_sentiment"] not in ["Positive", "Negative", "Neutral"]:
                print(f"❌ Market Data Endpoint: FAILED - Invalid news sentiment: {data['news_sentiment']}")
                return False
                
            if data["twitter_sentiment"] not in ["Positive", "Negative", "Neutral"]:
                print(f"❌ Market Data Endpoint: FAILED - Invalid twitter sentiment: {data['twitter_sentiment']}")
                return False
            
            print("✅ Real Market Data Endpoint: SUCCESS")
            print(f"   - Bitcoin Price: ${data['price']:,.2f}")
            print(f"   - News Sentiment: {data['news_sentiment']}")
            print(f"   - Twitter Sentiment: {data['twitter_sentiment']}")
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
        required_fields = ["total_trades", "successful_trades", "total_profit_loss", "accuracy_percentage", "auto_trading_enabled"]
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

def test_enhanced_trade_trigger():
    """Test 5: Enhanced Trade Trigger with Sentiment Analysis - POST /api/trade/trigger"""
    print("\n🔍 Testing Enhanced Trade Trigger Endpoint...")
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
                              "reasoning", "evidence", "is_valid", "verdict", "news_sentiment", "twitter_sentiment"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields and data.get('chain_of_thought'):
                print("✅ Enhanced Trade Trigger Endpoint: SUCCESS")
                print(f"   - News Sentiment: {data['news_sentiment']}")
                print(f"   - Twitter Sentiment: {data['twitter_sentiment']}")
                return True
            else:
                if missing_fields:
                    print(f"❌ Enhanced Trade Trigger Endpoint: FAILED - Missing fields: {missing_fields}")
                if not data.get('chain_of_thought'):
                    print("❌ Enhanced Trade Trigger Endpoint: FAILED - Missing Chain of Thought reasoning")
                return False
        else:
            print(f"❌ Enhanced Trade Trigger Endpoint: FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Enhanced Trade Trigger Endpoint: ERROR - {str(e)}")
        return False

def test_auto_trading_controls():
    """Test 6: Auto-trading Controls"""
    print("\n🔍 Testing Auto-trading Controls...")
    
    # First, check current status
    try:
        status_response = requests.get(f"{BACKEND_URL}/trade/auto/status")
        print(f"Initial Status Code: {status_response.status_code}")
        initial_status = status_response.json()
        print(f"Initial Status: {json.dumps(initial_status, indent=2)}")
        
        # Enable auto-trading
        print("\n🔍 Enabling auto-trading...")
        enable_response = requests.post(f"{BACKEND_URL}/trade/auto/enable")
        print(f"Enable Status Code: {enable_response.status_code}")
        enable_result = enable_response.json()
        print(f"Enable Response: {json.dumps(enable_result, indent=2)}")
        
        # Check status after enabling
        status_response = requests.get(f"{BACKEND_URL}/trade/auto/status")
        enabled_status = status_response.json()
        print(f"Status after enabling: {json.dumps(enabled_status, indent=2)}")
        
        if not enabled_status.get("auto_trading_enabled"):
            print("❌ Auto-trading Enable: FAILED - Status not updated after enabling")
            return False
            
        # Disable auto-trading
        print("\n🔍 Disabling auto-trading...")
        disable_response = requests.post(f"{BACKEND_URL}/trade/auto/disable")
        print(f"Disable Status Code: {disable_response.status_code}")
        disable_result = disable_response.json()
        print(f"Disable Response: {json.dumps(disable_result, indent=2)}")
        
        # Check status after disabling
        status_response = requests.get(f"{BACKEND_URL}/trade/auto/status")
        disabled_status = status_response.json()
        print(f"Status after disabling: {json.dumps(disabled_status, indent=2)}")
        
        if disabled_status.get("auto_trading_enabled"):
            print("❌ Auto-trading Disable: FAILED - Status not updated after disabling")
            return False
            
        print("✅ Auto-trading Controls: SUCCESS")
        return True
        
    except Exception as e:
        print(f"❌ Auto-trading Controls: ERROR - {str(e)}")
        return False

def test_live_trade():
    """Test 7: Live Trade with Sentiment Data - GET /api/trade/live"""
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
                
                # Check for sentiment data
                has_sentiment = "news_sentiment" in data and "twitter_sentiment" in data
                
                if not missing_fields:
                    if has_sentiment:
                        print("✅ Live Trade Endpoint: SUCCESS (with sentiment data)")
                        print(f"   - News Sentiment: {data.get('news_sentiment', 'Not available')}")
                        print(f"   - Twitter Sentiment: {data.get('twitter_sentiment', 'Not available')}")
                    else:
                        print("✅ Live Trade Endpoint: SUCCESS (but missing sentiment data)")
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
    """Test 8: Trade History with Sentiment Data - GET /api/trade/history"""
    print("\n🔍 Testing Trade History Endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/trade/history")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                print(f"Number of trades in history: {len(data)}")
                if data:
                    sample_trade = data[0]
                    print(f"Sample trade (first in list): {json.dumps({k: sample_trade[k] for k in ['id', 'decision', 'confidence', 'is_valid', 'verdict'] if k in sample_trade}, indent=2)}")
                    
                    # Check for sentiment data in the most recent trade
                    has_sentiment = "news_sentiment" in sample_trade and "twitter_sentiment" in sample_trade
                    if has_sentiment:
                        print(f"   - News Sentiment: {sample_trade.get('news_sentiment', 'Not available')}")
                        print(f"   - Twitter Sentiment: {sample_trade.get('twitter_sentiment', 'Not available')}")
                    else:
                        print("   - Note: Sentiment data not available in this trade")
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
    print("🚀 STARTING ENHANCED CRYPTO TRADING AGENT BACKEND TESTS")
    print(f"🔗 Testing against: {BACKEND_URL}")
    print(f"⏱️ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_separator()
    
    # Dictionary to track test results
    results = {}
    
    # Run all tests
    results["API Health"] = test_api_health()
    results["Real Market Data"] = test_real_market_data()
    results["Portfolio Status"] = test_portfolio_status()
    results["Metrics"] = test_metrics_endpoint()
    results["Enhanced Trade Trigger"] = test_enhanced_trade_trigger()
    results["Auto-trading Controls"] = test_auto_trading_controls()
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
        print("🎉 ALL TESTS PASSED! The Enhanced Crypto Trading Agent backend is working correctly.")
        print("✅ Real-world Data Integration: Successfully fetches Bitcoin price, news, and sentiment")
        print("✅ Auto-trading Controls: Enable/disable functionality works correctly")
        print("✅ Enhanced Trade Pipeline: Sentiment analysis is properly integrated")
        print("✅ Sentiment Analysis: Trade results include news and Twitter sentiment")
    else:
        print("⚠️ SOME TESTS FAILED. Please check the detailed output above.")
    
    print_separator()
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)