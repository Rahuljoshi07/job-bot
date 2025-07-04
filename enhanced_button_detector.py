#!/usr/bin/env python3
"""
Enhanced Button Detector for Job Applications
Robust Apply button detection across multiple job platforms
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

class EnhancedButtonDetector:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout
        
    def find_apply_button(self, platform="generic"):
        """
        Find Apply button using multiple strategies
        Returns (element, method_used) or (None, None)
        """
        print(f"🔍 Searching for Apply button on {platform}...")
        
        # Strategy 1: Platform-specific selectors
        platform_selectors = self.get_platform_selectors(platform)
        for i, selector in enumerate(platform_selectors):
            element = self._try_selector(selector, f"Platform-specific #{i+1}")
            if element:
                return element, f"platform_specific_{i+1}"
        
        # Strategy 2: Generic Apply button patterns
        generic_selectors = self.get_generic_apply_selectors()
        for i, selector in enumerate(generic_selectors):
            element = self._try_selector(selector, f"Generic pattern #{i+1}")
            if element:
                return element, f"generic_{i+1}"
        
        # Strategy 3: Text-based search
        text_element = self._find_by_text()
        if text_element:
            return text_element, "text_search"
        
        # Strategy 4: Contextual search (buttons near job listings)
        contextual_element = self._find_contextual_button()
        if contextual_element:
            return contextual_element, "contextual"
        
        # Strategy 5: AI-style fuzzy matching
        fuzzy_element = self._fuzzy_button_search()
        if fuzzy_element:
            return fuzzy_element, "fuzzy_match"
        
        print("❌ No Apply button found with any strategy")
        return None, None
    
    def get_platform_selectors(self, platform):
        """Get platform-specific selectors"""
        selectors = {
            "remoteok": [
                "a[href*='apply']",
                ".apply-link",
                "[data-apply-url]",
                "a[href*='mailto']",
                ".apply-button",
                "a[target='_blank'][href*='apply']"
            ],
            "linkedin": [
                ".jobs-apply-button",
                "[aria-label*='Easy Apply']",
                "[data-control-name='jobdetails_topcard_inapply']",
                ".artdeco-button--primary[aria-label*='Apply']",
                "button[aria-label*='Easy Apply']"
            ],
            "indeed": [
                "[data-testid='apply-button']",
                ".jobsearch-IndeedApplyButton",
                ".ia-IndeedApplyButton",
                "button[title*='Apply']",
                "[data-tn-element='applyButton']"
            ],
            "dice": [
                ".apply-button-wag",
                "[data-cy='apply-button']",
                ".btn-apply",
                "button[data-testid='apply-button']"
            ],
            "glassdoor": [
                "[data-test='apply-button']",
                ".apply-btn",
                "button[aria-label*='Apply']"
            ],
            "wellfound": [
                "[data-test='apply']",
                ".apply-button",
                "button[title*='Apply']",
                "[href*='apply']"
            ],
            "xtwitter": [
                "a[href*='careers.x.com']",
                "a[href*='apply']",
                "[role='button'][aria-label*='Apply']",
                ".apply-button",
                "button[data-testid*='apply']",
                "a[data-testid*='apply']",
                "[href*='x.com/jobs']",
                "[href*='twitter.com/jobs']",
                "[href*='jobs.x.com']",
                "[data-testid='apply']",
                "button[aria-label*='apply']",
                "a[class*='apply']",
                "[role='link'][href*='apply']",
                ".career-apply-btn",
                "[data-qa='apply-button']"
            ],
            "x/twitter": [
                "a[href*='careers.x.com']",
                "a[href*='apply']",
                "[role='button'][aria-label*='Apply']",
                ".apply-button",
                "button[data-testid*='apply']",
                "a[data-testid*='apply']",
                "[href*='x.com/jobs']",
                "[href*='twitter.com/jobs']"
            ],
            "twitter": [
                "a[href*='careers.x.com']",
                "a[href*='apply']",
                "[role='button'][aria-label*='Apply']",
                ".apply-button",
                "button[data-testid*='apply']",
                "a[data-testid*='apply']",
                "[href*='x.com/jobs']",
                "[href*='twitter.com/jobs']"
            ],
            "turing": [
                "[data-cy='apply-button']",
                ".apply-button",
                "button[class*='apply']",
                "a[href*='apply']",
                "[href*='turing.com/apply']",
                "button[title*='Apply']",
                ".btn-primary[href*='apply']",
                "[data-testid*='apply']",
                "[data-qa='apply']",
                ".job-apply-button",
                "button[type='submit'][class*='apply']",
                "a[class*='btn'][href*='apply']",
                ".opportunity-apply",
                "[role='button'][data-action='apply']",
                "button[aria-label*='Apply']",
                ".submit-application",
                "[data-testid='job-apply']"
            ],
            "weworkremotely": [
                "a[href*='apply']",
                ".apply-button",
                "button[class*='apply']",
                "[data-apply]",
                "button[title*='Apply']",
                ".btn[href*='apply']"
            ]
        }
        return selectors.get(platform.lower(), [])
    
    def get_generic_apply_selectors(self):
        """Generic Apply button selectors that work across platforms"""
        return [
            # Standard apply button patterns
            "button[class*='apply']",
            "a[class*='apply']",
            "[class*='apply-button']",
            "[class*='apply-btn']",
            
            # ID-based patterns
            "#apply-button",
            "#apply-btn",
            "[id*='apply']",
            
            # ARIA and accessibility patterns
            "[aria-label*='Apply']",
            "[aria-label*='apply']",
            "button[role='button'][aria-label*='Apply']",
            
            # Data attribute patterns
            "[data-apply]",
            "[data-test*='apply']",
            "[data-cy*='apply']",
            "[data-testid*='apply']",
            
            # URL-based patterns (external applications)
            "a[href*='apply']",
            "a[href*='application']",
            "a[href*='jobs/apply']",
            "a[href*='career']",
            
            # Button with apply-related text
            "button[title*='Apply']",
            "button[title*='apply']",
            "a[title*='Apply']",
            "a[title*='apply']",
            
            # Form-based patterns
            "input[type='submit'][value*='Apply']",
            "input[type='button'][value*='Apply']",
            
            # Modern CSS patterns
            ".btn-primary[href*='apply']",
            ".button-primary[href*='apply']",
            ".cta-button[href*='apply']"
        ]
    
    def _try_selector(self, selector, description):
        """Try a single CSS selector"""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                # Filter for visible and clickable elements
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✅ Found Apply button using {description}: {selector}")
                        return element
        except Exception as e:
            # Silent fail, continue to next strategy
            pass
        return None
    
    def _find_by_text(self):
        """Find buttons by text content"""
        text_patterns = [
            "Apply",
            "Apply Now",
            "Apply for this job",
            "Apply to this position",
            "Easy Apply",
            "Quick Apply",
            "Submit Application",
            "Apply Online"
        ]
        
        # XPath patterns for text-based search
        xpath_patterns = [
            f"//button[contains(text(), '{pattern}')]" for pattern in text_patterns
        ] + [
            f"//a[contains(text(), '{pattern}')]" for pattern in text_patterns
        ] + [
            f"//input[@type='submit' and contains(@value, '{pattern}')]" for pattern in text_patterns
        ]
        
        for pattern in xpath_patterns:
            try:
                elements = self.driver.find_elements(By.XPATH, pattern)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✅ Found Apply button by text: {pattern}")
                        return element
            except:
                continue
        
        return None
    
    def _find_contextual_button(self):
        """Find Apply button in context of job listing"""
        # Look for buttons within job containers
        job_container_selectors = [
            ".job-card",
            ".job-listing",
            ".job-details",
            ".job-container",
            "[data-job]",
            ".posting"
        ]
        
        for container_selector in job_container_selectors:
            try:
                containers = self.driver.find_elements(By.CSS_SELECTOR, container_selector)
                for container in containers:
                    # Look for apply buttons within this container
                    apply_buttons = container.find_elements(By.CSS_SELECTOR, 
                        "button, a[href], input[type='submit']")
                    
                    for button in apply_buttons:
                        button_text = button.text.lower()
                        button_attrs = str(button.get_attribute("outerHTML")).lower()
                        
                        if any(keyword in button_text + button_attrs for keyword in 
                              ["apply", "submit", "application"]):
                            if button.is_displayed() and button.is_enabled():
                                print(f"✅ Found Apply button in job container")
                                return button
            except:
                continue
        
        return None
    
    def _fuzzy_button_search(self):
        """AI-style fuzzy matching for Apply buttons"""
        # Get all clickable elements
        try:
            all_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                "button, a[href], input[type='submit'], input[type='button']")
            
            apply_keywords = ["apply", "application", "submit", "career", "job"]
            
            scored_buttons = []
            
            for button in all_buttons:
                if not (button.is_displayed() and button.is_enabled()):
                    continue
                
                score = 0
                button_html = str(button.get_attribute("outerHTML")).lower()
                button_text = button.text.lower()
                
                # Score based on text content
                for keyword in apply_keywords:
                    if keyword in button_text:
                        score += 3
                    if keyword in button_html:
                        score += 1
                
                # Bonus for common apply patterns
                if "apply" in button_text and len(button_text.split()) <= 3:
                    score += 5
                
                # Penalty for unlikely buttons
                if any(word in button_text for word in ["cancel", "close", "back", "previous"]):
                    score -= 2
                
                if score > 0:
                    scored_buttons.append((button, score))
            
            # Return highest scoring button
            if scored_buttons:
                best_button = max(scored_buttons, key=lambda x: x[1])
                if best_button[1] >= 3:  # Minimum confidence threshold
                    print(f"✅ Found Apply button via fuzzy matching (score: {best_button[1]})")
                    return best_button[0]
        
        except Exception as e:
            print(f"⚠️ Fuzzy search failed: {e}")
        
        return None
    
    def click_apply_button(self, platform="generic", take_screenshot_callback=None):
        """
        Find and click Apply button with error handling
        Returns (success, method_used, error_message)
        """
        button, method = self.find_apply_button(platform)
        
        if not button:
            return False, None, "No Apply button found"
        
        try:
            # Scroll to button
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(1)
            
            # Take screenshot before clicking if callback provided
            if take_screenshot_callback:
                take_screenshot_callback("before_apply_click")
            
            # Try different click methods
            click_success = False
            error_msg = ""
            
            # Method 1: Regular click
            try:
                button.click()
                click_success = True
                print("✅ Applied using regular click")
            except Exception as e:
                error_msg = str(e)
                
                # Method 2: JavaScript click
                try:
                    self.driver.execute_script("arguments[0].click();", button)
                    click_success = True
                    print("✅ Applied using JavaScript click")
                except Exception as e2:
                    error_msg = str(e2)
                    
                    # Method 3: ActionChains click
                    try:
                        from selenium.webdriver.common.action_chains import ActionChains
                        ActionChains(self.driver).move_to_element(button).click().perform()
                        click_success = True
                        print("✅ Applied using ActionChains click")
                    except Exception as e3:
                        error_msg = str(e3)
            
            if click_success:
                time.sleep(2)  # Wait for response
                
                # Take screenshot after clicking if callback provided
                if take_screenshot_callback:
                    take_screenshot_callback("after_apply_click")
                
                return True, method, None
            else:
                return False, method, f"Click failed: {error_msg}"
        
        except Exception as e:
            return False, method, f"Unexpected error: {str(e)}"

# Test function
def test_button_detector():
    """Test the button detector"""
    from browser_manager import BrowserManager
    
    print("🧪 Testing Enhanced Button Detector...")
    
    # Setup browser
    browser_manager = BrowserManager()
    if not browser_manager.setup_browser(headless=False):
        print("❌ Browser setup failed")
        return
    
    detector = EnhancedButtonDetector(browser_manager.driver)
    
    # Test on different job sites
    test_sites = [
        ("https://remoteok.io", "remoteok"),
        ("https://www.indeed.com/jobs?q=developer", "indeed"),
        ("https://www.dice.com/jobs", "dice")
    ]
    
    for url, platform in test_sites:
        print(f"\n🔍 Testing on {platform}: {url}")
        try:
            browser_manager.driver.get(url)
            time.sleep(3)
            
            button, method = detector.find_apply_button(platform)
            if button:
                print(f"✅ Found Apply button on {platform} using method: {method}")
            else:
                print(f"❌ No Apply button found on {platform}")
        except Exception as e:
            print(f"⚠️ Error testing {platform}: {e}")
    
    browser_manager.quit()
    print("🧪 Test completed")

if __name__ == "__main__":
    test_button_detector()
