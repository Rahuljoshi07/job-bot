#!/usr/bin/env python3
"""
Test Firefox ESR setup in CI environment
Specifically tests for Marionette port connection issues
"""

import os
import sys
import subprocess
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

def test_firefox_esr():
    """Test Firefox ESR setup and Marionette connection"""
    print("🧪 Testing Firefox ESR setup...")
    
    # Check if running in CI
    is_ci = os.environ.get('GITHUB_ACTIONS', False)
    print(f"📍 Running in CI: {is_ci}")
    
    # Check Firefox installation
    try:
        if is_ci:
            result = subprocess.run(['firefox-esr', '--version'], capture_output=True, text=True)
            print(f"🦊 Firefox ESR version: {result.stdout.strip()}")
        else:
            print("🦊 Firefox ESR check skipped (not in CI)")
    except Exception as e:
        print(f"⚠️ Firefox ESR version check failed: {e}")
    
    # Check geckodriver
    try:
        result = subprocess.run(['geckodriver', '--version'], capture_output=True, text=True)
        output_lines = result.stdout.strip().split('\n')
        print(f"🔧 Geckodriver version: {output_lines[0]}")
    except Exception as e:
        print(f"⚠️ Geckodriver version check failed: {e}")
    
    # Test Selenium with Firefox ESR
    driver = None
    try:
        print("🔧 Setting up Firefox ESR with Selenium...")
        
        options = FirefoxOptions()
        options.add_argument("--headless")
        
        # Enhanced options for CI compatibility
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--window-size=1920,1080")
        
        # CI-specific settings
        if is_ci:
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-features=TranslateUI")
            options.add_argument("--disable-ipc-flooding-protection")
            options.binary_location = "/usr/bin/firefox-esr"
        
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        
        print("✅ Firefox ESR driver created successfully")
        
        # Test navigation
        print("🌐 Testing navigation...")
        driver.get("https://www.google.com")
        title = driver.title
        print(f"✅ Navigation successful - Page title: {title}")
        
        # Test Marionette connection (implicit - if we get here, Marionette is working)
        print("🔗 Testing Marionette connection...")
        driver.execute_script("return document.readyState;")
        print("✅ Marionette connection successful")
        
        # Take screenshot as proof
        driver.save_screenshot("firefox_esr_test.png")
        print("📸 Test screenshot saved")
        
        return True
        
    except Exception as e:
        print(f"❌ Firefox ESR test failed: {e}")
        return False
    
    finally:
        if driver:
            try:
                driver.quit()
                print("✅ Firefox ESR driver closed")
            except Exception as e:
                print(f"⚠️ Error closing driver: {e}")

def main():
    """Run the Firefox ESR test"""
    print("🤖 FIREFOX ESR MARIONETTE PORT TEST")
    print("=" * 50)
    
    success = test_firefox_esr()
    
    if success:
        print("✅ All tests passed - Firefox ESR setup is working correctly!")
        sys.exit(0)
    else:
        print("❌ Tests failed - Firefox ESR setup needs attention")
        sys.exit(1)

if __name__ == "__main__":
    main()
