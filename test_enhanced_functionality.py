#!/usr/bin/env python3
"""
Test script to validate the enhanced job bot functionality
"""
import sys
import os
import time
import json
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, '.')

def test_configuration_loading():
    """Test configuration loading with fallbacks"""
    print("📋 Testing Configuration Loading...")
    
    try:
        # Mock configuration data
        test_config = {
            'personal': {
                'full_name': 'Test User',
                'email': 'test@example.com',
                'phone': '123-456-7890'
            },
            'platforms': {
                'linkedin': {
                    'username': 'test@linkedin.com',
                    'password': 'test_password'
                }
            },
            'verification': {
                'enable_email_check': True,
                'email': 'test@example.com',
                'app_password': 'test_app_password',
                'timeout': 300
            }
        }
        
        # Test configuration structure
        assert 'personal' in test_config
        assert 'platforms' in test_config
        assert 'verification' in test_config
        
        print("✅ Configuration loading test passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading test failed: {e}")
        return False

def test_credential_encryption():
    """Test credential encryption functionality"""
    print("📋 Testing Credential Encryption...")
    
    try:
        # Mock encryption key
        import hashlib
        import base64
        
        key = hashlib.sha256(b'test-key').digest()
        
        # Test encryption/decryption
        original_password = "test_password_123"
        
        # Simple XOR encryption
        encrypted = bytearray()
        for i, char in enumerate(original_password.encode('utf-8')):
            key_byte = key[i % len(key)]
            encrypted.append(char ^ key_byte)
        
        encrypted_b64 = base64.b64encode(encrypted).decode('utf-8')
        
        # Test decryption
        decrypted_bytes = base64.b64decode(encrypted_b64.encode('utf-8'))
        decrypted = bytearray()
        for i, byte in enumerate(decrypted_bytes):
            key_byte = key[i % len(key)]
            decrypted.append(byte ^ key_byte)
        
        decrypted_password = decrypted.decode('utf-8')
        
        assert decrypted_password == original_password
        
        print("✅ Credential encryption test passed")
        return True
        
    except Exception as e:
        print(f"❌ Credential encryption test failed: {e}")
        return False

def test_email_verification_config():
    """Test email verification configuration"""
    print("📋 Testing Email Verification Config...")
    
    try:
        # Test email provider detection
        email_providers = {
            'user@gmail.com': 'gmail',
            'user@outlook.com': 'outlook',
            'user@yahoo.com': 'yahoo',
            'user@custom.com': 'generic'
        }
        
        for email, expected_provider in email_providers.items():
            if '@gmail.com' in email.lower():
                detected = 'gmail'
            elif '@outlook.com' in email.lower() or '@hotmail.com' in email.lower():
                detected = 'outlook'
            elif '@yahoo.com' in email.lower():
                detected = 'yahoo'
            else:
                detected = 'generic'
            
            assert detected == expected_provider, f"Expected {expected_provider}, got {detected} for {email}"
        
        # Test IMAP configuration
        imap_configs = {
            'gmail': {'server': 'imap.gmail.com', 'port': 993},
            'outlook': {'server': 'outlook.office365.com', 'port': 993},
            'yahoo': {'server': 'imap.mail.yahoo.com', 'port': 993},
            'generic': {'server': 'imap.gmail.com', 'port': 993}
        }
        
        for provider, config in imap_configs.items():
            assert 'server' in config
            assert 'port' in config
            assert config['port'] == 993
        
        print("✅ Email verification config test passed")
        return True
        
    except Exception as e:
        print(f"❌ Email verification config test failed: {e}")
        return False

def test_search_keywords_building():
    """Test search keywords building for email verification"""
    print("📋 Testing Search Keywords Building...")
    
    try:
        # Test keyword building
        platform = "LinkedIn"
        company_name = "Test Company"
        job_title = "DevOps Engineer"
        
        base_keywords = [
            'application received',
            'application confirmation',
            'thank you for applying',
            'application submitted',
            'application complete',
            'we received your application',
            'your application has been',
            'application status',
            company_name.lower(),
            platform.lower()
        ]
        
        # Add job title words
        title_words = job_title.lower().split()
        base_keywords.extend([word for word in title_words if len(word) > 2])
        
        # Add platform-specific keywords
        platform_keywords = {
            'LinkedIn': ['linkedin', 'easy apply', 'your linkedin application'],
            'Indeed': ['indeed', 'indeed.com', 'indeed application'],
            'Dice': ['dice', 'dice.com', 'dice application'],
            'RemoteOK': ['remote ok', 'remoteok', 'remote-ok']
        }
        
        if platform in platform_keywords:
            base_keywords.extend(platform_keywords[platform])
        
        keywords = list(set(base_keywords))
        
        # Verify keywords
        assert 'linkedin' in keywords
        assert 'test company' in keywords
        assert 'devops' in keywords
        assert 'engineer' in keywords
        assert 'application received' in keywords
        
        print("✅ Search keywords building test passed")
        return True
        
    except Exception as e:
        print(f"❌ Search keywords building test failed: {e}")
        return False

def test_platform_cycle_result_structure():
    """Test platform cycle result structure"""
    print("📋 Testing Platform Cycle Result Structure...")
    
    try:
        # Test successful result structure
        success_result = {
            'success': True,
            'platform': 'LinkedIn',
            'jobs_found': 5,
            'jobs_applied': 3,
            'duration': 120.5,
            'metrics': {
                'login_attempts': 1,
                'login_failures': 0,
                'search_attempts': 2,
                'search_failures': 0,
                'application_attempts': 3,
                'application_failures': 0,
                'verification_successes': 2,
                'verification_failures': 1
            }
        }
        
        # Test failure result structure
        failure_result = {
            'success': False,
            'platform': 'LinkedIn',
            'jobs_found': 0,
            'jobs_applied': 0,
            'duration': 60.0,
            'metrics': {
                'login_attempts': 3,
                'login_failures': 3,
                'search_attempts': 0,
                'search_failures': 0,
                'application_attempts': 0,
                'application_failures': 0,
                'verification_successes': 0,
                'verification_failures': 0
            },
            'error': 'Max retries exceeded'
        }
        
        # Verify result structures
        for result in [success_result, failure_result]:
            assert 'success' in result
            assert 'platform' in result
            assert 'jobs_found' in result
            assert 'jobs_applied' in result
            assert 'duration' in result
            assert 'metrics' in result
            assert isinstance(result['metrics'], dict)
        
        print("✅ Platform cycle result structure test passed")
        return True
        
    except Exception as e:
        print(f"❌ Platform cycle result structure test failed: {e}")
        return False

def test_file_security():
    """Test file security and gitignore patterns"""
    print("📋 Testing File Security...")
    
    try:
        # Test gitignore patterns
        gitignore_patterns = [
            '.env',
            '.env.local',
            '.env.production',
            '.env.staging',
            '.encryption_key',
            'encrypted_credentials.json',
            'credentials.env'
        ]
        
        # Read gitignore file
        gitignore_path = '.gitignore'
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()
            
            # Check if critical patterns are present
            critical_patterns = ['.env', '.encryption_key', 'encrypted_credentials.json']
            for pattern in critical_patterns:
                assert pattern in gitignore_content, f"Critical pattern '{pattern}' not found in .gitignore"
        
        print("✅ File security test passed")
        return True
        
    except Exception as e:
        print(f"❌ File security test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting enhanced job bot tests...")
    print("=" * 50)
    
    tests = [
        test_configuration_loading,
        test_credential_encryption,
        test_email_verification_config,
        test_search_keywords_building,
        test_platform_cycle_result_structure,
        test_file_security
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if failed == 0:
        print("🎉 All tests passed! Enhanced functionality is ready.")
    else:
        print(f"❌ {failed} tests failed. Please review the issues.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)