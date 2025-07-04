#!/usr/bin/env python3
"""
Test Real Credentials for LinkedIn and Indeed
"""

import time
from browser_manager import BrowserManager
from captcha_solver import AdvancedCaptchaSolver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from config import Config
from datetime import datetime

class RealCredentialTester:
    def __init__(self):
        self.config = Config()
        self.user_config = self.config.load_config()
        self.browser_manager = BrowserManager()
        
    def test_linkedin_login(self):
        """Test LinkedIn login with real credentials"""
        print("🔍 Testing LinkedIn Login...")
        
        # Get credentials
        linkedin_email = self.user_config['platforms']['linkedin']['email']
        linkedin_password = self.user_config['platforms']['linkedin']['password']
        
        print(f"📧 Using email: {linkedin_email}")
        
        if not self.browser_manager.setup_browser(headless=False):
            return False, "Browser setup failed"
        
        driver = self.browser_manager.driver
        
        try:
            # Navigate to LinkedIn login
            driver.get("https://www.linkedin.com/login")
            time.sleep(3)
            
            # Find and fill email
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.clear()
            email_field.send_keys(linkedin_email)
            
            # Find and fill password
            password_field = driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(linkedin_password)
            
            # Take screenshot before login
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            driver.save_screenshot(f"linkedin_before_login_{timestamp}.png")
            
            # Click login button
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for redirect
            time.sleep(5)
            
            # Check if login was successful
            current_url = driver.current_url
            title = driver.title
            
            # Take screenshot after login attempt
            driver.save_screenshot(f"linkedin_after_login_{timestamp}.png")
            
            if "feed" in current_url or "linkedin.com/in/" in current_url or "challenge" in current_url:
                return True, f"Login successful - URL: {current_url}, Screenshots saved"
            else:
                return False, f"Login may have failed - URL: {current_url}, Title: {title}"
                
        except Exception as e:
            return False, f"Error during LinkedIn login: {e}"
        finally:
            # Keep browser open for manual verification
            input("Press Enter to close browser and continue...")
            self.browser_manager.quit()
    
    def test_indeed_login(self):
        """Test Indeed login with real credentials"""
        print("🔍 Testing Indeed Login...")
        
        # Get credentials
        indeed_email = self.user_config['platforms']['indeed']['email']
        indeed_password = self.user_config['platforms']['indeed']['password']
        
        print(f"📧 Using email: {indeed_email}")
        
        if not self.browser_manager.setup_browser(headless=False):
            return False, "Browser setup failed"
        
        driver = self.browser_manager.driver
        
        try:
            # Navigate to Indeed
            driver.get("https://secure.indeed.com/account/login")
            time.sleep(3)
            
            # Find and fill email
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "login-email-input"))
            )
            email_field.clear()
            email_field.send_keys(indeed_email)
            
            # Find and fill password
            password_field = driver.find_element(By.ID, "login-password-input")
            password_field.clear()
            password_field.send_keys(indeed_password)
            
            # Take screenshot before login
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            driver.save_screenshot(f"indeed_before_login_{timestamp}.png")
            
            # Click login button
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for redirect
            time.sleep(5)
            
            # Check if login was successful
            current_url = driver.current_url
            title = driver.title
            
            # Take screenshot after login attempt
            driver.save_screenshot(f"indeed_after_login_{timestamp}.png")
            
            if "indeed.com" in current_url and "login" not in current_url:
                return True, f"Login successful - URL: {current_url}, Screenshots saved"
            else:
                return False, f"Login may have failed - URL: {current_url}, Title: {title}"
                
        except Exception as e:
            return False, f"Error during Indeed login: {e}"
        finally:
            # Keep browser open for manual verification
            input("Press Enter to close browser and continue...")
            self.browser_manager.quit()
    
    def run_credential_tests(self):
        """Run tests for both platforms"""
        print("🚀 TESTING REAL CREDENTIALS")
        print("=" * 60)
        print(f"Started at: {datetime.now()}")
        print("=" * 60)
        
        results = {}
        
        # Test LinkedIn
        print("\n1️⃣ Testing LinkedIn...")
        success, message = self.test_linkedin_login()
        results['LinkedIn'] = {'success': success, 'message': message}
        print(f"{'✅' if success else '❌'} LinkedIn: {message}")
        
        # Wait between tests
        time.sleep(3)
        
        # Test Indeed
        print("\n2️⃣ Testing Indeed...")
        success, message = self.test_indeed_login()
        results['Indeed'] = {'success': success, 'message': message}
        print(f"{'✅' if success else '❌'} Indeed: {message}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 CREDENTIAL TEST RESULTS")
        print("=" * 60)
        
        working_platforms = len([r for r in results.values() if r['success']])
        total_platforms = len(results)
        
        print(f"Working platforms: {working_platforms}/{total_platforms}")
        print(f"Success rate: {(working_platforms/total_platforms)*100:.1f}%")
        
        for platform, result in results.items():
            status = "✅ WORKING" if result['success'] else "❌ FAILED"
            print(f"{status}: {platform}")
            print(f"   └─ {result['message']}")
        
        return results

if __name__ == "__main__":
    tester = RealCredentialTester()
    results = tester.run_credential_tests()
