#!/usr/bin/env python3
"""
Robust Browser Manager - Edge First, Firefox Backup, NO CHROME
Completely eliminates Chrome dependency issues
"""

import os
import sys
import platform
import subprocess
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

class BrowserManager:
    def __init__(self):
        self.driver = None
        self.browser_type = None
        
    def detect_browsers(self):
        """Detect available browsers on Windows - Edge First, Firefox Backup"""
        browsers = {}
        
        # Check for Edge FIRST (most reliable on Windows)
        edge_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        ]
        
        for path in edge_paths:
            if os.path.exists(path):
                browsers['edge'] = path
                break
        
        # Check for Firefox as backup
        firefox_paths = [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
        ]
        
        for path in firefox_paths:
            if os.path.exists(path):
                browsers['firefox'] = path
                break
                
        return browsers
    
    
    def setup_firefox(self, headless=True):
        """Setup Firefox browser (supports both regular Firefox and Firefox ESR)"""
        try:
            print("🔧 Setting up Firefox browser...")
            
            options = FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            
            # Enhanced Firefox options for better CI compatibility
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            options.add_argument("--window-size=1920,1080")
            
            # CI-specific settings for better stability
            if os.environ.get('GITHUB_ACTIONS'):
                options.add_argument("--disable-background-timer-throttling")
                options.add_argument("--disable-backgrounding-occluded-windows")
                options.add_argument("--disable-renderer-backgrounding")
                options.add_argument("--disable-features=TranslateUI")
                options.add_argument("--disable-ipc-flooding-protection")
                # For Firefox ESR in CI
                options.binary_location = "/usr/bin/firefox-esr"
            
            service = FirefoxService(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=options)
            self.browser_type = "firefox"
            print("✅ Firefox browser setup successful")
            return True
            
        except Exception as e:
            print(f"❌ Firefox setup failed: {e}")
            return False
    
    def setup_edge(self, headless=True):
        """Setup Edge browser with anti-detection"""
        try:
            print("🔧 Setting up Edge browser with anti-detection...")
            
            options = EdgeOptions()
            if headless:
                options.add_argument("--headless")
            
            # Anti-detection arguments
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")
            options.add_argument("--disable-javascript")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0")
            
            service = EdgeService(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(service=service, options=options)
            
            # Execute stealth script immediately after browser starts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.browser_type = "edge"
            print("✅ Edge browser setup successful with anti-detection")
            return True
            
        except Exception as e:
            print(f"❌ Edge setup failed: {e}")
            return False
    
    def setup_browser(self, headless=True, preferred_browser=None):
        """Setup browser with fallback options"""
        print("🔍 Detecting available browsers...")
        available_browsers = self.detect_browsers()
        
        if not available_browsers:
            print("❌ No browsers detected. Please install Edge or Firefox.")
            return False
        
        print(f"✅ Available browsers: {list(available_browsers.keys())}")
        
        # Try preferred browser first
        if preferred_browser and preferred_browser in available_browsers:
            if preferred_browser == "firefox" and self.setup_firefox(headless):
                return True
            elif preferred_browser == "edge" and self.setup_edge(headless):
                return True
        
        # Try browsers in order of preference - EDGE FIRST!
        browser_order = ["edge", "firefox"]
        
        for browser in browser_order:
            if browser in available_browsers:
                try:
                    if browser == "edge" and self.setup_edge(headless):
                        return True
                    elif browser == "firefox" and self.setup_firefox(headless):
                        return True
                except Exception as e:
                    print(f"⚠️ Failed to setup {browser}: {e}")
                    continue
        
        print("❌ All browser setup attempts failed")
        return False
    
    def test_browser(self):
        """Test browser functionality"""
        if not self.driver:
            return False
        
        try:
            print(f"🧪 Testing {self.browser_type} browser...")
            self.driver.get("https://www.google.com")
            title = self.driver.title
            print(f"✅ Browser test successful - Page title: {title}")
            return True
        except Exception as e:
            print(f"❌ Browser test failed: {e}")
            return False
    
    def take_screenshot(self, filename):
        """Take screenshot"""
        try:
            if self.driver:
                self.driver.save_screenshot(filename)
                print(f"📸 Screenshot saved: {filename}")
                return True
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
        return False
    
    def quit(self):
        """Close browser"""
        if self.driver:
            try:
                self.driver.quit()
                print(f"✅ {self.browser_type} browser closed")
            except Exception as e:
                print(f"⚠️ Error closing browser: {e}")

def test_browser_manager():
    """Test the browser manager"""
    print("🤖 TESTING BROWSER MANAGER")
    print("=" * 50)
    
    manager = BrowserManager()
    
    # Test browser setup
    if manager.setup_browser(headless=True):
        print("✅ Browser setup successful")
        
        # Test browser functionality
        if manager.test_browser():
            print("✅ Browser test successful")
            
            # Test screenshot
            if manager.take_screenshot("test_screenshot.png"):
                print("✅ Screenshot test successful")
            
        manager.quit()
        return True
    else:
        print("❌ Browser setup failed")
        return False

if __name__ == "__main__":
    success = test_browser_manager()
    sys.exit(0 if success else 1)
