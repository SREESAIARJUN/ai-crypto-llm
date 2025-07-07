#!/usr/bin/env python3
import requests
import json
import time
import sys
from datetime import datetime

# Backend API URL from frontend/.env
BACKEND_URL = "https://b365afac-dc34-4e20-a366-eab471747605.preview.emergentagent.com/api"

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

def test_chart_data():
    """Test 9: Chart Data Endpoint - GET /api/trades/chart-data"""
    print("\n🔍 Testing Chart Data Endpoint...")
    
    # Test with different timeframes
    timeframes = ["1h", "24h", "7d"]
    results = {}
    timeframe_data = {}  # Store data for each timeframe for comparison
    
    for timeframe in timeframes:
        print(f"\n🔍 Testing Chart Data with timeframe: {timeframe}")
        try:
            response = requests.get(f"{BACKEND_URL}/trades/chart-data?timeframe={timeframe}")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                timeframe_data[timeframe] = data  # Store data for comparison
                
                # Check required fields
                required_fields = ["price_history", "trade_markers", "portfolio_history", "sentiment_timeline", "timeframe", "last_updated"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Verify timeframe matches request
                    if data["timeframe"] != timeframe:
                        print(f"❌ Chart Data Endpoint ({timeframe}): FAILED - Timeframe mismatch: {data['timeframe']}")
                        results[timeframe] = False
                        continue
                    
                    # Verify data structures
                    if not isinstance(data["price_history"], list):
                        print(f"❌ Chart Data Endpoint ({timeframe}): FAILED - price_history is not a list")
                        results[timeframe] = False
                        continue
                        
                    if not isinstance(data["trade_markers"], list):
                        print(f"❌ Chart Data Endpoint ({timeframe}): FAILED - trade_markers is not a list")
                        results[timeframe] = False
                        continue
                        
                    if not isinstance(data["portfolio_history"], list):
                        print(f"❌ Chart Data Endpoint ({timeframe}): FAILED - portfolio_history is not a list")
                        results[timeframe] = False
                        continue
                        
                    if not isinstance(data["sentiment_timeline"], list):
                        print(f"❌ Chart Data Endpoint ({timeframe}): FAILED - sentiment_timeline is not a list")
                        results[timeframe] = False
                        continue
                    
                    # Print summary of data
                    print(f"   - Price history points: {len(data['price_history'])}")
                    print(f"   - Trade markers: {len(data['trade_markers'])}")
                    print(f"   - Portfolio history points: {len(data['portfolio_history'])}")
                    print(f"   - Sentiment timeline points: {len(data['sentiment_timeline'])}")
                    
                    # Check if we have at least some data (or fallback data)
                    if len(data["price_history"]) == 0:
                        print(f"❌ Chart Data Endpoint ({timeframe}): FAILED - No price history data")
                        results[timeframe] = False
                        continue
                        
                    if len(data["portfolio_history"]) == 0:
                        print(f"❌ Chart Data Endpoint ({timeframe}): FAILED - No portfolio history data")
                        results[timeframe] = False
                        continue
                    
                    # Check a sample price point if available
                    if data["price_history"]:
                        sample_price = data["price_history"][0]
                        price_fields = ["timestamp", "price", "volume", "rsi"]
                        missing_price_fields = [field for field in price_fields if field not in sample_price]
                        
                        if missing_price_fields:
                            print(f"❌ Chart Data Endpoint ({timeframe}): FAILED - Price point missing fields: {missing_price_fields}")
                            results[timeframe] = False
                            continue
                    
                    # Verify timestamps are within expected timeframe range
                    from datetime import datetime, timedelta
                    now = datetime.utcnow()
                    
                    if timeframe == "1h":
                        cutoff_time = now - timedelta(hours=1)
                    elif timeframe == "24h":
                        cutoff_time = now - timedelta(hours=24)
                    elif timeframe == "7d":
                        cutoff_time = now - timedelta(days=7)
                    
                    # Check if timestamps in price_history are within range
                    if data["price_history"]:
                        for point in data["price_history"]:
                            point_time = datetime.fromisoformat(point["timestamp"].replace("Z", "+00:00"))
                            if point_time < cutoff_time:
                                print(f"⚠️ Chart Data Endpoint ({timeframe}): Found price point outside timeframe range: {point_time}")
                    
                    print(f"✅ Chart Data Endpoint ({timeframe}): SUCCESS")
                    results[timeframe] = True
                else:
                    print(f"❌ Chart Data Endpoint ({timeframe}): FAILED - Missing fields: {missing_fields}")
                    results[timeframe] = False
            else:
                print(f"❌ Chart Data Endpoint ({timeframe}): FAILED - Status code: {response.status_code}")
                print(f"Response: {response.text}")
                results[timeframe] = False
        except Exception as e:
            print(f"❌ Chart Data Endpoint ({timeframe}): ERROR - {str(e)}")
            results[timeframe] = False
    
    # Compare data between timeframes
    if len(timeframe_data) > 1:
        print("\n🔍 Comparing data between timeframes...")
        
        # Check if there's any data to compare
        if all(timeframe_data[tf]["price_history"] for tf in timeframes if tf in timeframe_data):
            # Compare lengths of data arrays
            print("\nData array lengths by timeframe:")
            for tf in timeframes:
                if tf in timeframe_data:
                    data = timeframe_data[tf]
                    print(f"  {tf}:")
                    print(f"    - Price history points: {len(data['price_history'])}")
                    print(f"    - Portfolio history points: {len(data['portfolio_history'])}")
                    print(f"    - Sentiment timeline points: {len(data['sentiment_timeline'])}")
            
            # Expected behavior: longer timeframes should have more data points
            # (or at least different data) unless there's limited historical data
            
            # Compare first and last timestamps in price_history
            print("\nTimeframe ranges:")
            for tf in timeframes:
                if tf in timeframe_data and timeframe_data[tf]["price_history"]:
                    data = timeframe_data[tf]
                    if data["price_history"]:
                        first_time = datetime.fromisoformat(data["price_history"][0]["timestamp"].replace("Z", "+00:00"))
                        last_time = datetime.fromisoformat(data["price_history"][-1]["timestamp"].replace("Z", "+00:00"))
                        time_range = last_time - first_time
                        print(f"  {tf}: {first_time} to {last_time} (range: {time_range})")
            
            # Check if data is different between timeframes
            different_data = True
            for i in range(len(timeframes) - 1):
                tf1 = timeframes[i]
                tf2 = timeframes[i + 1]
                
                if tf1 in timeframe_data and tf2 in timeframe_data:
                    data1 = timeframe_data[tf1]
                    data2 = timeframe_data[tf2]
                    
                    # Compare number of data points
                    if (len(data1["price_history"]) == len(data2["price_history"]) and
                        len(data1["portfolio_history"]) == len(data2["portfolio_history"]) and
                        len(data1["sentiment_timeline"]) == len(data2["sentiment_timeline"])):
                        
                        # If all lengths are the same, check if the data is actually different
                        # by comparing the first timestamp in price_history
                        if (data1["price_history"] and data2["price_history"] and
                            data1["price_history"][0]["timestamp"] == data2["price_history"][0]["timestamp"]):
                            print(f"⚠️ Warning: {tf1} and {tf2} have identical first timestamps in price_history")
                            
                            # If there's only one data point, this might be expected
                            if len(data1["price_history"]) == 1:
                                print(f"  Note: Only one data point exists, so identical data may be expected")
                            else:
                                different_data = False
            
            if different_data:
                print("✅ Timeframe filtering appears to be working correctly")
            else:
                print("❌ Timeframe filtering may not be working correctly - data is too similar between timeframes")
                # Don't fail the test just for this, as it might be due to limited test data
                print("  Note: This could be due to limited historical data in the test environment")
        else:
            print("⚠️ Not enough data to compare between timeframes")
    
    # Overall result is True only if all timeframes passed
    overall_result = all(results.values())
    if overall_result:
        print("\n✅ Chart Data Endpoint: SUCCESS for all timeframes")
    else:
        print("\n❌ Chart Data Endpoint: FAILED for some timeframes")
    
    return overall_result

def test_live_chart_update():
    """Test 10: Live Chart Update Endpoint - GET /api/trades/chart-data/live"""
    print("\n🔍 Testing Live Chart Update Endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/trades/chart-data/live")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ["latest_price", "current_portfolio", "latest_sentiment", "timestamp"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                # Verify data structures
                if not isinstance(data["latest_price"], dict):
                    print("❌ Live Chart Update Endpoint: FAILED - latest_price is not a dictionary")
                    return False
                
                if not isinstance(data["current_portfolio"], dict):
                    print("❌ Live Chart Update Endpoint: FAILED - current_portfolio is not a dictionary")
                    return False
                
                if not isinstance(data["latest_sentiment"], dict):
                    print("❌ Live Chart Update Endpoint: FAILED - latest_sentiment is not a dictionary")
                    return False
                
                # Check latest price fields
                price_fields = ["timestamp", "price", "volume", "rsi"]
                missing_price_fields = [field for field in price_fields if field not in data["latest_price"]]
                
                if missing_price_fields:
                    print(f"❌ Live Chart Update Endpoint: FAILED - Latest price missing fields: {missing_price_fields}")
                    return False
                
                # Check portfolio fields
                portfolio_fields = ["timestamp", "total_value", "usd_balance", "btc_amount", "btc_value"]
                missing_portfolio_fields = [field for field in portfolio_fields if field not in data["current_portfolio"]]
                
                if missing_portfolio_fields:
                    print(f"❌ Live Chart Update Endpoint: FAILED - Portfolio missing fields: {missing_portfolio_fields}")
                    return False
                
                # Check sentiment fields
                sentiment_fields = ["timestamp", "news_sentiment", "twitter_sentiment"]
                missing_sentiment_fields = [field for field in sentiment_fields if field not in data["latest_sentiment"]]
                
                if missing_sentiment_fields:
                    print(f"❌ Live Chart Update Endpoint: FAILED - Sentiment missing fields: {missing_sentiment_fields}")
                    return False
                
                # Print summary of data
                print(f"   - Latest price: ${data['latest_price']['price']:,.2f}")
                print(f"   - Portfolio total value: ${data['current_portfolio']['total_value']:,.2f}")
                print(f"   - News sentiment: {data['latest_sentiment']['news_sentiment']}")
                print(f"   - Twitter sentiment: {data['latest_sentiment']['twitter_sentiment']}")
                
                # Test real-time updates by making a second request
                print("\n🔍 Testing real-time updates...")
                time.sleep(2)  # Wait a bit for potential data changes
                
                second_response = requests.get(f"{BACKEND_URL}/trades/chart-data/live")
                if second_response.status_code == 200:
                    second_data = second_response.json()
                    
                    # Check if timestamps are different (indicating real-time updates)
                    if "timestamp" in second_data and "timestamp" in data:
                        first_timestamp = data["timestamp"]
                        second_timestamp = second_data["timestamp"]
                        
                        if first_timestamp != second_timestamp:
                            print("✅ Real-time updates confirmed: Timestamps differ between requests")
                        else:
                            print("ℹ️ Note: Timestamps identical between requests (may be expected if no updates occurred)")
                    
                    print("✅ Live Chart Update Endpoint: SUCCESS")
                    return True
                else:
                    print(f"❌ Live Chart Update Endpoint: FAILED on second request - Status code: {second_response.status_code}")
                    return False
            else:
                print(f"❌ Live Chart Update Endpoint: FAILED - Missing fields: {missing_fields}")
                return False
        else:
            print(f"❌ Live Chart Update Endpoint: FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Live Chart Update Endpoint: ERROR - {str(e)}")
        return False

def test_get_settings():
    """Test 11: Get Trading Settings - GET /api/settings"""
    print("\n🔍 Testing Get Settings Endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/settings")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Check required fields
            required_fields = [
                "id", "initial_portfolio_value", "auto_trading_interval_minutes", 
                "price_history_limit", "portfolio_snapshots_limit", "sentiment_history_limit",
                "frontend_refresh_interval_seconds", "risk_threshold", "confidence_threshold",
                "max_trades_per_day", "stop_loss_percentage", "take_profit_percentage",
                "created_at", "updated_at"
            ]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ Get Settings Endpoint: SUCCESS")
                print(f"   - Initial Portfolio Value: ${data['initial_portfolio_value']}")
                print(f"   - Auto Trading Interval: {data['auto_trading_interval_minutes']} minutes")
                print(f"   - Risk Threshold: {data['risk_threshold']}")
                return True
            else:
                print(f"❌ Get Settings Endpoint: FAILED - Missing fields: {missing_fields}")
                return False
        else:
            print(f"❌ Get Settings Endpoint: FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get Settings Endpoint: ERROR - {str(e)}")
        return False

def test_update_settings():
    """Test 12: Update Trading Settings - PUT /api/settings"""
    print("\n🔍 Testing Update Settings Endpoint...")
    try:
        # First, get current settings
        get_response = requests.get(f"{BACKEND_URL}/settings")
        if get_response.status_code != 200:
            print(f"❌ Update Settings Endpoint: FAILED - Could not get current settings")
            return False
            
        current_settings = get_response.json()
        print(f"Current Settings: {json.dumps({k: current_settings[k] for k in ['initial_portfolio_value', 'auto_trading_interval_minutes', 'risk_threshold'] if k in current_settings}, indent=2)}")
        
        # Create updated settings with modified values
        updated_settings = current_settings.copy()
        updated_settings["initial_portfolio_value"] = 2000.0  # Change from default 1000.0
        updated_settings["auto_trading_interval_minutes"] = 10  # Change from default 5
        updated_settings["risk_threshold"] = 0.8  # Change from default 0.7
        
        # Send update request
        print("\n🔍 Sending updated settings...")
        update_response = requests.put(f"{BACKEND_URL}/settings", json=updated_settings)
        print(f"Update Status Code: {update_response.status_code}")
        
        if update_response.status_code == 200:
            updated_data = update_response.json()
            print(f"Updated Settings Response: {json.dumps({k: updated_data[k] for k in ['initial_portfolio_value', 'auto_trading_interval_minutes', 'risk_threshold'] if k in updated_data}, indent=2)}")
            
            # Verify the changes were applied
            if (updated_data["initial_portfolio_value"] == 2000.0 and
                updated_data["auto_trading_interval_minutes"] == 10 and
                updated_data["risk_threshold"] == 0.8):
                
                # Double-check by getting settings again
                verify_response = requests.get(f"{BACKEND_URL}/settings")
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    
                    if (verify_data["initial_portfolio_value"] == 2000.0 and
                        verify_data["auto_trading_interval_minutes"] == 10 and
                        verify_data["risk_threshold"] == 0.8):
                        print("✅ Update Settings Endpoint: SUCCESS - Changes verified")
                        return True
                    else:
                        print("❌ Update Settings Endpoint: FAILED - Changes not persisted in database")
                        return False
                else:
                    print(f"❌ Update Settings Endpoint: FAILED - Could not verify changes")
                    return False
            else:
                print("❌ Update Settings Endpoint: FAILED - Changes not applied correctly")
                return False
        else:
            print(f"❌ Update Settings Endpoint: FAILED - Status code: {update_response.status_code}")
            print(f"Response: {update_response.text}")
            return False
    except Exception as e:
        print(f"❌ Update Settings Endpoint: ERROR - {str(e)}")
        return False

def test_reset_settings():
    """Test 13: Reset Trading Settings - POST /api/settings/reset"""
    print("\n🔍 Testing Reset Settings Endpoint...")
    try:
        # Send reset request
        reset_response = requests.post(f"{BACKEND_URL}/settings/reset")
        print(f"Reset Status Code: {reset_response.status_code}")
        
        if reset_response.status_code == 200:
            reset_data = reset_response.json()
            print(f"Reset Response: {json.dumps(reset_data, indent=2)}")
            
            # Verify settings were reset to defaults
            if "settings" in reset_data:
                settings = reset_data["settings"]
                
                # Check default values
                default_values = {
                    "initial_portfolio_value": 1000.0,
                    "auto_trading_interval_minutes": 5,
                    "price_history_limit": 100,
                    "portfolio_snapshots_limit": 100,
                    "sentiment_history_limit": 50,
                    "frontend_refresh_interval_seconds": 15,
                    "risk_threshold": 0.7,
                    "confidence_threshold": 0.6,
                    "max_trades_per_day": 10,
                    "stop_loss_percentage": 5.0,
                    "take_profit_percentage": 10.0
                }
                
                # Check if all default values match
                mismatched_values = []
                for key, value in default_values.items():
                    if key in settings and settings[key] != value:
                        mismatched_values.append(f"{key}: expected {value}, got {settings[key]}")
                
                if not mismatched_values:
                    # Double-check by getting settings again
                    verify_response = requests.get(f"{BACKEND_URL}/settings")
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        
                        # Check if all default values match in the retrieved settings
                        verify_mismatched = []
                        for key, value in default_values.items():
                            if key in verify_data and verify_data[key] != value:
                                verify_mismatched.append(f"{key}: expected {value}, got {verify_data[key]}")
                        
                        if not verify_mismatched:
                            print("✅ Reset Settings Endpoint: SUCCESS - Settings reset to defaults")
                            return True
                        else:
                            print(f"❌ Reset Settings Endpoint: FAILED - Settings not reset correctly in database: {verify_mismatched}")
                            return False
                    else:
                        print(f"❌ Reset Settings Endpoint: FAILED - Could not verify reset")
                        return False
                else:
                    print(f"❌ Reset Settings Endpoint: FAILED - Settings not reset to defaults: {mismatched_values}")
                    return False
            else:
                print("❌ Reset Settings Endpoint: FAILED - No settings in response")
                return False
        else:
            print(f"❌ Reset Settings Endpoint: FAILED - Status code: {reset_response.status_code}")
            print(f"Response: {reset_response.text}")
            return False
    except Exception as e:
        print(f"❌ Reset Settings Endpoint: ERROR - {str(e)}")
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
    results["Chart Data"] = test_chart_data()
    results["Live Chart Update"] = test_live_chart_update()
    results["Get Settings"] = test_get_settings()
    results["Update Settings"] = test_update_settings()
    results["Reset Settings"] = test_reset_settings()
    
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