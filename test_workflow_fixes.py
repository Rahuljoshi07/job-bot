#!/usr/bin/env python3
"""
Test script to identify and fix workflow issues
"""

import os
import sys
import json
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """Test all required imports"""
    logger.info("🧪 Testing imports...")
    
    try:
        import requests
        logger.info("✅ requests imported successfully")
    except ImportError as e:
        logger.error(f"❌ requests import failed: {e}")
        return False
    
    try:
        from selenium import webdriver
        logger.info("✅ selenium imported successfully")
    except ImportError as e:
        logger.error(f"❌ selenium import failed: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        logger.info("✅ BeautifulSoup imported successfully")
    except ImportError as e:
        logger.error(f"❌ BeautifulSoup import failed: {e}")
        return False
    
    # Optional imports
    try:
        import nltk
        logger.info("✅ NLTK available")
    except ImportError:
        logger.warning("⚠️ NLTK not available (optional)")
    
    try:
        import spacy
        logger.info("✅ spaCy available")
    except ImportError:
        logger.warning("⚠️ spaCy not available (optional)")
    
    return True

def test_environment():
    """Test environment configuration"""
    logger.info("🧪 Testing environment...")
    
    # Check if we're in GitHub Actions
    if os.getenv('GITHUB_ACTIONS') == 'true':
        logger.info("✅ Running in GitHub Actions")
    else:
        logger.info("✅ Running locally")
    
    # Test environment variables
    required_vars = [
        'PERSONAL_EMAIL', 'PERSONAL_FULL_NAME'
    ]
    
    for var in required_vars:
        if os.getenv(var):
            logger.info(f"✅ {var} is set")
        else:
            logger.warning(f"⚠️ {var} is not set")
    
    return True

def test_browser_setup():
    """Test browser setup"""
    logger.info("🧪 Testing browser setup...")
    
    try:
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.firefox.service import Service
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        logger.info("✅ Firefox options configured")
        
        # Try to find geckodriver
        import shutil
        geckodriver_path = shutil.which('geckodriver')
        if geckodriver_path:
            logger.info(f"✅ geckodriver found at {geckodriver_path}")
        else:
            logger.warning("⚠️ geckodriver not found in PATH")
            
            # Try webdriver-manager
            try:
                from webdriver_manager.firefox import GeckoDriverManager
                driver_path = GeckoDriverManager().install()
                logger.info(f"✅ geckodriver installed via webdriver-manager at {driver_path}")
            except Exception as e:
                logger.error(f"❌ Could not install geckodriver: {e}")
                return False
        
        # Test actual browser creation (but don't keep it running)
        try:
            if geckodriver_path:
                service = Service(geckodriver_path)
            else:
                from webdriver_manager.firefox import GeckoDriverManager
                service = Service(GeckoDriverManager().install())
            
            from selenium import webdriver
            driver = webdriver.Firefox(service=service, options=options)
            driver.quit()
            logger.info("✅ Browser test successful")
            
        except Exception as e:
            logger.error(f"❌ Browser test failed: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Browser setup test failed: {e}")
        return False
    
    return True

def test_api_connections():
    """Test API connections"""
    logger.info("🧪 Testing API connections...")
    
    try:
        # Test RemoteOK API
        response = requests.get("https://remoteok.io/api", timeout=10)
        if response.status_code == 200:
            logger.info("✅ RemoteOK API accessible")
        else:
            logger.warning(f"⚠️ RemoteOK API returned status {response.status_code}")
    except Exception as e:
        logger.error(f"❌ RemoteOK API test failed: {e}")
    
    return True

def test_file_structure():
    """Test required file structure"""
    logger.info("🧪 Testing file structure...")
    
    current_dir = Path('.')
    
    required_files = [
        'requirements.txt',
        'enhanced_ultimate_job_bot.py',
        '.github/workflows/job-bot-automation.yml'
    ]
    
    for file_path in required_files:
        if (current_dir / file_path).exists():
            logger.info(f"✅ {file_path} exists")
        else:
            logger.error(f"❌ {file_path} missing")
            return False
    
    # Create necessary directories
    directories = ['application_proofs', 'logs']
    for directory in directories:
        dir_path = current_dir / directory
        dir_path.mkdir(exist_ok=True)
        logger.info(f"✅ {directory} directory ready")
    
    return True

def create_default_config():
    """Create default configuration if needed"""
    logger.info("🧪 Creating default configuration...")
    
    config = {
        'personal': {
            'full_name': os.getenv('PERSONAL_FULL_NAME', 'Rahul Joshi'),
            'email': os.getenv('PERSONAL_EMAIL', 'rahuljoshisg@gmail.com'),
            'phone': os.getenv('PERSONAL_PHONE', '+91 9456382923'),
            'linkedin': os.getenv('PERSONAL_LINKEDIN', 'https://linkedin.com/in/rahul-joshi'),
            'github': os.getenv('PERSONAL_GITHUB', 'https://github.com/Rahuljoshi07'),
            'location': os.getenv('PERSONAL_LOCATION', 'Remote Worldwide')
        },
        'platforms': {
            'twitter': {
                'email': os.getenv('TWITTER_EMAIL', ''),
                'password': os.getenv('TWITTER_PASSWORD', '')
            },
            'turing': {
                'email': os.getenv('TURING_EMAIL', ''),
                'password': os.getenv('TURING_PASSWORD', '')
            },
            'indeed': {
                'email': os.getenv('INDEED_EMAIL', ''),
                'password': os.getenv('INDEED_PASSWORD', '')
            },
            'dice': {
                'email': os.getenv('DICE_EMAIL', ''),
                'password': os.getenv('DICE_PASSWORD', '')
            }
        },
        'preferences': {
            'job_titles': [
                "DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer",
                "Infrastructure Engineer", "Platform Engineer", "AWS Engineer"
            ],
            'skills': ["DevOps", "AWS", "Docker", "Kubernetes", "Python", "Linux", "CI/CD"],
            'remote_only': True,
            'experience_level': 'entry'
        }
    }
    
    with open('user_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info("✅ Default configuration created")
    return True

def main():
    """Run all tests"""
    logger.info("🚀 Starting workflow diagnostics...")
    
    tests = [
        ("Imports", test_imports),
        ("Environment", test_environment),
        ("File Structure", test_file_structure),
        ("Default Config", create_default_config),
        ("Browser Setup", test_browser_setup),
        ("API Connections", test_api_connections)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {test_name} test...")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results[test_name] = result
            if result:
                logger.info(f"✅ {test_name} test PASSED")
            else:
                logger.error(f"❌ {test_name} test FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} test CRASHED: {e}")
            results[test_name] = False
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("📊 TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Workflow should work correctly.")
        return True
    else:
        logger.error("❌ Some tests failed. Please fix the issues before running the workflow.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
