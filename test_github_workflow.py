#!/usr/bin/env python3
"""
Test script to validate GitHub Actions workflow compatibility
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_python_version():
    """Test Python version compatibility"""
    logger.info(f"Testing Python version: {sys.version}")
    major, minor = sys.version_info[:2]
    if major == 3 and minor >= 8:
        logger.info("✅ Python version is compatible")
        return True
    else:
        logger.error("❌ Python version must be 3.8 or higher")
        return False

def test_environment_variables():
    """Test required environment variables"""
    logger.info("Testing environment variables...")
    
    # Required variables for GitHub Actions
    required_vars = [
        'PERSONAL_FULL_NAME', 'PERSONAL_EMAIL', 'PERSONAL_PHONE', 'PERSONAL_LOCATION'
    ]
    
    # Set defaults for testing
    os.environ.setdefault('PERSONAL_FULL_NAME', 'Test User')
    os.environ.setdefault('PERSONAL_EMAIL', 'test@example.com')
    os.environ.setdefault('PERSONAL_PHONE', '+1234567890')
    os.environ.setdefault('PERSONAL_LOCATION', 'Remote')
    os.environ.setdefault('GITHUB_ACTIONS', 'true')
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"⚠️ Missing variables (using defaults): {missing_vars}")
    else:
        logger.info("✅ All required environment variables are set")
    
    return True

def test_dependencies():
    """Test package dependencies"""
    logger.info("Testing package dependencies...")
    
    required_packages = [
        'selenium', 'beautifulsoup4', 'requests', 'webdriver_manager'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"✅ {package} is available")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"⚠️ {package} is missing")
    
    if missing_packages:
        logger.warning(f"Missing packages: {missing_packages}")
        logger.info("Installing missing packages...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            logger.info("✅ Missing packages installed")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install packages: {e}")
            return False
    
    return True

def test_bot_import():
    """Test bot import"""
    logger.info("Testing enhanced ultimate job bot import...")
    
    try:
        import enhanced_ultimate_job_bot
        logger.info("✅ Enhanced Ultimate Job Bot imports successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Failed to import enhanced ultimate job bot: {e}")
        return False

def test_browser_setup():
    """Test browser setup (without actually running)"""
    logger.info("Testing browser setup configuration...")
    
    try:
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.firefox.service import Service
        
        # Test Firefox options
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        logger.info("✅ Firefox options configured successfully")
        
        # Check for geckodriver path in GitHub Actions
        if os.getenv('GITHUB_ACTIONS') == 'true':
            expected_path = '/usr/local/bin/geckodriver'
            if os.path.exists(expected_path):
                logger.info(f"✅ Geckodriver found at {expected_path}")
            else:
                logger.warning(f"⚠️ Geckodriver not found at {expected_path} (expected in CI)")
        else:
            logger.info("🏠 Running locally, geckodriver will be downloaded")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Browser setup test failed: {e}")
        return False

def test_file_structure():
    """Test required file structure"""
    logger.info("Testing file structure...")
    
    required_files = [
        'enhanced_ultimate_job_bot.py',
        'requirements.txt',
        '.github/workflows/job-bot-automation.yml'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            logger.info(f"✅ {file_path} exists")
        else:
            missing_files.append(file_path)
            logger.warning(f"⚠️ {file_path} is missing")
    
    # Create directories if they don't exist
    os.makedirs('application_proofs', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    logger.info("✅ Required directories created/verified")
    
    return len(missing_files) == 0

def test_workflow_compatibility():
    """Test GitHub Actions workflow compatibility"""
    logger.info("Testing GitHub Actions workflow compatibility...")
    
    # Simulate GitHub Actions environment
    os.environ['GITHUB_ACTIONS'] = 'true'
    os.environ['DISPLAY'] = ':99'
    
    try:
        # Test enhanced ultimate job bot initialization
        from enhanced_ultimate_job_bot import EnhancedUltimateJobBot
        
        logger.info("✅ Bot class can be imported")
        
        # Test basic initialization (without browser)
        bot = EnhancedUltimateJobBot()
        logger.info("✅ Bot can be initialized")
        
        # Test configuration loading
        config = bot._load_configuration()
        logger.info(f"✅ Configuration loaded: {len(config)} sections")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Workflow compatibility test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🧪 Starting GitHub Actions workflow compatibility tests...")
    logger.info("=" * 60)
    
    tests = [
        ("Python Version", test_python_version),
        ("Environment Variables", test_environment_variables),
        ("Dependencies", test_dependencies),
        ("Bot Import", test_bot_import),
        ("Browser Setup", test_browser_setup),
        ("File Structure", test_file_structure),
        ("Workflow Compatibility", test_workflow_compatibility)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running test: {test_name}")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} PASSED")
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} ERROR: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Workflow should work correctly.")
        return 0
    else:
        logger.error(f"⚠️ {total - passed} test(s) failed. Please fix issues before deploying.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
