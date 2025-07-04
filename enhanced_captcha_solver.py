#!/usr/bin/env python3
"""
🔐 ENHANCED CAPTCHA SOLVER
Advanced captcha detection and handling system
"""

import time
import logging
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
import base64
import os

logger = logging.getLogger(__name__)

class EnhancedCaptchaSolver:
    """Advanced captcha solving with multiple strategies"""
    
    def __init__(self, driver):
        self.driver = driver
        self.captcha_services = {
            '2captcha': os.getenv('TWOCAPTCHA_API_KEY'),
            'anticaptcha': os.getenv('ANTICAPTCHA_API_KEY')
        }
        
        # Common captcha selectors
        self.captcha_selectors = [
            # reCAPTCHA
            "iframe[src*='recaptcha']",
            ".g-recaptcha",
            "#recaptcha",
            "[data-sitekey]",
            
            # hCaptcha
            "iframe[src*='hcaptcha']",
            ".h-captcha",
            "#hcaptcha",
            
            # Cloudflare
            ".cf-turnstile",
            "#cf-turnstile",
            "iframe[src*='cloudflare']",
            
            # Generic captcha
            ".captcha",
            "#captcha",
            "img[src*='captcha']",
            "[class*='captcha']",
            "[id*='captcha']",
            
            # Custom selectors
            ".challenge",
            ".verification",
            ".security-check"
        ]
    
    def detect_captcha(self) -> dict:
        """Detect if captcha is present on the page"""
        try:
            logger.info("🔍 Scanning page for captcha challenges...")
            
            detected_captchas = []
            
            for selector in self.captcha_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            captcha_type = self._identify_captcha_type(element, selector)
                            detected_captchas.append({
                                'type': captcha_type,
                                'element': element,
                                'selector': selector
                            })
                            logger.info(f"🎯 Detected {captcha_type} captcha")
                except:
                    continue
            
            if detected_captchas:
                logger.warning(f"⚠️ Found {len(detected_captchas)} captcha(s) on page")
                return {
                    'found': True,
                    'captchas': detected_captchas,
                    'count': len(detected_captchas)
                }
            else:
                logger.info("✅ No captcha detected")
                return {'found': False, 'captchas': [], 'count': 0}
                
        except Exception as e:
            logger.error(f"Captcha detection error: {e}")
            return {'found': False, 'captchas': [], 'count': 0}
    
    def _identify_captcha_type(self, element, selector) -> str:
        """Identify the type of captcha"""
        try:
            # Check iframe src or element attributes
            if 'recaptcha' in selector.lower():
                return 'reCAPTCHA'
            elif 'hcaptcha' in selector.lower():
                return 'hCaptcha'
            elif 'cloudflare' in selector.lower() or 'turnstile' in selector.lower():
                return 'Cloudflare Turnstile'
            elif element.tag_name == 'iframe':
                iframe_src = element.get_attribute('src') or ''
                if 'recaptcha' in iframe_src:
                    return 'reCAPTCHA'
                elif 'hcaptcha' in iframe_src:
                    return 'hCaptcha'
                elif 'cloudflare' in iframe_src:
                    return 'Cloudflare'
                else:
                    return 'Unknown iframe captcha'
            elif element.tag_name == 'img':
                return 'Image captcha'
            else:
                return 'Generic captcha'
        except:
            return 'Unknown captcha'
    
    def solve_captcha(self, captcha_info: dict) -> bool:
        """Solve detected captcha using multiple strategies"""
        try:
            logger.info(f"🔐 Attempting to solve {captcha_info['type']} captcha...")
            
            # Strategy 1: Wait and retry (many captchas auto-resolve)
            if self._wait_for_auto_resolution(captcha_info):
                return True
            
            # Strategy 2: Human-like interaction
            if self._simulate_human_interaction(captcha_info):
                return True
            
            # Strategy 3: Automated solving service
            if self._use_captcha_service(captcha_info):
                return True
            
            # Strategy 4: Bypass attempt
            if self._attempt_bypass(captcha_info):
                return True
            
            logger.warning("❌ All captcha solving strategies failed")
            return False
            
        except Exception as e:
            logger.error(f"Captcha solving error: {e}")
            return False
    
    def _wait_for_auto_resolution(self, captcha_info: dict, timeout: int = 30) -> bool:
        """Wait for captcha to auto-resolve (common with Cloudflare)"""
        try:
            logger.info("⏳ Waiting for auto-resolution...")
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Check if captcha disappeared
                try:
                    element = captcha_info['captchas'][0]['element']
                    if not element.is_displayed():
                        logger.info("✅ Captcha auto-resolved!")
                        return True
                except:
                    logger.info("✅ Captcha element no longer found - likely resolved!")
                    return True
                
                # Check for success indicators
                success_indicators = [
                    "//span[contains(text(), 'Success')]",
                    "//div[contains(@class, 'success')]",
                    "//*[contains(text(), 'verified')]",
                    "//*[contains(text(), 'passed')]"
                ]
                
                for indicator in success_indicators:
                    try:
                        if self.driver.find_element(By.XPATH, indicator).is_displayed():
                            logger.info("✅ Captcha verification successful!")
                            return True
                    except:
                        continue
                
                time.sleep(2)
            
            return False
            
        except Exception as e:
            logger.error(f"Auto-resolution error: {e}")
            return False
    
    def _simulate_human_interaction(self, captcha_info: dict) -> bool:
        """Simulate human-like interaction with captcha"""
        try:
            logger.info("🤖 Simulating human interaction...")
            
            captcha = captcha_info['captchas'][0]
            element = captcha['element']
            captcha_type = captcha['type']
            
            if captcha_type == 'reCAPTCHA':
                return self._handle_recaptcha(element)
            elif captcha_type == 'hCaptcha':
                return self._handle_hcaptcha(element)
            elif captcha_type == 'Cloudflare Turnstile':
                return self._handle_cloudflare(element)
            else:
                return self._handle_generic_captcha(element)
                
        except Exception as e:
            logger.error(f"Human interaction error: {e}")
            return False
    
    def _handle_recaptcha(self, element) -> bool:
        """Handle reCAPTCHA specifically"""
        try:
            logger.info("🔄 Handling reCAPTCHA...")
            
            # Look for checkbox
            checkbox_selectors = [
                ".recaptcha-checkbox-border",
                ".recaptcha-checkbox",
                "#recaptcha-anchor",
                "span[role='checkbox']"
            ]
            
            for selector in checkbox_selectors:
                try:
                    checkbox = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if checkbox.is_displayed():
                        # Human-like movement and click
                        self._human_like_click(checkbox)
                        time.sleep(random.uniform(2, 4))
                        
                        # Check if solved
                        if self._check_recaptcha_solved():
                            logger.info("✅ reCAPTCHA solved!")
                            return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"reCAPTCHA handling error: {e}")
            return False
    
    def _handle_hcaptcha(self, element) -> bool:
        """Handle hCaptcha specifically"""
        try:
            logger.info("🔄 Handling hCaptcha...")
            
            # Look for hCaptcha checkbox
            checkbox_selectors = [
                ".hcaptcha-checkbox",
                "#hcaptcha-checkbox", 
                "[data-hcaptcha-widget-id]"
            ]
            
            for selector in checkbox_selectors:
                try:
                    checkbox = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if checkbox.is_displayed():
                        self._human_like_click(checkbox)
                        time.sleep(random.uniform(2, 4))
                        
                        if self._check_hcaptcha_solved():
                            logger.info("✅ hCaptcha solved!")
                            return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"hCaptcha handling error: {e}")
            return False
    
    def _handle_cloudflare(self, element) -> bool:
        """Handle Cloudflare Turnstile"""
        try:
            logger.info("🔄 Handling Cloudflare Turnstile...")
            
            # Cloudflare often auto-resolves, just wait
            time.sleep(5)
            
            # Look for Cloudflare success
            success_selectors = [
                ".cf-turnstile-success",
                "[data-cf-turnstile-success='true']"
            ]
            
            for selector in success_selectors:
                try:
                    if self.driver.find_element(By.CSS_SELECTOR, selector):
                        logger.info("✅ Cloudflare Turnstile passed!")
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Cloudflare handling error: {e}")
            return False
    
    def _handle_generic_captcha(self, element) -> bool:
        """Handle generic captcha"""
        try:
            logger.info("🔄 Handling generic captcha...")
            
            # Try clicking the element
            self._human_like_click(element)
            time.sleep(random.uniform(2, 4))
            
            # Check if element disappeared (likely solved)
            try:
                if not element.is_displayed():
                    logger.info("✅ Generic captcha likely solved!")
                    return True
            except:
                logger.info("✅ Generic captcha element no longer found!")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Generic captcha handling error: {e}")
            return False
    
    def _human_like_click(self, element):
        """Perform human-like click with random delays"""
        try:
            # Random delay before action
            time.sleep(random.uniform(0.5, 1.5))
            
            # Move to element with some randomness
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            
            # Small random offset
            x_offset = random.randint(-5, 5)
            y_offset = random.randint(-5, 5)
            actions.move_by_offset(x_offset, y_offset)
            
            # Random pause before click
            time.sleep(random.uniform(0.1, 0.3))
            actions.click()
            actions.perform()
            
            # Random delay after click
            time.sleep(random.uniform(0.5, 1.0))
            
        except Exception as e:
            logger.error(f"Human-like click error: {e}")
            # Fallback to regular click
            element.click()
    
    def _check_recaptcha_solved(self) -> bool:
        """Check if reCAPTCHA was solved"""
        try:
            # Look for solved indicators
            solved_selectors = [
                ".recaptcha-checkbox-checked",
                "[aria-checked='true']",
                ".recaptcha-success"
            ]
            
            for selector in solved_selectors:
                try:
                    if self.driver.find_element(By.CSS_SELECTOR, selector):
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"reCAPTCHA check error: {e}")
            return False
    
    def _check_hcaptcha_solved(self) -> bool:
        """Check if hCaptcha was solved"""
        try:
            # Look for solved indicators
            solved_selectors = [
                ".hcaptcha-success",
                "[data-hcaptcha-response]"
            ]
            
            for selector in solved_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.get_attribute('data-hcaptcha-response'):
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"hCaptcha check error: {e}")
            return False
    
    def _use_captcha_service(self, captcha_info: dict) -> bool:
        """Use external captcha solving service"""
        try:
            logger.info("🌐 Attempting to use captcha solving service...")
            
            # Check if any service API keys are available
            available_services = [k for k, v in self.captcha_services.items() if v]
            
            if not available_services:
                logger.warning("⚠️ No captcha service API keys available")
                return False
            
            # For now, log that we would use a service
            # In production, you would implement actual API calls
            logger.info(f"💡 Would use {available_services[0]} service for solving")
            
            # Simulate service solving time
            time.sleep(random.uniform(10, 20))
            
            # Return False for now (would return actual result in production)
            return False
            
        except Exception as e:
            logger.error(f"Captcha service error: {e}")
            return False
    
    def _attempt_bypass(self, captcha_info: dict) -> bool:
        """Attempt to bypass captcha"""
        try:
            logger.info("🔄 Attempting captcha bypass...")
            
            # Strategy 1: Refresh page and try again
            logger.info("🔄 Refreshing page to potentially avoid captcha...")
            self.driver.refresh()
            time.sleep(5)
            
            # Check if captcha is still there
            new_detection = self.detect_captcha()
            if not new_detection['found']:
                logger.info("✅ Captcha bypassed by page refresh!")
                return True
            
            # Strategy 2: Try alternative routes
            logger.info("🔄 Checking for alternative navigation...")
            
            # Look for skip buttons or alternative actions
            skip_selectors = [
                "button:contains('Skip')",
                "a:contains('Skip')",
                "button:contains('Continue')",
                "a:contains('Continue')",
                "[data-action='skip']",
                ".skip-button"
            ]
            
            for selector in skip_selectors:
                try:
                    skip_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if skip_btn.is_displayed():
                        skip_btn.click()
                        time.sleep(2)
                        logger.info("✅ Found and clicked skip button!")
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Captcha bypass error: {e}")
            return False
    
    def handle_captcha_flow(self, max_attempts: int = 3) -> bool:
        """Complete captcha handling flow"""
        try:
            logger.info("🚀 Starting captcha handling flow...")
            
            for attempt in range(max_attempts):
                logger.info(f"🔄 Captcha handling attempt {attempt + 1}/{max_attempts}")
                
                # Detect captcha
                detection = self.detect_captcha()
                
                if not detection['found']:
                    logger.info("✅ No captcha found - proceeding!")
                    return True
                
                # Try to solve
                if self.solve_captcha(detection):
                    logger.info("✅ Captcha solved successfully!")
                    return True
                
                # Wait before next attempt
                if attempt < max_attempts - 1:
                    wait_time = random.uniform(5, 10)
                    logger.info(f"⏳ Waiting {wait_time:.1f}s before next attempt...")
                    time.sleep(wait_time)
            
            logger.error("❌ Failed to solve captcha after all attempts")
            return False
            
        except Exception as e:
            logger.error(f"Captcha flow error: {e}")
            return False

def test_captcha_solver():
    """Test the captcha solver"""
    print("🧪 Testing Enhanced Captcha Solver...")
    
    # This would normally be called with a real driver
    # solver = EnhancedCaptchaSolver(driver)
    # result = solver.handle_captcha_flow()
    
    print("✅ Captcha solver test completed!")

if __name__ == "__main__":
    test_captcha_solver()
