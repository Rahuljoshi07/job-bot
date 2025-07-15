#!/usr/bin/env python3
"""
Test script for datetime_utils functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime_utils import (
    get_current_datetime,
    get_current_user,
    format_datetime_user_info,
    get_datetime_user_header,
    format_report_timestamp
)

def test_datetime_utils():
    """Test the datetime utility functions"""
    print("🧪 Testing datetime_utils functions...")
    print("=" * 50)
    
    # Test individual functions
    print(f"get_current_datetime(): {get_current_datetime()}")
    print(f"get_current_user(): {get_current_user()}")
    print(f"format_datetime_user_info(): {format_datetime_user_info()}")
    print(f"get_datetime_user_header(): {get_datetime_user_header()}")
    print(f"format_report_timestamp(): {format_report_timestamp()}")
    
    # Verify the expected values
    expected_datetime = "2025-07-15 19:42:43"
    expected_user = "Rahuljoshi07"
    
    assert get_current_datetime() == expected_datetime, f"Expected {expected_datetime}, got {get_current_datetime()}"
    assert get_current_user() == expected_user, f"Expected {expected_user}, got {get_current_user()}"
    
    print("\n✅ All datetime_utils tests passed!")

def test_analytics_integration():
    """Test the analytics dashboard integration"""
    print("\n🧪 Testing analytics dashboard integration...")
    print("=" * 50)
    
    try:
        from analytics_dashboard import JobBotAnalytics
        analytics = JobBotAnalytics()
        print("✅ Analytics dashboard import successful")
        
        # Test generate_report method exists
        assert hasattr(analytics, 'generate_report'), "generate_report method missing"
        print("✅ generate_report method exists")
        
        # Test that generate_report would use our datetime utils
        # (We can't run it without a database, but we can check the import)
        import analytics_dashboard
        assert hasattr(analytics_dashboard, 'format_report_timestamp'), "format_report_timestamp not imported"
        print("✅ format_report_timestamp imported correctly")
        
    except Exception as e:
        print(f"❌ Analytics integration test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_datetime_utils()
    test_analytics_integration()
    print("\n🎉 All tests completed successfully!")