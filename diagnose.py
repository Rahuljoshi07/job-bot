#!/usr/bin/env python3
"""
Diagnostic script to identify GitHub Actions issues
"""

import os
import sys
import subprocess
import traceback

def check_python_environment():
    """Check Python environment"""
    print("🐍 Python Environment Check:")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    print(f"GitHub Actions: {os.environ.get('GITHUB_ACTIONS', 'Not set')}")

def check_firefox_geckodriver():
    """Check Firefox and geckodriver installation"""
    print("\n🔥 Firefox & Geckodriver Check:")
    
    # Check Firefox
    try:
        result = subprocess.run(['firefox', '--version'], capture_output=True, text=True, timeout=10)
        print(f"Firefox: {result.stdout.strip()}")
    except Exception as e:
        print(f"Firefox check failed: {e}")
    
    # Check geckodriver
    try:
        result = subprocess.run(['geckodriver', '--version'], capture_output=True, text=True, timeout=10)
        print(f"Geckodriver: {result.stdout.strip()}")
    except Exception as e:
        print(f"Geckodriver check failed: {e}")
    
    # Check geckodriver path
    geckodriver_paths = ['/usr/local/bin/geckodriver', '/usr/bin/geckodriver']
    for path in geckodriver_paths:
        if os.path.exists(path):
            print(f"Geckodriver found at: {path}")
            try:
                result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=10)
                print(f"Version: {result.stdout.strip()}")
            except Exception as e:
                print(f"Error running {path}: {e}")
        else:
            print(f"Geckodriver NOT found at: {path}")

def check_dependencies():
    """Check Python dependencies"""
    print("\n📦 Dependencies Check:")
    
    required_packages = [
        'selenium', 'requests', 'beautifulsoup4', 
        'python-dotenv', 'webdriver_manager'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}: OK")
        except ImportError as e:
            print(f"❌ {package}: MISSING - {e}")

def check_environment_variables():
    """Check environment variables"""
    print("\n🔐 Environment Variables Check:")
    
    required_vars = [
        'PERSONAL_FULL_NAME', 'PERSONAL_EMAIL', 'PERSONAL_PHONE',
        'TWITTER_EMAIL', 'TWITTER_PASSWORD', 'TURING_EMAIL', 'TURING_PASSWORD'
    ]
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: SET (length: {len(value)})")
        else:
            print(f"❌ {var}: NOT SET")

def check_files():
    """Check required files"""
    print("\n📁 Files Check:")
    
    required_files = [
        'config.py', 'resume_analyzer.py', 'super_ultimate_bot.py',
        'cover_letter.txt', 'requirements.txt', 'resume.pdf'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file}: EXISTS ({size} bytes)")
        else:
            print(f"❌ {file}: MISSING")

def test_selenium_setup():
    """Test basic Selenium setup"""
    print("\n🤖 Selenium Setup Test:")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.firefox.service import Service
        from selenium.webdriver.firefox.options import Options
        
        print("✅ Selenium imports successful")
        
        # Test Firefox options
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        print("✅ Firefox options created")
        
        # Test service creation
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            service = Service('/usr/local/bin/geckodriver')
        else:
            from webdriver_manager.firefox import GeckoDriverManager
            service = Service(GeckoDriverManager().install())
        
        print("✅ Service created")
        
        # Test driver creation (but don't start it)
        print("🔧 Driver setup would use:", service.path)
        
    except Exception as e:
        print(f"❌ Selenium test failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")

def test_config_loading():
    """Test config loading"""
    print("\n⚙️ Config Loading Test:")
    
    try:
        from config import Config
        config = Config()
        print("✅ Config class imported and initialized")
        
        user_config = config.load_config()
        print("✅ Configuration loaded successfully")
        print(f"Personal name: {user_config.get('personal', {}).get('full_name', 'NOT SET')}")
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")

def main():
    """Run all diagnostic checks"""
    print("🔍 GitHub Actions Job Bot Diagnostics")
    print("=" * 50)
    
    try:
        check_python_environment()
        check_firefox_geckodriver()
        check_dependencies()
        check_environment_variables()
        check_files()
        test_selenium_setup()
        test_config_loading()
        
        print("\n" + "=" * 50)
        print("🎉 Diagnostics completed!")
        print("If any items show ❌, those need to be fixed for the bot to work.")
        
    except Exception as e:
        print(f"\n❌ Diagnostic error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
