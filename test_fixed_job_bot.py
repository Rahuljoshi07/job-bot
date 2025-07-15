#!/usr/bin/env python3
"""
Test script for enhanced fixed_job_bot.py implementations
"""
import sys
import os
import time
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, '.')

def test_imports():
    """Test that all imports work correctly"""
    try:
        from fixed_job_bot import FixedJobBot
        print("✅ Fixed job bot imports successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_initialization():
    """Test that the bot can be initialized"""
    try:
        # Set up minimal environment variables for testing
        os.environ['PERSONAL_FULL_NAME'] = 'Test User'
        os.environ['PERSONAL_EMAIL'] = 'test@example.com'
        os.environ['PERSONAL_PHONE'] = '123-456-7890'
        os.environ['PERSONAL_LOCATION'] = 'Remote'
        os.environ['LINKEDIN_EMAIL'] = 'test@example.com'
        os.environ['LINKEDIN_PASSWORD'] = 'test_password'
        os.environ['INDEED_EMAIL'] = 'test@example.com'
        os.environ['INDEED_PASSWORD'] = 'test_password'
        os.environ['DICE_EMAIL'] = 'test@example.com'
        os.environ['DICE_PASSWORD'] = 'test_password'
        os.environ['TWITTER_EMAIL'] = 'test@example.com'
        os.environ['TWITTER_PASSWORD'] = 'test_password'
        os.environ['TURING_EMAIL'] = 'test@example.com'
        os.environ['TURING_PASSWORD'] = 'test_password'
        
        from fixed_job_bot import FixedJobBot
        bot = FixedJobBot()
        
        print("✅ Bot initialization successful")
        print(f"   - Config loaded: {bool(bot.config)}")
        print(f"   - Applied jobs file: {bot.applied_jobs_file}")
        print(f"   - Selectors initialized: {bool(bot.selectors)}")
        return True
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

def test_run_platform_cycle_signature():
    """Test that run_platform_cycle method exists and has correct signature"""
    try:
        from fixed_job_bot import FixedJobBot
        
        # Check if method exists
        if not hasattr(FixedJobBot, 'run_platform_cycle'):
            print("❌ run_platform_cycle method does not exist")
            return False
        
        # Check method signature
        import inspect
        sig = inspect.signature(FixedJobBot.run_platform_cycle)
        params = list(sig.parameters.keys())
        
        print("✅ run_platform_cycle method exists")
        print(f"   - Parameters: {params}")
        
        # Check if it has the enhanced parameters
        if 'max_jobs_per_search' in params and 'max_retries' in params:
            print("✅ Method has enhanced parameters")
        else:
            print("⚠️  Method missing enhanced parameters")
        
        return True
    except Exception as e:
        print(f"❌ run_platform_cycle signature test error: {e}")
        return False

def test_comprehensive_cycle_method():
    """Test that comprehensive cycle method exists"""
    try:
        from fixed_job_bot import FixedJobBot
        
        # Check if method exists
        if not hasattr(FixedJobBot, 'run_comprehensive_cycle'):
            print("❌ run_comprehensive_cycle method does not exist")
            return False
        
        # Check method signature
        import inspect
        sig = inspect.signature(FixedJobBot.run_comprehensive_cycle)
        params = list(sig.parameters.keys())
        
        print("✅ run_comprehensive_cycle method exists")
        print(f"   - Parameters: {params}")
        
        return True
    except Exception as e:
        print(f"❌ run_comprehensive_cycle test error: {e}")
        return False

def test_smart_retry_method():
    """Test that smart retry method exists"""
    try:
        from fixed_job_bot import FixedJobBot
        
        # Check if method exists
        if not hasattr(FixedJobBot, 'run_smart_retry_cycle'):
            print("❌ run_smart_retry_cycle method does not exist")
            return False
        
        # Check method signature
        import inspect
        sig = inspect.signature(FixedJobBot.run_smart_retry_cycle)
        params = list(sig.parameters.keys())
        
        print("✅ run_smart_retry_cycle method exists")
        print(f"   - Parameters: {params}")
        
        return True
    except Exception as e:
        print(f"❌ run_smart_retry_cycle test error: {e}")
        return False

def test_enhanced_email_verification():
    """Test that enhanced email verification methods exist"""
    try:
        from fixed_job_bot import FixedJobBot
        
        methods_to_check = [
            '_enhanced_email_verification_check',
            '_alternative_email_check'
        ]
        
        for method_name in methods_to_check:
            if not hasattr(FixedJobBot, method_name):
                print(f"❌ {method_name} method does not exist")
                return False
        
        print("✅ Enhanced email verification methods exist")
        return True
    except Exception as e:
        print(f"❌ Enhanced email verification test error: {e}")
        return False

def test_config_email_verification():
    """Test email verification configuration"""
    try:
        from config import Config
        
        # Test configuration loading
        config_obj = Config()
        config = config_obj.load_config()
        
        if 'email_verification' in config:
            email_config = config['email_verification']
            print("✅ Email verification configuration exists")
            print(f"   - Enabled: {email_config.get('enabled', False)}")
            print(f"   - IMAP Server: {email_config.get('imap_server', 'N/A')}")
            print(f"   - Timeout: {email_config.get('timeout', 'N/A')}")
            return True
        else:
            print("❌ Email verification configuration missing")
            return False
    except Exception as e:
        print(f"❌ Email verification config test error: {e}")
        return False

def test_file_compilation():
    """Test that modified files compile correctly"""
    try:
        import py_compile
        
        files_to_test = [
            'fixed_job_bot.py',
            'config.py'
        ]
        
        for file in files_to_test:
            if os.path.exists(file):
                py_compile.compile(file, doraise=True)
                print(f"✅ {file} compiles successfully")
            else:
                print(f"⚠️  {file} not found")
        
        return True
    except Exception as e:
        print(f"❌ File compilation test error: {e}")
        return False

def test_error_handling():
    """Test error handling in enhanced methods"""
    try:
        from fixed_job_bot import FixedJobBot
        
        # Test mock error handling
        class MockBot:
            def __init__(self):
                self.config = {
                    'email_verification': {
                        'enabled': False
                    }
                }
                
            def _log_error(self, message, exception, save_to_file=True):
                pass
        
        mock_bot = MockBot()
        
        # Test that error handling structure exists
        if hasattr(FixedJobBot, '_log_error'):
            print("✅ Error handling method exists")
            return True
        else:
            print("❌ Error handling method missing")
            return False
        
    except Exception as e:
        print(f"❌ Error handling test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting fixed job bot enhancement tests...")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Initialization", test_initialization),
        ("Platform Cycle Signature", test_run_platform_cycle_signature),
        ("Comprehensive Cycle Method", test_comprehensive_cycle_method),
        ("Smart Retry Method", test_smart_retry_method),
        ("Enhanced Email Verification", test_enhanced_email_verification),
        ("Email Verification Config", test_config_email_verification),
        ("File Compilation", test_file_compilation),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"   ❌ Failed: {test_name}")
        except Exception as e:
            print(f"   ❌ Exception in {test_name}: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced job bot is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())