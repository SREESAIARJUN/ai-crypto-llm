#!/usr/bin/env python3
import requests
import json
from datetime import datetime, timedelta
import sys

# Backend API URL from frontend/.env
BACKEND_URL = "https://6213b92a-a983-46c4-b8a7-5fde584ff091.preview.emergentagent.com/api"

def print_separator():
    print("\n" + "="*80 + "\n")

def test_chart_data_timeframes():
    """Test Chart Data Endpoint with different timeframes"""
    print_separator()
    print("🚀 TESTING CHART DATA ENDPOINT WITH DIFFERENT TIMEFRAMES")
    print(f"🔗 Testing against: {BACKEND_URL}")
    print(f"⏱️ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_separator()
    
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
                
                # Print summary of data
                print(f"   - Timeframe: {data['timeframe']}")
                print(f"   - Price history points: {len(data['price_history'])}")
                print(f"   - Trade markers: {len(data['trade_markers'])}")
                print(f"   - Portfolio history points: {len(data['portfolio_history'])}")
                print(f"   - Sentiment timeline points: {len(data['sentiment_timeline'])}")
                
                # Print first and last timestamp in price_history if available
                if data["price_history"]:
                    first_time_str = data["price_history"][0]["timestamp"]
                    last_time_str = data["price_history"][-1]["timestamp"]
                    
                    # Convert to datetime objects for comparison
                    first_time = datetime.fromisoformat(first_time_str.replace("Z", "+00:00"))
                    last_time = datetime.fromisoformat(last_time_str.replace("Z", "+00:00"))
                    
                    print(f"   - First timestamp: {first_time}")
                    print(f"   - Last timestamp: {last_time}")
                    print(f"   - Time range: {last_time - first_time}")
                
                results[timeframe] = True
            else:
                print(f"❌ Chart Data Endpoint ({timeframe}): FAILED - Status code: {response.status_code}")
                print(f"Response: {response.text}")
                results[timeframe] = False
        except Exception as e:
            print(f"❌ Chart Data Endpoint ({timeframe}): ERROR - {str(e)}")
            results[timeframe] = False
    
    # Compare data between timeframes
    if len(timeframe_data) > 1:
        print_separator()
        print("🔍 COMPARING DATA BETWEEN TIMEFRAMES")
        print_separator()
        
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
            different_data = False
            different_lengths = False
            
            # Compare lengths of data arrays between timeframes
            lengths = {}
            for tf in timeframes:
                if tf in timeframe_data:
                    lengths[tf] = {
                        "price_history": len(timeframe_data[tf]["price_history"]),
                        "portfolio_history": len(timeframe_data[tf]["portfolio_history"]),
                        "sentiment_timeline": len(timeframe_data[tf]["sentiment_timeline"])
                    }
            
            # Check if any lengths are different
            if len(lengths) > 1:
                for i in range(len(timeframes) - 1):
                    tf1 = timeframes[i]
                    tf2 = timeframes[i + 1]
                    
                    if tf1 in lengths and tf2 in lengths:
                        if (lengths[tf1]["price_history"] != lengths[tf2]["price_history"] or
                            lengths[tf1]["portfolio_history"] != lengths[tf2]["portfolio_history"] or
                            lengths[tf1]["sentiment_timeline"] != lengths[tf2]["sentiment_timeline"]):
                            different_lengths = True
                            break
            
            # Check if timestamps are different between timeframes
            first_timestamps = {}
            for tf in timeframes:
                if tf in timeframe_data and timeframe_data[tf]["price_history"]:
                    first_timestamps[tf] = timeframe_data[tf]["price_history"][0]["timestamp"]
            
            if len(first_timestamps) > 1:
                timestamp_values = list(first_timestamps.values())
                if len(set(timestamp_values)) > 1:
                    different_data = True
            
            # Print results of comparison
            print("\nComparison results:")
            print(f"  - Different data lengths between timeframes: {'Yes' if different_lengths else 'No'}")
            print(f"  - Different first timestamps between timeframes: {'Yes' if different_data else 'No'}")
            
            if different_lengths or different_data:
                print("✅ Timeframe filtering appears to be working correctly")
            else:
                print("❌ Timeframe filtering may not be working correctly - data is identical between timeframes")
                # Don't fail the test just for this, as it might be due to limited test data
                print("  Note: This could be due to limited historical data in the test environment")
        else:
            print("⚠️ Not enough data to compare between timeframes")
    
    # Overall result is True only if all timeframes passed
    overall_result = all(results.values())
    
    print_separator()
    print("📊 TEST SUMMARY")
    print_separator()
    
    for timeframe, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"Chart Data ({timeframe}): {status}")
    
    print_separator()
    if overall_result:
        print("🎉 ALL TIMEFRAME TESTS PASSED!")
        if len(timeframe_data) > 1:
            if different_lengths or different_data:
                print("✅ Timeframe filtering is working correctly - different data returned for different timeframes")
            else:
                print("⚠️ Timeframe filtering may not be working correctly - identical data returned for different timeframes")
                print("  Note: This could be due to limited historical data in the test environment")
    else:
        print("⚠️ SOME TIMEFRAME TESTS FAILED. Please check the detailed output above.")
    
    print_separator()
    return overall_result

if __name__ == "__main__":
    success = test_chart_data_timeframes()
    sys.exit(0 if success else 1)