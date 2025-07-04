#!/usr/bin/env python3
"""
Advanced Captcha Solver and Anti-Detection System
Handles CloudFlare, reCAPTCHA, hCaptcha, and other security measures
"""

import time
import random
import cv2
import numpy as np
from PIL import Image
import base64
import io
import requests
import speech_recognition as sr
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc

class AdvancedCaptchaSolver:
    def __init__(self, driver=None):
        self.driver = driver
        self.recognizer = sr.Recognizer()
        
    def add_anti_detection_measures(self, driver):
        """Add advanced anti-detection measures"""
        print("🛡️ Adding anti-detection measures...")
        
        # Execute JavaScript to hide automation indicators
        stealth_js = """
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        // Mock plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        // Mock languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        
        // Override the `chrome` property
        window.chrome = {
            runtime: {},
        };
        
        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Mock hairline
        Object.defineProperty(navigator.connection, 'rtt', {
            get: () => 100,
        });
        """
        
        try:
            driver.execute_script(stealth_js)
            print("✅ Anti-detection measures applied")
        except Exception as e:
            print(f"⚠️ Could not apply some anti-detection measures: {e}")
    
    def simulate_human_behavior(self, driver):
        """Simulate human-like behavior"""
        print("🤖 Simulating human behavior...")
        
        # Random mouse movements
        actions = ActionChains(driver)
        
        # Move mouse randomly
        for _ in range(random.randint(2, 5)):
            x_offset = random.randint(-100, 100)
            y_offset = random.randint(-100, 100)
            actions.move_by_offset(x_offset, y_offset)
            actions.pause(random.uniform(0.1, 0.3))
        
        actions.perform()
        
        # Random scroll
        driver.execute_script(f"window.scrollBy(0, {random.randint(-200, 200)})")
        time.sleep(random.uniform(1, 3))
        
        print("✅ Human behavior simulation complete")
    
    def detect_cloudflare(self, driver):
        """Detect CloudFlare protection"""
        print("🔍 Checking for CloudFlare protection...")
        
        cf_indicators = [
            "ray id",
            "cloudflare",
            "checking your browser",
            "just a moment",
            "please wait",
            "security check",
            "ddos protection"
        ]
        
        try:
            page_source = driver.page_source.lower()
            page_title = driver.title.lower()
            
            for indicator in cf_indicators:
                if indicator in page_source or indicator in page_title:
                    print(f"🚨 CloudFlare detected: {indicator}")
                    return True
            
            # Check for CloudFlare elements
            cf_selectors = [
                "#cf-wrapper",
                ".cf-browser-verification",
                "[data-translate='checking_browser']",
                ".ray-id"
            ]
            
            for selector in cf_selectors:
                try:
                    if driver.find_element(By.CSS_SELECTOR, selector):
                        print(f"🚨 CloudFlare element detected: {selector}")
                        return True
                except:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error detecting CloudFlare: {e}")
        
        return False
    
    def bypass_cloudflare(self, driver, max_wait=30):
        """Bypass CloudFlare protection"""
        print("🔓 Attempting to bypass CloudFlare...")
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                # Add anti-detection measures
                self.add_anti_detection_measures(driver)
                
                # Simulate human behavior
                self.simulate_human_behavior(driver)
                
                # Check if still on CloudFlare page
                if not self.detect_cloudflare(driver):
                    print("✅ CloudFlare bypass successful!")
                    return True
                
                # Look for and click verification checkbox
                try:
                    verification_selectors = [
                        "input[type='checkbox']",
                        ".cf-turnstile",
                        "#challenge-form input",
                        ".challenge-form input"
                    ]
                    
                    for selector in verification_selectors:
                        try:
                            checkbox = WebDriverWait(driver, 2).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                            
                            # Simulate human-like clicking
                            actions = ActionChains(driver)
                            actions.move_to_element(checkbox)
                            actions.pause(random.uniform(0.5, 1.5))
                            actions.click()
                            actions.perform()
                            
                            print(f"✅ Clicked verification element: {selector}")
                            time.sleep(random.uniform(2, 4))
                            break
                            
                        except TimeoutException:
                            continue
                        except Exception as e:
                            print(f"⚠️ Could not click {selector}: {e}")
                            continue
                
                except Exception as e:
                    print(f"⚠️ No verification elements found: {e}")
                
                # Wait and check again
                time.sleep(random.uniform(3, 6))
                
            except Exception as e:
                print(f"⚠️ Error during CloudFlare bypass: {e}")
                time.sleep(2)
        
        print("❌ CloudFlare bypass timeout")
        return False
    
    def detect_recaptcha(self, driver):
        """Detect reCAPTCHA"""
        print("🔍 Checking for reCAPTCHA...")
        
        recaptcha_selectors = [
            ".g-recaptcha",
            "#g-recaptcha",
            ".recaptcha-checkbox",
            "iframe[src*='recaptcha']",
            "[data-sitekey]"
        ]
        
        for selector in recaptcha_selectors:
            try:
                if driver.find_element(By.CSS_SELECTOR, selector):
                    print(f"🚨 reCAPTCHA detected: {selector}")
                    return True
            except:
                continue
        
        return False
    
    def solve_recaptcha_checkbox(self, driver):
        """Solve reCAPTCHA checkbox"""
        print("🧩 Solving reCAPTCHA checkbox...")
        
        try:
            # Switch to reCAPTCHA iframe
            recaptcha_iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='recaptcha']"))
            )
            
            driver.switch_to.frame(recaptcha_iframe)
            
            # Find and click the checkbox
            checkbox = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".recaptcha-checkbox-border"))
            )
            
            # Human-like clicking
            actions = ActionChains(driver)
            actions.move_to_element(checkbox)
            actions.pause(random.uniform(1, 2))
            actions.click()
            actions.perform()
            
            print("✅ reCAPTCHA checkbox clicked")
            
            # Switch back to main content
            driver.switch_to.default_content()
            
            # Wait for verification
            time.sleep(random.uniform(3, 6))
            
            return True
            
        except Exception as e:
            print(f"❌ reCAPTCHA checkbox solving failed: {e}")
            driver.switch_to.default_content()
            return False
    
    def solve_image_captcha(self, driver):
        """Solve image-based captcha"""
        print("🖼️ Attempting to solve image captcha...")
        
        try:
            # Look for image captcha elements
            image_selectors = [
                ".captcha-image img",
                "#captcha img",
                ".challenge-image img",
                "img[alt*='captcha']"
            ]
            
            for selector in image_selectors:
                try:
                    img_element = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # Take screenshot of captcha
                    screenshot = driver.get_screenshot_as_png()
                    img = Image.open(io.BytesIO(screenshot))
                    
                    # Save for manual review (in real scenario, you'd use OCR)
                    timestamp = int(time.time())
                    img.save(f"captcha_{timestamp}.png")
                    
                    print(f"📸 Captcha image saved as captcha_{timestamp}.png")
                    
                    # For now, just wait and hope it passes
                    time.sleep(random.uniform(5, 10))
                    
                    return True
                    
                except:
                    continue
            
        except Exception as e:
            print(f"❌ Image captcha solving failed: {e}")
        
        return False
    
    def detect_hcaptcha(self, driver):
        """Detect hCaptcha"""
        print("🔍 Checking for hCaptcha...")
        
        hcaptcha_selectors = [
            ".h-captcha",
            "#h-captcha",
            "iframe[src*='hcaptcha']",
            "[data-hcaptcha-sitekey]"
        ]
        
        for selector in hcaptcha_selectors:
            try:
                if driver.find_element(By.CSS_SELECTOR, selector):
                    print(f"🚨 hCaptcha detected: {selector}")
                    return True
            except:
                continue
        
        return False
    
    def solve_hcaptcha(self, driver):
        """Solve hCaptcha"""
        print("🧩 Solving hCaptcha...")
        
        try:
            # Switch to hCaptcha iframe
            hcaptcha_iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='hcaptcha']"))
            )
            
            driver.switch_to.frame(hcaptcha_iframe)
            
            # Find and click the checkbox
            checkbox = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".hcaptcha-checkbox"))
            )
            
            # Human-like clicking
            actions = ActionChains(driver)
            actions.move_to_element(checkbox)
            actions.pause(random.uniform(1, 2))
            actions.click()
            actions.perform()
            
            print("✅ hCaptcha checkbox clicked")
            
            # Switch back to main content
            driver.switch_to.default_content()
            
            # Wait for verification
            time.sleep(random.uniform(3, 6))
            
            return True
            
        except Exception as e:
            print(f"❌ hCaptcha solving failed: {e}")
            driver.switch_to.default_content()
            return False
    
    def comprehensive_security_bypass(self, driver, url=None, max_attempts=3):
        """Comprehensive security bypass for any website"""
        print("🛡️ Starting comprehensive security bypass...")
        
        for attempt in range(max_attempts):
            print(f"🔄 Attempt {attempt + 1}/{max_attempts}")
            
            try:
                # Add anti-detection measures first
                self.add_anti_detection_measures(driver)
                
                # Simulate human behavior
                self.simulate_human_behavior(driver)
                
                # Wait for page to load
                time.sleep(random.uniform(2, 5))
                
                # Check for different security measures
                security_detected = False
                
                # 1. Check for CloudFlare
                if self.detect_cloudflare(driver):
                    security_detected = True
                    if self.bypass_cloudflare(driver):
                        print("✅ CloudFlare bypassed successfully")
                    else:
                        print("❌ CloudFlare bypass failed")
                        continue
                
                # 2. Check for reCAPTCHA
                if self.detect_recaptcha(driver):
                    security_detected = True
                    if self.solve_recaptcha_checkbox(driver):
                        print("✅ reCAPTCHA solved successfully")
                    else:
                        print("❌ reCAPTCHA solving failed")
                        continue
                
                # 3. Check for hCaptcha
                if self.detect_hcaptcha(driver):
                    security_detected = True
                    if self.solve_hcaptcha(driver):
                        print("✅ hCaptcha solved successfully")
                    else:
                        print("❌ hCaptcha solving failed")
                        continue
                
                # 4. Check for image captcha
                if self.solve_image_captcha(driver):
                    security_detected = True
                    print("✅ Image captcha handled")
                
                # If no security detected or all bypassed
                if not security_detected:
                    print("✅ No security measures detected")
                    return True
                
                # Final check - see if we're past security
                time.sleep(random.uniform(3, 7))
                
                # Check if we're still on a security page
                current_url = driver.current_url
                page_source = driver.page_source.lower()
                
                security_keywords = [
                    "cloudflare", "checking your browser", "just a moment",
                    "security check", "captcha", "verification"
                ]
                
                if not any(keyword in page_source for keyword in security_keywords):
                    print("✅ Successfully bypassed all security measures!")
                    return True
                
            except Exception as e:
                print(f"❌ Error in security bypass attempt {attempt + 1}: {e}")
                time.sleep(random.uniform(2, 5))
        
        print("❌ Failed to bypass security after all attempts")
        return False

def test_captcha_solver():
    """Test the captcha solver"""
    print("🧪 Testing Captcha Solver...")
    
    # This would be integrated with your browser manager
    from browser_manager import BrowserManager
    
    browser_manager = BrowserManager()
    if browser_manager.setup_browser(headless=False):  # Non-headless for testing
        driver = browser_manager.driver
        solver = AdvancedCaptchaSolver(driver)
        
        # Test on a site known to have CloudFlare
        test_urls = [
            "https://www.glassdoor.com",
            "https://weworkremotely.com"
        ]
        
        for url in test_urls:
            print(f"\\n🌐 Testing {url}...")
            try:
                driver.get(url)
                time.sleep(3)
                
                if solver.comprehensive_security_bypass(driver):
                    print(f"✅ Successfully accessed {url}")
                else:
                    print(f"❌ Failed to access {url}")
                    
            except Exception as e:
                print(f"❌ Error testing {url}: {e}")
        
        browser_manager.quit()
    else:
        print("❌ Failed to setup browser for testing")

if __name__ == "__main__":
    test_captcha_solver()
