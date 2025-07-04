#!/usr/bin/env python3
"""
Button Finder Utility - Fix for invalid CSS selectors
Replaces invalid pseudo-classes with proper XPath and CSS alternatives
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class ButtonFinder:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout
    
    def find_button_by_text(self, text_patterns, element_types=None):
        """
        Find buttons by text content using XPath (proper alternative to invalid pseudo-classes)
        
        Args:
            text_patterns: List of text patterns to search for
            element_types: List of element types to search in (default: ['button', 'a', 'input'])
        
        Returns:
            First matching element or None
        """
        if element_types is None:
            element_types = ['button', 'a', 'input[@type="submit"]', 'input[@type="button"]']
        
        if isinstance(text_patterns, str):
            text_patterns = [text_patterns]
        
        for pattern in text_patterns:
            for element_type in element_types:
                # XPath patterns for exact and partial text matching
                xpath_patterns = [
                    f"//{element_type}[contains(text(), '{pattern}')]",
                    f"//{element_type}[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{pattern.lower()}')]",
                    f"//{element_type}[contains(@value, '{pattern}')]",
                    f"//{element_type}[contains(@title, '{pattern}')]",
                    f"//{element_type}[contains(@aria-label, '{pattern}')]"
                ]
                
                for xpath in xpath_patterns:
                    try:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                print(f"✅ Found button by text '{pattern}' using XPath: {xpath}")
                                return element
                    except Exception as e:
                        continue
        
        return None
    
    def find_apply_button(self):
        """Find Apply button using multiple strategies"""
        
        # Strategy 1: Find by common Apply button text
        apply_texts = [
            'Apply', 'Apply Now', 'Apply for this job', 'Apply to this position',
            'Easy Apply', 'Quick Apply', 'Submit Application', 'Apply Online',
            'Submit Resume', 'Apply Here'
        ]
        
        button = self.find_button_by_text(apply_texts)
        if button:
            return button
        
        # Strategy 2: Find by CSS selectors (safe ones only)
        css_selectors = [
            # Class-based selectors
            "button[class*='apply']",
            "a[class*='apply']",
            ".apply-button", ".apply-btn", ".btn-apply",
            ".apply-link", ".apply-now",
            
            # ID-based selectors
            "#apply-button", "#apply-btn", "#apply",
            "[id*='apply']",
            
            # Data attribute selectors
            "[data-test*='apply']", "[data-cy*='apply']",
            "[data-testid*='apply']", "[data-apply]",
            
            # ARIA and title selectors
            "[aria-label*='Apply']", "[title*='Apply']",
            "button[title*='apply']", "a[title*='apply']",
            
            # URL-based selectors for external applications
            "a[href*='apply']", "a[href*='application']",
            "a[href*='jobs/apply']", "a[href*='career']"
        ]
        
        for selector in css_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✅ Found Apply button using CSS: {selector}")
                        return element
            except Exception:
                continue
        
        # Strategy 3: Context-aware search
        button = self.find_contextual_apply_button()
        if button:
            return button
        
        print("❌ No Apply button found with any strategy")
        return None
    
    def find_contextual_apply_button(self):
        """Find Apply button within job listing context"""
        
        # Look for job containers
        container_selectors = [
            ".job-card", ".job-listing", ".job-details", 
            ".job-container", "[data-job]", ".posting",
            ".job-item", ".job", "article[class*='job']"
        ]
        
        for container_selector in container_selectors:
            try:
                containers = self.driver.find_elements(By.CSS_SELECTOR, container_selector)
                for container in containers:
                    # Look for clickable elements within this container
                    clickable_elements = container.find_elements(
                        By.CSS_SELECTOR, 
                        "button, a[href], input[type='submit'], input[type='button']"
                    )
                    
                    for element in clickable_elements:
                        if not (element.is_displayed() and element.is_enabled()):
                            continue
                        
                        # Check text content and attributes
                        element_text = element.text.lower()
                        element_html = element.get_attribute("outerHTML").lower()
                        
                        apply_keywords = ["apply", "submit", "application"]
                        
                        if any(keyword in element_text or keyword in element_html 
                               for keyword in apply_keywords):
                            print(f"✅ Found contextual Apply button in {container_selector}")
                            return element
            except Exception:
                continue
        
        return None
    
    def find_login_button(self):
        """Find login/sign-in button"""
        
        # Strategy 1: Text-based search
        login_texts = [
            'Sign In', 'Log In', 'Login', 'Sign in', 'Log in',
            'Enter', 'Access', 'Sign On', 'Sign-in', 'Log-in'
        ]
        
        button = self.find_button_by_text(login_texts)
        if button:
            return button
        
        # Strategy 2: CSS selectors
        login_selectors = [
            "a[href*='sign-in']", "a[href*='signin']",
            "a[href*='login']", "a[href*='log-in']",
            ".login", ".signin", ".sign-in",
            "[title*='Sign In']", "[title*='Login']",
            "[aria-label*='Sign In']", "[aria-label*='Login']"
        ]
        
        for selector in login_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✅ Found login button using: {selector}")
                        return element
            except Exception:
                continue
        
        return None
    
    def click_button_safely(self, button, description="button"):
        """Safely click a button with multiple fallback methods"""
        
        if not button:
            print(f"❌ No {description} provided to click")
            return False
        
        try:
            # Scroll to button
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(1)
            
            # Method 1: Regular click
            try:
                button.click()
                print(f"✅ Successfully clicked {description} (regular click)")
                return True
            except Exception as e:
                print(f"⚠️ Regular click failed: {e}")
            
            # Method 2: JavaScript click
            try:
                self.driver.execute_script("arguments[0].click();", button)
                print(f"✅ Successfully clicked {description} (JavaScript click)")
                return True
            except Exception as e:
                print(f"⚠️ JavaScript click failed: {e}")
            
            # Method 3: ActionChains click
            try:
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).move_to_element(button).click().perform()
                print(f"✅ Successfully clicked {description} (ActionChains click)")
                return True
            except Exception as e:
                print(f"⚠️ ActionChains click failed: {e}")
            
            print(f"❌ All click methods failed for {description}")
            return False
            
        except Exception as e:
            print(f"❌ Unexpected error clicking {description}: {e}")
            return False

# Test function
def test_button_finder():
    """Test the button finder utility"""
    from browser_manager import BrowserManager
    
    print("🧪 Testing Button Finder Utility...")
    
    # Setup browser
    browser_manager = BrowserManager()
    if not browser_manager.setup_browser(headless=False):
        print("❌ Browser setup failed")
        return
    
    finder = ButtonFinder(browser_manager.driver)
    
    # Test on a job site
    test_url = "https://remoteok.io"
    print(f"🔍 Testing on: {test_url}")
    
    try:
        browser_manager.driver.get(test_url)
        time.sleep(3)
        
        # Test finding Apply button
        apply_button = finder.find_apply_button()
        if apply_button:
            print("✅ Apply button found successfully")
        else:
            print("❌ Apply button not found")
        
        # Test finding login button
        login_button = finder.find_login_button()
        if login_button:
            print("✅ Login button found successfully")
        else:
            print("❌ Login button not found")
        
    except Exception as e:
        print(f"⚠️ Test error: {e}")
    
    browser_manager.quit()
    print("🧪 Test completed")

if __name__ == "__main__":
    test_button_finder()
