#!/usr/bin/env python3
"""
Test script to verify GitHub secrets are accessible
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_secrets():
    """Test that all required secrets are accessible"""
    print("🔐 Testing GitHub Secrets Access")
    print("=" * 50)
    
    # Check if running in GitHub Actions
    is_github_actions = os.environ.get('GITHUB_ACTIONS') == 'true'
    print(f"Running in GitHub Actions: {is_github_actions}")
    
    # Required secrets
    required_secrets = [
        'PERSONAL_FULL_NAME',
        'PERSONAL_EMAIL', 
        'PERSONAL_PHONE',
        'TWITTER_EMAIL',
        'TWITTER_PASSWORD',
        'TURING_EMAIL',
        'TURING_PASSWORD'
    ]
    
    print("\n📋 Checking required secrets:")
    all_present = True
    
    for secret in required_secrets:
        value = os.environ.get(secret)
        if value:
            # Don't print the actual value for security
            print(f"✅ {secret}: SET (length: {len(value)})")
        else:
            print(f"❌ {secret}: NOT SET")
            all_present = False
    
    # Check .env file if it exists
    if os.path.exists('.env'):
        print(f"\n📄 .env file exists (size: {os.path.getsize('.env')} bytes)")
        with open('.env', 'r') as f:
            lines = f.readlines()
            print(f"📄 .env file has {len(lines)} lines")
            
            # Show first few lines (but mask values)
            print("\n🔍 .env file preview (values masked):")
            for i, line in enumerate(lines[:5]):
                if '=' in line:
                    key, _ = line.split('=', 1)
                    print(f"  {key}=***MASKED***")
                else:
                    print(f"  {line.strip()}")
    else:
        print("\n❌ .env file not found")
    
    if all_present:
        print("\n🎉 All required secrets are accessible!")
        return True
    else:
        print("\n❌ Some secrets are missing. Please check your GitHub repository secrets.")
        return False

def test_python_modules():
    """Test that required Python modules are available"""
    print("\n🐍 Testing Python Modules")
    print("=" * 50)
    
    required_modules = [
        'selenium',
        'requests', 
        'beautifulsoup4',
        'python-dotenv',
        'webdriver_manager',
        'schedule',
        'lxml'
    ]
    
    all_present = True
    
    for module in required_modules:
        try:
            # Handle module name differences
            if module == 'python-dotenv':
                import_name = 'dotenv'
            elif module == 'beautifulsoup4':
                import_name = 'bs4'
            else:
                import_name = module.replace('-', '_')
            
            __import__(import_name)
            print(f"✅ {module}: OK")
        except ImportError as e:
            print(f"❌ {module}: MISSING - {e}")
            all_present = False
    
    if all_present:
        print("\n🎉 All required Python modules are available!")
        return True
    else:
        print("\n❌ Some Python modules are missing.")
        return False

if __name__ == "__main__":
    secrets_ok = test_secrets()
    modules_ok = test_python_modules()
    
    if secrets_ok and modules_ok:
        print("\n🎉 All tests passed! Your setup should work correctly.")
        exit(0)
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
        exit(1)
