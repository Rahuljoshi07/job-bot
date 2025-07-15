#!/usr/bin/env python3
"""
Integration test for enhanced fixed_job_bot.py functionality
"""
import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch

# Add current directory to path
sys.path.insert(0, '.')

def setup_test_environment():
    """Setup test environment variables"""
    test_env = {
        'PERSONAL_FULL_NAME': 'Test User',
        'PERSONAL_EMAIL': 'test@example.com',
        'PERSONAL_PHONE': '123-456-7890',
        'PERSONAL_LOCATION': 'Remote',
        'LINKEDIN_EMAIL': 'test@example.com',
        'LINKEDIN_PASSWORD': 'test_password',
        'INDEED_EMAIL': 'test@example.com',
        'INDEED_PASSWORD': 'test_password',
        'DICE_EMAIL': 'test@example.com',
        'DICE_PASSWORD': 'test_password',
        'TWITTER_EMAIL': 'test@example.com',
        'TWITTER_PASSWORD': 'test_password',
        'TURING_EMAIL': 'test@example.com',
        'TURING_PASSWORD': 'test_password',
        'EMAIL_VERIFICATION_ENABLED': 'false',  # Disable for testing
        'CI': 'true',  # Enable CI mode for headless testing
        'GITHUB_ACTIONS': 'true'
    }
    
    for key, value in test_env.items():
        os.environ[key] = value

def test_enhanced_run_platform_cycle():
    """Test the enhanced run_platform_cycle method"""
    print("🧪 Testing enhanced run_platform_cycle method...")
    
    try:
        setup_test_environment()
        from fixed_job_bot import FixedJobBot
        
        # Create bot instance
        bot = FixedJobBot()
        
        # Mock the browser setup to avoid actual browser initialization
        with patch.object(bot, '_setup_browser', return_value=False):
            # Test platform cycle with mock failure
            result = bot.run_platform_cycle("LinkedIn", max_jobs_per_search=2, max_retries=2)
            
            # Verify result structure
            assert isinstance(result, dict), "Result should be a dictionary"
            assert 'success' in result, "Result should have 'success' key"
            assert 'platform' in result, "Result should have 'platform' key"
            assert 'jobs_found' in result, "Result should have 'jobs_found' key"
            assert 'jobs_applied' in result, "Result should have 'jobs_applied' key"
            assert 'duration' in result, "Result should have 'duration' key"
            assert 'retry_count' in result, "Result should have 'retry_count' key"
            
            print("✅ Enhanced run_platform_cycle method test passed")
            print(f"   - Result structure: {list(result.keys())}")
            print(f"   - Success: {result['success']}")
            print(f"   - Platform: {result['platform']}")
            
            return True
            
    except Exception as e:
        print(f"❌ Enhanced run_platform_cycle test failed: {e}")
        return False

def test_comprehensive_cycle():
    """Test the comprehensive cycle method"""
    print("🧪 Testing run_comprehensive_cycle method...")
    
    try:
        setup_test_environment()
        from fixed_job_bot import FixedJobBot
        
        # Create bot instance
        bot = FixedJobBot()
        
        # Mock the browser setup to avoid actual browser initialization
        with patch.object(bot, '_setup_browser', return_value=False):
            # Test comprehensive cycle
            result = bot.run_comprehensive_cycle(
                platforms=["LinkedIn", "Indeed"], 
                max_jobs_per_platform=5,
                cycle_delay=1  # Short delay for testing
            )
            
            # Verify result structure
            assert isinstance(result, dict), "Result should be a dictionary"
            assert 'success' in result, "Result should have 'success' key"
            assert 'platform_results' in result, "Result should have 'platform_results' key"
            assert 'duration' in result, "Result should have 'duration' key"
            
            print("✅ run_comprehensive_cycle method test passed")
            print(f"   - Result structure: {list(result.keys())}")
            print(f"   - Success: {result['success']}")
            print(f"   - Platform results: {list(result['platform_results'].keys())}")
            
            return True
            
    except Exception as e:
        print(f"❌ run_comprehensive_cycle test failed: {e}")
        return False

def test_smart_retry_cycle():
    """Test the smart retry cycle method"""
    print("🧪 Testing run_smart_retry_cycle method...")
    
    try:
        setup_test_environment()
        from fixed_job_bot import FixedJobBot
        
        # Create bot instance
        bot = FixedJobBot()
        
        # Test smart retry cycle with empty failed platforms
        result = bot.run_smart_retry_cycle([], max_attempts=1)
        
        # Verify result structure for empty case
        assert isinstance(result, dict), "Result should be a dictionary"
        assert 'success' in result, "Result should have 'success' key"
        assert 'retried_platforms' in result, "Result should have 'retried_platforms' key"
        assert result['success'] == True, "Should succeed with empty failed platforms"
        assert result['retried_platforms'] == [], "Should have empty retried platforms"
        
        print("✅ run_smart_retry_cycle method test passed")
        print(f"   - Result structure: {list(result.keys())}")
        print(f"   - Success: {result['success']}")
        print(f"   - Retried platforms: {result['retried_platforms']}")
        
        return True
        
    except Exception as e:
        print(f"❌ run_smart_retry_cycle test failed: {e}")
        return False

def test_email_verification():
    """Test email verification methods"""
    print("🧪 Testing email verification methods...")
    
    try:
        setup_test_environment()
        from fixed_job_bot import FixedJobBot
        
        # Create bot instance
        bot = FixedJobBot()
        
        # Test email verification with disabled config
        result = bot._enhanced_email_verification_check(
            "LinkedIn", "Software Engineer", "TechCorp", datetime.now()
        )
        
        # Verify result structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert 'status' in result, "Result should have 'status' key"
        assert 'message' in result, "Result should have 'message' key"
        assert result['status'] == 'disabled', "Should be disabled in test config"
        
        print("✅ Email verification methods test passed")
        print(f"   - Status: {result['status']}")
        print(f"   - Message: {result['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Email verification test failed: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    print("🧪 Testing configuration loading...")
    
    try:
        setup_test_environment()
        from config import Config
        
        # Test configuration loading
        config_obj = Config()
        config = config_obj.load_config()
        
        # Verify config structure
        assert isinstance(config, dict), "Config should be a dictionary"
        assert 'personal' in config, "Config should have 'personal' section"
        assert 'platforms' in config, "Config should have 'platforms' section"
        assert 'preferences' in config, "Config should have 'preferences' section"
        assert 'email_verification' in config, "Config should have 'email_verification' section"
        
        print("✅ Configuration loading test passed")
        print(f"   - Personal name: {config['personal']['full_name']}")
        print(f"   - Email verification enabled: {config['email_verification']['enabled']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting integration tests for enhanced job bot...")
    print("=" * 60)
    
    tests = [
        ("Enhanced Platform Cycle", test_enhanced_run_platform_cycle),
        ("Comprehensive Cycle", test_comprehensive_cycle),
        ("Smart Retry Cycle", test_smart_retry_cycle),
        ("Email Verification", test_email_verification),
        ("Configuration Loading", test_config_loading)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"   ❌ Failed: {test_name}")
        except Exception as e:
            print(f"   ❌ Exception in {test_name}: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! Enhanced job bot functionality is working.")
        return 0
    else:
        print("⚠️  Some integration tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())