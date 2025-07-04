#!/usr/bin/env python3
"""
Test script to verify job bot functionality
"""

import os
import sys
from config import Config
from resume_analyzer import ResumeAnalyzer

def test_config():
    """Test configuration loading"""
    try:
        config = Config()
        print("✅ Config class initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_resume_analyzer():
    """Test resume analyzer"""
    try:
        analyzer = ResumeAnalyzer()
        print("✅ Resume analyzer initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Resume analyzer test failed: {e}")
        return False

def test_files():
    """Test required files exist"""
    required_files = [
        'requirements.txt',
        'config.py', 
        'resume_analyzer.py',
        'super_ultimate_bot.py',
        'cover_letter.txt',
        '.github/workflows/job-bot-automation.yml'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_environment():
    """Test environment setup"""
    github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
    
    if github_actions:
        print("✅ Running in GitHub Actions environment")
        # Check for required secrets
        required_vars = ['PERSONAL_FULL_NAME', 'PERSONAL_EMAIL', 'TWITTER_EMAIL']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"⚠️  Missing environment variables: {missing_vars}")
            print("Make sure to set these as GitHub Secrets")
        else:
            print("✅ Required environment variables found")
    else:
        print("✅ Running in local environment")
        if os.path.exists('.env'):
            print("✅ .env file found")
        else:
            print("⚠️  No .env file found (create one based on .env.example)")
    
    return True

def main():
    """Run all tests"""
    print("🧪 Testing Job Bot Configuration...")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config),
        ("Resume Analyzer", test_resume_analyzer), 
        ("Required Files", test_files),
        ("Environment", test_environment)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bot is ready to run.")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
