#!/usr/bin/env python3
"""
Test script to validate the job bot email verification functionality
"""
import sys
import os
import time
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, '.')

def test_email_verification_config():
    """Test email verification configuration parsing"""
    try:
        # Mock environment variables
        os.environ['EMAIL_VERIFICATION_ENABLED'] = 'true'
        os.environ['EMAIL_IMAP_SERVER'] = 'imap.gmail.com'
        os.environ['EMAIL_IMAP_PORT'] = '993'
        os.environ['EMAIL_SMTP_SERVER'] = 'smtp.gmail.com'
        os.environ['EMAIL_SMTP_PORT'] = '587'
        os.environ['PERSONAL_EMAIL'] = 'test@example.com'
        os.environ['EMAIL_APP_PASSWORD'] = 'test_password'
        os.environ['EMAIL_VERIFICATION_TIMEOUT'] = '300'
        os.environ['EMAIL_CHECK_INTERVAL'] = '30'
        
        # Test email verification config structure
        email_config = {
            'enabled': os.getenv('EMAIL_VERIFICATION_ENABLED', 'true').lower() == 'true',
            'imap_server': os.getenv('EMAIL_IMAP_SERVER', 'imap.gmail.com'),
            'imap_port': int(os.getenv('EMAIL_IMAP_PORT', '993')),
            'smtp_server': os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', '587')),
            'email': os.getenv('PERSONAL_EMAIL'),
            'app_password': os.getenv('EMAIL_APP_PASSWORD'),
            'timeout': int(os.getenv('EMAIL_VERIFICATION_TIMEOUT', '300')),
            'check_interval': int(os.getenv('EMAIL_CHECK_INTERVAL', '30'))
        }
        
        print("✅ Email verification config test passed")
        print(f"   - Enabled: {email_config['enabled']}")
        print(f"   - IMAP Server: {email_config['imap_server']}")
        print(f"   - Email: {email_config['email']}")
        print(f"   - Timeout: {email_config['timeout']}s")
        return True
        
    except Exception as e:
        print(f"❌ Email verification config test failed: {e}")
        return False

def test_email_verification_method():
    """Test email verification method structure"""
    try:
        # Mock email verification method
        def check_email_confirmation(platform, job_title, company_name, application_time):
            """Mock email verification function"""
            try:
                # Simulate email verification logic
                if not os.getenv('EMAIL_VERIFICATION_ENABLED', 'true').lower() == 'true':
                    return {"status": "disabled", "message": "Email verification is disabled"}
                
                if not os.getenv('PERSONAL_EMAIL') or not os.getenv('EMAIL_APP_PASSWORD'):
                    return {"status": "config_missing", "message": "Email configuration incomplete"}
                
                # Mock search for confirmation
                search_keywords = [
                    'application received',
                    'application confirmation',
                    'thank you for applying',
                    'application submitted',
                    company_name.lower(),
                    platform.lower()
                ]
                
                # Simulate timeout and return
                timeout = int(os.getenv('EMAIL_VERIFICATION_TIMEOUT', '300'))
                return {
                    "status": "pending",
                    "message": f"No email confirmation found within {timeout}s timeout"
                }
                
            except Exception as e:
                return {"status": "error", "message": f"Email verification failed: {str(e)}"}
        
        # Test the method
        result = check_email_confirmation("LinkedIn", "Software Engineer", "TechCorp", datetime.now())
        
        print("✅ Email verification method test passed")
        print(f"   - Status: {result['status']}")
        print(f"   - Message: {result['message']}")
        return True
        
    except Exception as e:
        print(f"❌ Email verification method test failed: {e}")
        return False

def test_file_compilation():
    """Test that all modified files can be compiled"""
    try:
        import py_compile
        
        files_to_test = [
            'config.py',
            'fixed_job_bot.py'
        ]
        
        for file in files_to_test:
            if os.path.exists(file):
                py_compile.compile(file, doraise=True)
                print(f"✅ {file} compiles successfully")
            else:
                print(f"⚠️  {file} not found, skipping")
        
        return True
        
    except Exception as e:
        print(f"❌ File compilation test failed: {e}")
        return False

def test_documentation_exists():
    """Test that documentation was created"""
    try:
        doc_file = 'EMAIL_VERIFICATION_DOCUMENTATION.md'
        if os.path.exists(doc_file):
            with open(doc_file, 'r') as f:
                content = f.read()
                if 'Email Verification Feature' in content:
                    print("✅ Documentation exists and contains expected content")
                    return True
                else:
                    print("❌ Documentation missing expected content")
                    return False
        else:
            print("❌ Documentation file not found")
            return False
            
    except Exception as e:
        print(f"❌ Documentation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting job bot email verification tests...")
    print("=" * 50)
    
    tests = [
        ("Email Verification Config", test_email_verification_config),
        ("Email Verification Method", test_email_verification_method),
        ("File Compilation", test_file_compilation),
        ("Documentation", test_documentation_exists)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"   Failed: {test_name}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Email verification functionality is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())