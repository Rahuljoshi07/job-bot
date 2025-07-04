#!/usr/bin/env python3
"""
Simple CloudFlare Bypass Script
Specifically designed to handle Glassdoor and WeWorkRemotely
"""

import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from browser_manager import BrowserManager

class SimpleCloudFlareBypass:
    def __init__(self):
        self.browser_manager = BrowserManager()
        self.driver = None
        
    def setup_stealth_browser(self):
        """Setup browser with maximum stealth"""
        print("🔧 Setting up stealth browser...")
        
        if self.browser_manager.setup_browser(headless=False):
            self.driver = self.browser_manager.driver
            
            # Apply stealth measures
            stealth_script = """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            window.chrome = {
                runtime: {},
            };
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            """
            
            try:
                self.driver.execute_script(stealth_script)
                print("✅ Stealth measures applied")
            except:
                print("⚠️ Some stealth measures skipped")
            
            return True
        return False
    
    def wait_for_cloudflare_bypass(self, max_wait=45):
        """Wait for CloudFlare to automatically pass"""
        print("⏳ Waiting for CloudFlare to complete verification...")
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                # Check if CloudFlare indicators are gone
                page_source = self.driver.page_source.lower()
                title = self.driver.title.lower()
                
                cf_indicators = [
                    "checking your browser",
                    "just a moment",
                    "please wait",
                    "cloudflare"
                ]
                
                # If no CloudFlare indicators found, we're through
                if not any(indicator in page_source for indicator in cf_indicators):
                    if not any(indicator in title for indicator in cf_indicators):
                        print("✅ CloudFlare verification completed!")
                        return True
                
                # Wait and check again
                time.sleep(2)
                
            except Exception as e:
                print(f"⚠️ Error checking CloudFlare status: {e}")
                time.sleep(2)
        
        print("❌ CloudFlare verification timeout")
        return False
    
    def access_protected_site(self, url, site_name="Site"):
        """Access a CloudFlare protected site"""
        print(f"🌐 Accessing {site_name}: {url}")
        
        if not self.driver:
            if not self.setup_stealth_browser():
                return False, "Browser setup failed"
        
        try:
            # Navigate to the site
            self.driver.get(url)
            print(f"📡 Navigated to {url}")
            
            # Wait a moment for initial load
            time.sleep(5)
            
            # Check if CloudFlare protection is present
            page_source = self.driver.page_source.lower()
            
            if any(indicator in page_source for indicator in ["cloudflare", "checking your browser", "just a moment"]):
                print("🚨 CloudFlare protection detected, waiting for bypass...")
                if self.wait_for_cloudflare_bypass():
                    print(f"✅ Successfully bypassed CloudFlare for {site_name}")
                else:
                    print(f"❌ Failed to bypass CloudFlare for {site_name}")
                    return False, "CloudFlare bypass failed"
            else:
                print(f"✅ No CloudFlare protection detected for {site_name}")
            
            # Final verification - check if we can access the site
            time.sleep(3)
            title = self.driver.title
            current_url = self.driver.current_url
            
            # Take screenshot as proof
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_name = f"{site_name.lower()}_access_proof_{timestamp}.png"
            
            try:
                self.driver.save_screenshot(screenshot_name)
                print(f"📸 Screenshot saved: {screenshot_name}")
            except:
                print("⚠️ Could not save screenshot")
                screenshot_name = "screenshot_failed"
            
            return True, f"Successfully accessed {site_name} - Title: {title}, Proof: {screenshot_name}"
            
        except Exception as e:
            return False, f"Error accessing {site_name}: {e}"
    
    def test_glassdoor(self):
        """Test Glassdoor access"""
        return self.access_protected_site("https://www.glassdoor.com", "Glassdoor")
    
    def test_weworkremotely(self):
        """Test WeWorkRemotely access"""
        return self.access_protected_site("https://weworkremotely.com", "WeWorkRemotely")
    
    def run_bypass_test(self):
        """Run bypass test on both problem sites"""
        print("🚀 SIMPLE CLOUDFLARE BYPASS TEST")
        print("=" * 60)
        
        results = {}
        
        # Test Glassdoor
        print("\\n🔍 Testing Glassdoor...")
        success, message = self.test_glassdoor()
        results['Glassdoor'] = {'success': success, 'message': message}
        print(f"{'✅' if success else '❌'} Glassdoor: {message}")
        
        # Wait between tests
        time.sleep(5)
        
        # Test WeWorkRemotely
        print("\\n🔍 Testing WeWorkRemotely...")
        success, message = self.test_weworkremotely()
        results['WeWorkRemotely'] = {'success': success, 'message': message}
        print(f"{'✅' if success else '❌'} WeWorkRemotely: {message}")
        
        # Summary
        print("\\n" + "=" * 60)
        print("📊 BYPASS TEST RESULTS")
        print("=" * 60)
        
        working_sites = len([r for r in results.values() if r['success']])
        total_sites = len(results)
        
        print(f"Working sites: {working_sites}/{total_sites}")
        print(f"Success rate: {(working_sites/total_sites)*100:.1f}%")
        
        for site, result in results.items():
            status = "✅ WORKING" if result['success'] else "❌ FAILED"
            print(f"{status}: {site}")
            print(f"   └─ {result['message']}")
        
        # Cleanup
        if self.driver:
            self.browser_manager.quit()
        
        return results

if __name__ == "__main__":
    bypass = SimpleCloudFlareBypass()
    results = bypass.run_bypass_test()
