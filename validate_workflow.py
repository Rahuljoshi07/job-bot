#!/usr/bin/env python3
"""
Simple validation script that mimics GitHub Actions execution
"""

import os
import sys
import subprocess
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def simulate_github_actions_environment():
    """Simulate GitHub Actions environment variables"""
    logger.info("🔧 Setting up GitHub Actions simulation...")
    
    # Set required environment variables
    os.environ['GITHUB_ACTIONS'] = 'true'
    os.environ['DISPLAY'] = ':99'
    
    # Set personal info (defaults for testing)
    os.environ.setdefault('PERSONAL_FULL_NAME', 'Rahul Joshi')
    os.environ.setdefault('PERSONAL_EMAIL', 'rahuljoshisg@gmail.com')
    os.environ.setdefault('PERSONAL_PHONE', '+91 9456382923')
    os.environ.setdefault('PERSONAL_LOCATION', 'Remote Worldwide')
    os.environ.setdefault('PERSONAL_LINKEDIN', 'https://linkedin.com/in/rahul')
    os.environ.setdefault('PERSONAL_GITHUB', 'https://github.com/Rahuljoshi07')
    
    # Set platform credentials (empty for testing)
    os.environ.setdefault('TWITTER_EMAIL', 'test@example.com')
    os.environ.setdefault('TWITTER_PASSWORD', 'test_password')
    os.environ.setdefault('INDEED_EMAIL', 'test@example.com')
    os.environ.setdefault('INDEED_PASSWORD', 'test_password')
    os.environ.setdefault('DICE_EMAIL', 'test@example.com')
    os.environ.setdefault('DICE_PASSWORD', 'test_password')
    
    logger.info("✅ GitHub Actions environment simulated")

def validate_bot_execution():
    """Validate that the bot can be executed successfully"""
    logger.info("🤖 Testing bot execution...")
    
    try:
        # Import the bot to check for import errors
        from enhanced_ultimate_job_bot import EnhancedUltimateJobBot
        logger.info("✅ Bot imports successfully")
        
        # Initialize the bot
        bot = EnhancedUltimateJobBot()
        logger.info("✅ Bot initializes successfully")
        
        # Test configuration loading
        config = bot._load_configuration()
        if config:
            logger.info(f"✅ Configuration loaded: {len(config)} sections")
        else:
            logger.warning("⚠️ Configuration is empty but bot continues")
        
        # Test user profile creation
        profile = bot._create_user_profile()
        if profile.name:
            logger.info(f"✅ User profile created: {profile.name}")
        else:
            logger.warning("⚠️ User profile has no name but continues")
        
        logger.info("✅ Bot execution validation completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Bot execution validation failed: {e}")
        return False

def validate_dependencies():
    """Validate all required dependencies are available"""
    logger.info("📦 Validating dependencies...")
    
    critical_imports = [
        'selenium',
        'requests', 
        'json',
        'time',
        'os',
        'logging'
    ]
    
    optional_imports = [
        'beautifulsoup4',
        'schedule',
        'webdriver_manager'
    ]
    
    for package in critical_imports:
        try:
            if package == 'beautifulsoup4':
                import bs4
            else:
                __import__(package.replace('-', '_'))
            logger.info(f"✅ {package} available")
        except ImportError:
            logger.error(f"❌ Critical dependency missing: {package}")
            return False
    
    for package in optional_imports:
        try:
            if package == 'beautifulsoup4':
                import bs4
            else:
                __import__(package.replace('-', '_'))
            logger.info(f"✅ {package} available")
        except ImportError:
            logger.warning(f"⚠️ Optional dependency missing: {package}")
    
    logger.info("✅ Dependency validation completed")
    return True

def validate_file_structure():
    """Validate required files exist"""
    logger.info("📁 Validating file structure...")
    
    required_files = [
        'enhanced_ultimate_job_bot.py',
        'requirements.txt'
    ]
    
    optional_files = [
        'resume.pdf',
        '.env'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            logger.info(f"✅ {file_path} exists")
        else:
            logger.error(f"❌ Required file missing: {file_path}")
            return False
    
    for file_path in optional_files:
        if os.path.exists(file_path):
            logger.info(f"✅ {file_path} exists")
        else:
            logger.warning(f"⚠️ Optional file missing: {file_path}")
    
    # Create required directories
    os.makedirs('application_proofs', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    logger.info("✅ Required directories ensured")
    
    return True

def main():
    """Main validation function"""
    logger.info("🎯 Starting workflow validation...")
    logger.info("=" * 60)
    
    # Set up environment
    simulate_github_actions_environment()
    
    # Run validations
    validations = [
        ("File Structure", validate_file_structure),
        ("Dependencies", validate_dependencies),
        ("Bot Execution", validate_bot_execution)
    ]
    
    passed = 0
    total = len(validations)
    
    for validation_name, validation_func in validations:
        logger.info(f"\n🧪 Running validation: {validation_name}")
        try:
            if validation_func():
                passed += 1
                logger.info(f"✅ {validation_name} PASSED")
            else:
                logger.error(f"❌ {validation_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {validation_name} ERROR: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"📊 Validation Results: {passed}/{total} validations passed")
    
    if passed == total:
        logger.info("🎉 All validations passed! Workflow is ready for GitHub Actions.")
        logger.info("🚀 You can now safely trigger the workflow manually or wait for scheduled runs.")
        return 0
    else:
        logger.error(f"⚠️ {total - passed} validation(s) failed. Please fix issues before deploying.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
