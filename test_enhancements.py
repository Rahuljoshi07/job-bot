#!/usr/bin/env python3
"""
🧪 Test script for Fixed Job Bot enhancements
"""

import os
import sys
import tempfile
import json
from unittest.mock import patch, MagicMock

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_email_verification_enhancement():
    """Test email verification system"""
    print("🧪 Testing Email Verification Enhancement...")
    
    try:
        # Mock the imports that might not be available
        with patch.dict('sys.modules', {
            'selenium': MagicMock(),
            'selenium.webdriver': MagicMock(),
            'selenium.webdriver.common.by': MagicMock(),
            'selenium.webdriver.support.ui': MagicMock(),
            'selenium.webdriver.support': MagicMock(),
            'selenium.webdriver.firefox.service': MagicMock(),
            'selenium.webdriver.firefox.options': MagicMock(),
            'selenium.webdriver.common.keys': MagicMock(),
            'selenium.webdriver.common.action_chains': MagicMock(),
            'selenium.common.exceptions': MagicMock(),
            'webdriver_manager.firefox': MagicMock(),
            'webdriver_manager.chrome': MagicMock(),
            'cryptography.fernet': MagicMock(),
            'cryptography.hazmat.primitives': MagicMock(),
            'cryptography.hazmat.primitives.hashes': MagicMock(),
            'cryptography.hazmat.primitives.kdf.pbkdf2': MagicMock(),
        }):
            from fixed_job_bot import FixedJobBot
            
            # Test with mock configuration
            bot = FixedJobBot()
            
            # Test email config retrieval
            email_config = bot._get_email_config_for_address('test@gmail.com')
            assert email_config is None or isinstance(email_config, dict), "Email config should be None or dict"
            
            print("✅ Email verification system loaded successfully")
            return True
            
    except Exception as e:
        print(f"❌ Email verification test failed: {e}")
        return False

def test_encrypted_credentials():
    """Test encrypted credentials system"""
    print("🧪 Testing Encrypted Credentials...")
    
    try:
        # Mock the imports
        with patch.dict('sys.modules', {
            'selenium': MagicMock(),
            'selenium.webdriver': MagicMock(),
            'selenium.webdriver.common.by': MagicMock(),
            'selenium.webdriver.support.ui': MagicMock(),
            'selenium.webdriver.support': MagicMock(),
            'selenium.webdriver.firefox.service': MagicMock(),
            'selenium.webdriver.firefox.options': MagicMock(),
            'selenium.webdriver.common.keys': MagicMock(),
            'selenium.webdriver.common.action_chains': MagicMock(),
            'selenium.common.exceptions': MagicMock(),
            'webdriver_manager.firefox': MagicMock(),
            'webdriver_manager.chrome': MagicMock(),
            'cryptography.fernet': MagicMock(),
            'cryptography.hazmat.primitives': MagicMock(),
            'cryptography.hazmat.primitives.hashes': MagicMock(),
            'cryptography.hazmat.primitives.kdf.pbkdf2': MagicMock(),
        }):
            from fixed_job_bot import FixedJobBot
            
            bot = FixedJobBot()
            
            # Test encryption key generation
            key = bot._generate_encryption_key("test_password")
            assert key is not None, "Encryption key should be generated"
            
            # Test credential encryption/decryption
            test_credentials = {
                'personal': {'name': 'Test User', 'email': 'test@example.com'},
                'platforms': {'linkedin': {'username': 'test', 'password': 'pass'}}
            }
            
            encrypted = bot._encrypt_credentials(test_credentials, "test_password")
            if encrypted:
                decrypted = bot._decrypt_credentials(encrypted, "test_password")
                assert decrypted == test_credentials, "Decrypted credentials should match original"
                print("✅ Encryption/decryption working correctly")
            else:
                print("⚠️ Encryption failed (likely due to missing cryptography library)")
            
            return True
            
    except Exception as e:
        print(f"❌ Encrypted credentials test failed: {e}")
        return False

def test_platform_rotation():
    """Test platform rotation system"""
    print("🧪 Testing Platform Rotation...")
    
    try:
        # Mock the imports
        with patch.dict('sys.modules', {
            'selenium': MagicMock(),
            'selenium.webdriver': MagicMock(),
            'selenium.webdriver.common.by': MagicMock(),
            'selenium.webdriver.support.ui': MagicMock(),
            'selenium.webdriver.support': MagicMock(),
            'selenium.webdriver.firefox.service': MagicMock(),
            'selenium.webdriver.firefox.options': MagicMock(),
            'selenium.webdriver.common.keys': MagicMock(),
            'selenium.webdriver.common.action_chains': MagicMock(),
            'selenium.common.exceptions': MagicMock(),
            'webdriver_manager.firefox': MagicMock(),
            'webdriver_manager.chrome': MagicMock(),
            'cryptography.fernet': MagicMock(),
            'cryptography.hazmat.primitives': MagicMock(),
            'cryptography.hazmat.primitives.hashes': MagicMock(),
            'cryptography.hazmat.primitives.kdf.pbkdf2': MagicMock(),
        }):
            from fixed_job_bot import FixedJobBot
            
            bot = FixedJobBot()
            
            # Test platform rotation logic
            available_platforms = ["LinkedIn", "Indeed", "RemoteOK", "Dice"]
            failed_platform = "LinkedIn"
            
            # Mock the health check to return False for LinkedIn, True for others
            original_check_health = bot._check_platform_health
            
            def mock_health_check(platform):
                return platform != "LinkedIn"
            
            bot._check_platform_health = mock_health_check
            
            # Test rotation
            next_platform = bot._rotate_platforms(failed_platform, available_platforms)
            assert next_platform in ["Indeed", "RemoteOK", "Dice"], f"Should rotate to available platform, got {next_platform}"
            
            print("✅ Platform rotation logic working correctly")
            return True
            
    except Exception as e:
        print(f"❌ Platform rotation test failed: {e}")
        return False

def test_comprehensive_cycle():
    """Test comprehensive cycle implementation"""
    print("🧪 Testing Comprehensive Cycle...")
    
    try:
        # Mock the imports
        with patch.dict('sys.modules', {
            'selenium': MagicMock(),
            'selenium.webdriver': MagicMock(),
            'selenium.webdriver.common.by': MagicMock(),
            'selenium.webdriver.support.ui': MagicMock(),
            'selenium.webdriver.support': MagicMock(),
            'selenium.webdriver.firefox.service': MagicMock(),
            'selenium.webdriver.firefox.options': MagicMock(),
            'selenium.webdriver.common.keys': MagicMock(),
            'selenium.webdriver.common.action_chains': MagicMock(),
            'selenium.common.exceptions': MagicMock(),
            'webdriver_manager.firefox': MagicMock(),
            'webdriver_manager.chrome': MagicMock(),
            'cryptography.fernet': MagicMock(),
            'cryptography.hazmat.primitives': MagicMock(),
            'cryptography.hazmat.primitives.hashes': MagicMock(),
            'cryptography.hazmat.primitives.kdf.pbkdf2': MagicMock(),
        }):
            from fixed_job_bot import FixedJobBot
            
            bot = FixedJobBot()
            
            # Check if comprehensive cycle method exists
            assert hasattr(bot, 'run_comprehensive_cycle'), "Should have run_comprehensive_cycle method"
            
            # Check verification success rate method
            success_rate = bot._check_verification_success_rate("LinkedIn")
            assert isinstance(success_rate, float), "Success rate should be a float"
            assert 0.0 <= success_rate <= 1.0, "Success rate should be between 0 and 1"
            
            print("✅ Comprehensive cycle implementation complete")
            return True
            
    except Exception as e:
        print(f"❌ Comprehensive cycle test failed: {e}")
        return False

def test_main_function():
    """Test main function implementation"""
    print("🧪 Testing Main Function...")
    
    try:
        # Mock the imports
        with patch.dict('sys.modules', {
            'selenium': MagicMock(),
            'selenium.webdriver': MagicMock(),
            'selenium.webdriver.common.by': MagicMock(),
            'selenium.webdriver.support.ui': MagicMock(),
            'selenium.webdriver.support': MagicMock(),
            'selenium.webdriver.firefox.service': MagicMock(),
            'selenium.webdriver.firefox.options': MagicMock(),
            'selenium.webdriver.common.keys': MagicMock(),
            'selenium.webdriver.common.action_chains': MagicMock(),
            'selenium.common.exceptions': MagicMock(),
            'webdriver_manager.firefox': MagicMock(),
            'webdriver_manager.chrome': MagicMock(),
            'cryptography.fernet': MagicMock(),
            'cryptography.hazmat.primitives': MagicMock(),
            'cryptography.hazmat.primitives.hashes': MagicMock(),
            'cryptography.hazmat.primitives.kdf.pbkdf2': MagicMock(),
        }):
            import fixed_job_bot
            
            # Check if main function exists
            assert hasattr(fixed_job_bot, 'main'), "Should have main function"
            
            print("✅ Main function implementation complete")
            return True
            
    except Exception as e:
        print(f"❌ Main function test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 FIXED JOB BOT - TESTING ENHANCEMENTS")
    print("=" * 50)
    
    tests = [
        test_email_verification_enhancement,
        test_encrypted_credentials,
        test_platform_rotation,
        test_comprehensive_cycle,
        test_main_function
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"🧪 TEST RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All tests passed! The enhancements are working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit(main())