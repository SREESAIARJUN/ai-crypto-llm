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

def test_get_settings():
    """Test 1: Get Trading Settings - GET /api/settings"""
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
    """Test 2: Update Trading Settings - PUT /api/settings"""
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
    """Test 3: Reset Trading Settings - POST /api/settings/reset"""
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

def run_settings_tests():
    print_separator()
    print("🚀 STARTING CRYPTO TRADING AGENT SETTINGS TESTS")
    print(f"🔗 Testing against: {BACKEND_URL}")
    print(f"⏱️ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_separator()
    
    # Dictionary to track test results
    results = {}
    
    # Run settings tests
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
        print("🎉 ALL SETTINGS TESTS PASSED!")
        print("✅ Get Settings: Successfully retrieves current trading settings")
        print("✅ Update Settings: Successfully updates and persists settings changes")
        print("✅ Reset Settings: Successfully resets settings to default values")
    else:
        print("⚠️ SOME SETTINGS TESTS FAILED. Please check the detailed output above.")
    
    print_separator()
    return all_passed

if __name__ == "__main__":
    success = run_settings_tests()
    sys.exit(0 if success else 1)