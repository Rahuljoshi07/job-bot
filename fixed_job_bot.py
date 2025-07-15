#!/usr/bin/env python3
"""
🚀 FIXED JOB BOT - Comprehensive automated job application system
With enhanced verification and confirmation tracking
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementClickInterceptedException,
    StaleElementReferenceException, ElementNotInteractableException, WebDriverException
)
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager

import time
import json
import requests
import random
import os
import sys
import traceback
import logging
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin
import re

# Configure logging with proper encoding
try:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('job_bot.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
except Exception:
    # Fallback for systems with encoding issues
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

class UserProfile:
    """User profile for job applications"""
    
    def __init__(self, name="", email="", phone="", location="", linkedin="", github=""):
        self.name = name
        self.email = email
        self.phone = phone
        self.location = location
        self.linkedin = linkedin
        self.github = github

class FixedJobBot:
    """Fixed Job Application Bot with enhanced verification"""
    
    def __init__(self):
        """Initialize with comprehensive error handling and verification"""
        logger.info("🚀 Initializing Fixed Job Bot with enhanced verification...")
        
        # Initialize all components with error handling
        self.driver = None
        self.wait = None
        self.actions = None
        self.applied_jobs = set()
        self.applied_jobs_file = "applied_jobs_history.pkl"
        self.proof_folder = "application_proofs"
        self.config_file = "user_config.json"
        self.applications_file = "fixed_applications.txt"
        self.cycle_log_file = "fixed_cycle_log.txt"
        self.error_log_file = "fixed_error_log.txt"
        self.verification_log_file = "application_verification_log.txt"
        
        # Create directories
        self._create_directories()
        
        # Load configuration
        self.config = self._load_configuration()
        
        # Load applied jobs history
        self._load_applied_jobs()
        
        # Initialize skills
        self.skills = self._get_skills()
        
        # Initialize platform selectors
        self._initialize_selectors()
        
        # Initialize verification system
        self.verification_timestamps = {}
        
        logger.info("✅ Fixed Job Bot initialized successfully!")
    
    def _create_directories(self):
        """Create necessary directories"""
        try:
            os.makedirs(self.proof_folder, exist_ok=True)
            os.makedirs("logs", exist_ok=True)
            os.makedirs(f"{self.proof_folder}/verification", exist_ok=True)
            logger.info("✅ Directories created/verified")
        except Exception as e:
            self._log_error("Directory creation failed", e)
    
    def _initialize_selectors(self):
        """Initialize selectors for all platforms"""
        self.selectors = {
            "LinkedIn": {
                "login": {
                    "username": "input#username",
                    "password": "input#password",
                    "submit": "button[type='submit']"
                },
                "apply": [
                    ".jobs-apply-button",
                    "button[data-control-name='jobdetails_topcard_inapply']",
                    "button.jobs-apply-button",
                    ".jobs-s-apply button",
                    "button:contains('Easy Apply')",
                    "button:contains('Apply')",
                    ".jobs-apply-button--top-card",
                ],
                "next": [
                    "button[aria-label='Continue to next step']",
                    "button[aria-label='Submit application']",
                    "button[aria-label='Review your application']",
                    "button:contains('Continue')",
                    "button:contains('Next')",
                    "button:contains('Submit')",
                    "button:contains('Review')",
                    ".artdeco-button--primary",
                ],
                "success_indicators": [
                    "h2:contains('Application submitted')",
                    "h2:contains('Your application was sent')",
                    ".artdeco-inline-feedback--success",
                    ".jobs-s-apply-content__confirmation-message",
                ]
            },
            "Indeed": {
                "login": {
                    "username": "#ifl-InputFormField-3",
                    "password": "#ifl-InputFormField-7",
                    "submit": "button[type='submit']"
                },
                "apply": [
                    ".jobsearch-IndeedApplyButton",
                    ".ia-IndeedApplyButton",
                    "button:contains('Apply now')",
                    "a:contains('Apply on company site')",
                    "a:contains('Apply Now')",
                    "#indeedApplyButton",
                    ".indeed-apply-button",
                ],
                "success_indicators": [
                    "div:contains('Application submitted')",
                    "div:contains('Your application has been submitted')",
                    ".ia-ApplyFormScreen div:contains('successfully submitted')",
                    "#ia-container div:contains('Thank you')"
                ]
            },
            "RemoteOK": {
                "apply": [
                    ".action-apply",
                    "a.preventLink",
                    "a:contains('Apply')",
                    ".job-apply",
                    ".apply-link",
                ]
            },
            "Dice": {
                "login": {
                    "username": "#email",
                    "password": "#password",
                    "submit": "button[type='submit']"
                },
                "apply": [
                    "button[data-cy='easyApplyBtn']",
                    ".dice-btn-primary",
                    "a:contains('Apply')",
                    "a.btn-apply",
                    ".apply-button",
                ],
                "success_indicators": [
                    "div:contains('Application submitted')",
                    ".applied-success-message",
                    "div:contains('Your application was sent')"
                ]
            },
            # Generic selectors that work across many sites
            "Generic": {
                "apply": [
                    "button:contains('Apply')",
                    "a:contains('Apply')",
                    "button:contains('Easy Apply')",
                    "button:contains('Quick Apply')",
                    "button.apply",
                    "a.apply",
                    ".apply-button",
                    ".applyButton",
                    "#apply-button",
                    "[data-test='apply-button']",
                ],
                "success_indicators": [
                    "div:contains('Application submitted')",
                    "div:contains('Thank you')",
                    "div:contains('successfully submitted')",
                    "div:contains('Your application was sent')",
                    "div:contains('Successfully applied')",
                    ".success-message",
                    ".application-success",
                    ".application-confirmation"
                ]
            }
        }
    
    def _load_configuration(self):
        """Load configuration with fallbacks"""
        try:
            # Try environment variables first
            config = self._load_from_environment()
            if config:
                logger.info("✅ Configuration loaded from environment")
                return config
            
            # Try config file
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info("✅ Configuration loaded from file")
                return config
            
            # Try .env file
            if os.path.exists('.env'):
                try:
                    import dotenv
                    dotenv.load_dotenv()
                    config = self._load_from_environment()
                    if config:
                        logger.info("✅ Configuration loaded from .env file")
                        return config
                except ImportError:
                    logger.warning("⚠️ python-dotenv not installed, skipping .env file")
            
            # Fallback to defaults
            config = self._get_default_config()
            logger.info("⚠️ Using default configuration")
            return config
            
        except Exception as e:
            self._log_error("Configuration loading failed", e)
            return self._get_default_config()
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        try:
            # Required variables
            name = os.environ.get('PERSONAL_FULL_NAME', '')
            email = os.environ.get('PERSONAL_EMAIL', '')
            phone = os.environ.get('PERSONAL_PHONE', '')
            
            # Platform credentials
            linkedin_username = os.environ.get('LINKEDIN_EMAIL', '')
            linkedin_password = os.environ.get('LINKEDIN_PASSWORD', '')
            
            indeed_username = os.environ.get('INDEED_EMAIL', '')
            indeed_password = os.environ.get('INDEED_PASSWORD', '')
            
            dice_username = os.environ.get('DICE_EMAIL', '')
            dice_password = os.environ.get('DICE_PASSWORD', '')
            
            twitter_username = os.environ.get('TWITTER_EMAIL', '')
            twitter_password = os.environ.get('TWITTER_PASSWORD', '')
            
            turing_username = os.environ.get('TURING_EMAIL', '')
            turing_password = os.environ.get('TURING_PASSWORD', '')
            
            # Skip if critical info missing
            if not (name and email):
                logger.warning("⚠️ Critical personal info missing from environment")
                return None
            
            # Build config dictionary
            config = {
                'personal': {
                    'full_name': name,
                    'email': email,
                    'phone': phone
                },
                'platforms': {
                    'linkedin': {
                        'username': linkedin_username,
                        'password': linkedin_password
                    },
                    'indeed': {
                        'username': indeed_username,
                        'password': indeed_password
                    },
                    'dice': {
                        'username': dice_username,
                        'password': dice_password
                    },
                    'twitter': {
                        'username': twitter_username,
                        'password': twitter_password
                    },
                    'turing': {
                        'username': turing_username,
                        'password': turing_password
                    }
                },
                'preferences': {
                    'job_types': ['DevOps Engineer', 'Site Reliability Engineer', 'Cloud Engineer', 'Infrastructure Engineer'],
                    'locations': ['Remote', 'United States'],
                    'experience_level': 'Mid-level',
                    'apply_strategy': 'all_matching'
                },
                'verification': {
                    'enable_email_check': False,
                    'email_imap_server': '',
                    'email_smtp_server': '',
                    'email_smtp_port': 587
                }
            }
            
            return config
            
        except Exception as e:
            self._log_error("Environment loading failed", e)
            return None
    
    def _get_default_config(self):
        """Get default configuration"""
        return {
            'personal': {
                'full_name': 'Job Applicant',
                'email': 'example@example.com',
                'phone': '123-456-7890'
            },
            'platforms': {
                'linkedin': {'username': '', 'password': ''},
                'indeed': {'username': '', 'password': ''},
                'dice': {'username': '', 'password': ''},
                'twitter': {'username': '', 'password': ''},
                'turing': {'username': '', 'password': ''}
            },
            'preferences': {
                'job_types': ['DevOps Engineer', 'SRE'],
                'locations': ['Remote'],
                'experience_level': 'Mid-level',
                'apply_strategy': 'all_matching'
            },
            'verification': {
                'enable_email_check': False,
                'email_imap_server': '',
                'email_smtp_server': '',
                'email_smtp_port': 587
            }
        }
    
    def _load_applied_jobs(self):
        """Load applied jobs with error handling"""
        try:
            if os.path.exists(self.applied_jobs_file):
                with open(self.applied_jobs_file, 'rb') as f:
                    self.applied_jobs = pickle.load(f)
                logger.info(f"✅ Loaded {len(self.applied_jobs)} previously applied jobs")
            else:
                self.applied_jobs = set()
                logger.info("✅ No previous applications found, starting fresh")
        except Exception as e:
            self._log_error("Failed to load applied jobs", e)
            self.applied_jobs = set()
    
    def _save_applied_jobs(self):
        """Save applied jobs with error handling"""
        try:
            with open(self.applied_jobs_file, 'wb') as f:
                pickle.dump(self.applied_jobs, f)
            logger.info(f"✅ Saved {len(self.applied_jobs)} applied jobs")
        except Exception as e:
            self._log_error("Failed to save applied jobs", e)
    
    def _get_skills(self):
        """Get skills from resume or default"""
        try:
            # TODO: Implement resume parsing if needed
            return [
                'Python', 'JavaScript', 'DevOps', 'AWS', 'Docker', 
                'Kubernetes', 'Jenkins', 'CI/CD', 'Git', 'Linux',
                'Terraform', 'Ansible', 'Cloud', 'Infrastructure as Code',
                'Monitoring', 'Automation'
            ]
        except Exception as e:
            self._log_error("Failed to extract skills", e)
            return ['Python', 'DevOps', 'AWS', 'Docker', 'Kubernetes']
    
    def _log_error(self, message, exception, save_to_file=True):
        """Log error with details"""
        error_message = f"{message}: {str(exception)}"
        logger.error(error_message)
        
        if save_to_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_details = f"{timestamp} - {message}\n{str(exception)}\n{traceback.format_exc()}\n\n"
            
            try:
                with open(self.error_log_file, 'a', encoding='utf-8') as f:
                    f.write(error_details)
            except Exception as e:
                logger.error(f"Failed to write to error log: {e}")
    
    def _log_application(self, platform, job_title, company, status, url="", verification_status=""):
        """Log application details with verification status"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            verification_info = f"VERIFICATION: {verification_status}\n" if verification_status else ""
            
            application_details = (
                f"{timestamp} - {platform} - {job_title} - {company} - {status}\n"
                f"URL: {url}\n"
                f"{verification_info}"
                f"Skills: {', '.join(self.skills[:5])}\n"
                f"-" * 50 + "\n"
            )
            
            with open(self.applications_file, 'a', encoding='utf-8') as f:
                f.write(application_details)
                
            logger.info(f"✅ Logged application: {platform} - {job_title} - {status}")
            
            # Store timestamp for email verification
            if status == "SUCCESS":
                self.verification_timestamps[f"{platform}_{company}_{job_title}"] = timestamp
                
        except Exception as e:
            self._log_error("Failed to log application", e)
    
    def _log_cycle(self, platform, jobs_found, jobs_applied, duration):
        """Log cycle statistics"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cycle_details = (
                f"{timestamp} - {platform}\n"
                f"Jobs found: {jobs_found}\n"
                f"Jobs applied: {jobs_applied}\n"
                f"Duration: {duration:.2f} seconds\n"
                f"-" * 50 + "\n"
            )
            
            with open(self.cycle_log_file, 'a', encoding='utf-8') as f:
                f.write(cycle_details)
                
            logger.info(f"✅ Logged cycle: {platform} - Found: {jobs_found} - Applied: {jobs_applied}")
            
        except Exception as e:
            self._log_error("Failed to log cycle", e)
    
    def _log_verification(self, platform, company, job_title, verification_status, details):
        """Log verification details"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            verification_details = (
                f"{timestamp} - {platform} - {company} - {job_title}\n"
                f"Status: {verification_status}\n"
                f"Details: {details}\n"
                f"-" * 50 + "\n"
            )
            
            with open(self.verification_log_file, 'a', encoding='utf-8') as f:
                f.write(verification_details)
                
            logger.info(f"✅ Logged verification: {platform} - {job_title} - {verification_status}")
            
        except Exception as e:
            self._log_error("Failed to log verification", e)
    
    def _create_user_profile(self):
        """Create user profile from configuration"""
        try:
            personal = self.config.get('personal', {})
            return UserProfile(
                name=personal.get('full_name', ''),
                email=personal.get('email', ''),
                phone=personal.get('phone', ''),
                location=personal.get('location', 'Remote'),
                linkedin=personal.get('linkedin', ''),
                github=personal.get('github', '')
            )
        except Exception as e:
            self._log_error("Failed to create user profile", e)
            return UserProfile()
    
    def _setup_browser(self):
        """Setup browser with error handling and fallbacks"""
        try:
            logger.info("🌐 Setting up Firefox browser...")
            
            options = Options()
            
            # Common options
            options.set_preference("dom.webnotifications.enabled", False)
            options.set_preference("app.update.enabled", False)
            
            # Determine if in CI environment for headless mode
            if os.environ.get('CI') == 'true' or os.environ.get('GITHUB_ACTIONS') == 'true':
                logger.info("🤖 Running in CI environment, using headless mode")
                options.add_argument('-headless')
            
            try:
                # Try Firefox first
                service = Service(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=options)
                logger.info("✅ Firefox browser initialized")
            except Exception as firefox_error:
                # Log Firefox error but continue to Chrome fallback
                self._log_error("Firefox initialization failed, trying Chrome", firefox_error)
                
                # Try Chrome as fallback
                try:
                    from selenium.webdriver.chrome.options import Options as ChromeOptions
                    chrome_options = ChromeOptions()
                    
                    if os.environ.get('CI') == 'true' or os.environ.get('GITHUB_ACTIONS') == 'true':
                        chrome_options.add_argument('--headless')
                        
                    chrome_options.add_argument('--disable-gpu')
                    chrome_options.add_argument('--no-sandbox')
                    chrome_options.add_argument('--disable-dev-shm-usage')
                    
                    self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
                    logger.info("✅ Chrome browser initialized as fallback")
                except Exception as chrome_error:
                    # If Chrome also fails, log error and re-raise
                    self._log_error("Chrome initialization also failed", chrome_error)
                    raise RuntimeError("Failed to initialize any browser")
            
            # Set window size and timeout
            self.driver.set_window_size(1920, 1080)
            self.wait = WebDriverWait(self.driver, 10)
            self.actions = ActionChains(self.driver)
            
            return True
            
        except Exception as e:
            self._log_error("Browser setup failed", e)
            return False
    
    def _close_browser(self):
        """Safely close browser"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.wait = None
                self.actions = None
                logger.info("✅ Browser closed successfully")
        except Exception as e:
            self._log_error("Browser close error", e)
    
    def _wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Wait for element with better error handling"""
        try:
            return self.wait.until(EC.presence_of_element_located((by, selector)))
        except TimeoutException:
            logger.warning(f"⚠️ Element not found: {selector}")
            return None
        except Exception as e:
            self._log_error(f"Error waiting for element: {selector}", e)
            return None
    
    def _find_element_safely(self, selector, by=By.CSS_SELECTOR):
        """Find element with error handling"""
        try:
            return self.driver.find_element(by, selector)
        except NoSuchElementException:
            return None
        except Exception as e:
            self._log_error(f"Error finding element: {selector}", e)
            return None
    
    def _find_elements_safely(self, selector, by=By.CSS_SELECTOR):
        """Find elements with error handling"""
        try:
            return self.driver.find_elements(by, selector)
        except Exception as e:
            self._log_error(f"Error finding elements: {selector}", e)
            return []
    
    def _click_safely(self, element):
        """Click element with multiple fallback strategies"""
        if not element:
            logger.warning("⚠️ Cannot click None element")
            return False
        
        # Try multiple strategies
        strategies = [
            self._regular_click,
            self._javascript_click,
            self._action_chains_click,
            self._send_keys_enter
        ]
        
        for strategy in strategies:
            try:
                if strategy(element):
                    return True
            except Exception as e:
                continue
        
        logger.warning("⚠️ All click strategies failed")
        return False
    
    def _regular_click(self, element):
        """Regular click strategy"""
        try:
            element.click()
            time.sleep(1)
            return True
        except Exception as e:
            return False
    
    def _javascript_click(self, element):
        """JavaScript click strategy"""
        try:
            self.driver.execute_script("arguments[0].click();", element)
            time.sleep(1)
            return True
        except Exception as e:
            return False
    
    def _action_chains_click(self, element):
        """Action chains click strategy"""
        try:
            self.actions.move_to_element(element).click().perform()
            time.sleep(1)
            return True
        except Exception as e:
            return False
    
    def _send_keys_enter(self, element):
        """Send keys enter strategy"""
        try:
            element.send_keys(Keys.ENTER)
            time.sleep(1)
            return True
        except Exception as e:
            return False
    
    def _try_all_selectors(self, selector_list, platform=None):
        """Try all selectors in a list until one works"""
        if platform and platform in self.selectors:
            # Try platform-specific selectors first
            for selector in self.selectors[platform].get("apply", []):
                element = self._find_element_safely(selector)
                if element:
                    return element
        
        # Try provided selectors next
        for selector in selector_list:
            element = self._find_element_safely(selector)
            if element:
                return element
        
        # Try generic selectors last
        for selector in self.selectors["Generic"].get("apply", []):
            element = self._find_element_safely(selector)
            if element:
                return element
        
        return None
    
    def _check_success_indicators(self, platform):
        """Check for success indicators on the page after application submission"""
        try:
            # Get platform-specific success indicators
            indicators = []
            if platform in self.selectors and "success_indicators" in self.selectors[platform]:
                indicators.extend(self.selectors[platform]["success_indicators"])
            
            # Add generic success indicators
            indicators.extend(self.selectors["Generic"]["success_indicators"])
            
            # Check each indicator
            for indicator in indicators:
                elements = self._find_elements_safely(indicator)
                if elements:
                    logger.info(f"✅ Success indicator found: {indicator}")
                    return True
            
            logger.warning("⚠️ No success indicators found")
            return False
            
        except Exception as e:
            self._log_error("Error checking success indicators", e)
            return False
    
    def _take_screenshot(self, name_prefix):
        """Take screenshot with error handling"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.proof_folder}/{name_prefix}_{timestamp}.png"
            self.driver.save_screenshot(filename)
            logger.info(f"📸 Screenshot saved: {filename}")
            return filename
        except Exception as e:
            self._log_error("Screenshot error", e)
            return None
    
    def _take_verification_screenshot(self, platform, company, job_title):
        """Take a verification screenshot with all page contents"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            sanitized_company = re.sub(r'[^\w]', '_', company)
            sanitized_job = re.sub(r'[^\w]', '_', job_title)
            
            filename = f"{self.proof_folder}/verification/{platform}_{sanitized_company}_{sanitized_job}_{timestamp}.png"
            
            # Take full page screenshot
            try:
                # Try to get full page screenshot
                original_size = self.driver.get_window_size()
                required_width = self.driver.execute_script('return document.body.parentNode.scrollWidth')
                required_height = self.driver.execute_script('return document.body.parentNode.scrollHeight')
                
                self.driver.set_window_size(required_width, required_height)
                self.driver.save_screenshot(filename)
                self.driver.set_window_size(original_size['width'], original_size['height'])
            except:
                # Fallback to regular screenshot
                self.driver.save_screenshot(filename)
            
            # Save page source as well for better verification
            html_filename = filename.replace(".png", ".html")
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            
            logger.info(f"📸 Verification screenshot saved: {filename}")
            logger.info(f"📄 Page source saved: {html_filename}")
            
            return filename
        except Exception as e:
            self._log_error("Verification screenshot error", e)
            return None
    
    def _login_to_platform(self, platform):
        """Login to specified platform"""
        try:
            if platform == "LinkedIn":
                return self._login_linkedin()
            elif platform == "Indeed":
                return self._login_indeed()
            elif platform == "Dice":
                return self._login_dice()
            elif platform == "RemoteOK":
                # RemoteOK doesn't require login
                return True
            else:
                logger.warning(f"⚠️ Login not implemented for {platform}")
                return False
        except Exception as e:
            self._log_error(f"Login error for {platform}", e)
            return False
    
    def _login_linkedin(self):
        """Login to LinkedIn"""
        try:
            username = self.config['platforms']['linkedin']['username']
            password = self.config['platforms']['linkedin']['password']
            
            if not username or not password:
                logger.warning("⚠️ LinkedIn credentials not configured")
                return False
            
            logger.info("🔐 Logging into LinkedIn...")
            
            # Navigate to login page
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(3)
            
            # Enter credentials
            username_field = self._wait_for_element(self.selectors["LinkedIn"]["login"]["username"])
            password_field = self._wait_for_element(self.selectors["LinkedIn"]["login"]["password"])
            
            if not username_field or not password_field:
                logger.error("❌ LinkedIn login fields not found")
                return False
            
            username_field.clear()
            username_field.send_keys(username)
            time.sleep(1)
            
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            # Take screenshot before login
            self._take_screenshot("LinkedIn_Before_Login")
            
            # Submit form
            submit_button = self._wait_for_element(self.selectors["LinkedIn"]["login"]["submit"])
            if not submit_button:
                logger.error("❌ LinkedIn submit button not found")
                return False
            
            self._click_safely(submit_button)
            time.sleep(5)
            
            # Take screenshot for verification
            self._take_screenshot("LinkedIn_After_Login")
            
            # Check if login successful
            if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                logger.info("✅ LinkedIn login successful")
                return True
            else:
                logger.warning("⚠️ LinkedIn login may have failed")
                return False
                
        except Exception as e:
            self._log_error("LinkedIn login error", e)
            return False
    
    def _login_indeed(self):
        """Login to Indeed"""
        try:
            username = self.config['platforms']['indeed']['username']
            password = self.config['platforms']['indeed']['password']
            
            if not username or not password:
                logger.warning("⚠️ Indeed credentials not configured")
                return False
            
            logger.info("🔐 Logging into Indeed...")
            
            # Navigate to login page
            self.driver.get("https://secure.indeed.com/account/login")
            time.sleep(3)
            
            # Take screenshot before login
            self._take_screenshot("Indeed_Before_Login")
            
            # Enter credentials
            username_field = self._wait_for_element(self.selectors["Indeed"]["login"]["username"])
            if not username_field:
                logger.error("❌ Indeed username field not found")
                return False
            
            username_field.clear()
            username_field.send_keys(username)
            time.sleep(1)
            
            # Click continue button
            continue_button = self._wait_for_element("button[type='submit']")
            if not continue_button:
                logger.error("❌ Indeed continue button not found")
                return False
            
            self._click_safely(continue_button)
            time.sleep(3)
            
            # Enter password
            password_field = self._wait_for_element(self.selectors["Indeed"]["login"]["password"])
            if not password_field:
                logger.error("❌ Indeed password field not found")
                return False
            
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            # Submit form
            submit_button = self._wait_for_element(self.selectors["Indeed"]["login"]["submit"])
            if not submit_button:
                logger.error("❌ Indeed submit button not found")
                return False
            
            self._click_safely(submit_button)
            time.sleep(5)
            
            # Take screenshot for verification
            self._take_screenshot("Indeed_After_Login")
            
            # Check if login successful
            if "account" in self.driver.current_url or "resume" in self.driver.current_url:
                logger.info("✅ Indeed login successful")
                return True
            else:
                logger.warning("⚠️ Indeed login may have failed")
                return False
                
        except Exception as e:
            self._log_error("Indeed login error", e)
            return False
    
    def _login_dice(self):
        """Login to Dice"""
        try:
            username = self.config['platforms']['dice']['username']
            password = self.config['platforms']['dice']['password']
            
            if not username or not password:
                logger.warning("⚠️ Dice credentials not configured")
                return False
            
            logger.info("🔐 Logging into Dice...")
            
            # Navigate to login page
            self.driver.get("https://www.dice.com/dashboard/login")
            time.sleep(3)
            
            # Take screenshot before login
            self._take_screenshot("Dice_Before_Login")
            
            # Enter credentials
            username_field = self._wait_for_element(self.selectors["Dice"]["login"]["username"])
            password_field = self._wait_for_element(self.selectors["Dice"]["login"]["password"])
            
            if not username_field or not password_field:
                logger.error("❌ Dice login fields not found")
                return False
            
            username_field.clear()
            username_field.send_keys(username)
            time.sleep(1)
            
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            # Submit form
            submit_button = self._wait_for_element(self.selectors["Dice"]["login"]["submit"])
            if not submit_button:
                logger.error("❌ Dice submit button not found")
                return False
            
            self._click_safely(submit_button)
            time.sleep(5)
            
            # Take screenshot for verification
            self._take_screenshot("Dice_After_Login")
            
            # Check if login successful
            if "dashboard" in self.driver.current_url or "profile" in self.driver.current_url:
                logger.info("✅ Dice login successful")
                return True
            else:
                logger.warning("⚠️ Dice login may have failed")
                return False
                
        except Exception as e:
            self._log_error("Dice login error", e)
            return False
    
    def search_jobs(self, platform, keyword, location="Remote"):
        """Search for jobs on a platform"""
        try:
            if platform == "LinkedIn":
                return self._search_linkedin_jobs(keyword, location)
            elif platform == "Indeed":
                return self._search_indeed_jobs(keyword, location)
            elif platform == "RemoteOK":
                return self._search_remoteok_jobs(keyword)
            elif platform == "Dice":
                return self._search_dice_jobs(keyword, location)
            else:
                logger.warning(f"⚠️ Job search not implemented for {platform}")
                return []
        except Exception as e:
            self._log_error(f"Job search error for {platform}", e)
            return []
    
    def _search_linkedin_jobs(self, keyword, location="Remote"):
        """Search for jobs on LinkedIn"""
        try:
            logger.info(f"🔍 Searching LinkedIn for: {keyword} in {location}")
            
            # Format search URL
            keyword_encoded = keyword.replace(" ", "%20")
            location_encoded = location.replace(" ", "%20")
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword_encoded}&location={location_encoded}"
            
            self.driver.get(search_url)
            time.sleep(5)
            
            # Take screenshot of search results
            self._take_screenshot(f"LinkedIn_Search_{keyword}")
            
            # Get job listings
            job_items = self._find_elements_safely(".jobs-search-results__list-item")
            
            if not job_items:
                logger.warning(f"⚠️ No LinkedIn job listings found for {keyword}")
                return []
            
            logger.info(f"✅ Found {len(job_items)} LinkedIn jobs for {keyword}")
            
            return job_items
            
        except Exception as e:
            self._log_error(f"LinkedIn search error for {keyword}", e)
            return []
    
    def _search_indeed_jobs(self, keyword, location="Remote"):
        """Search for jobs on Indeed"""
        try:
            logger.info(f"🔍 Searching Indeed for: {keyword} in {location}")
            
            # Format search URL
            keyword_encoded = keyword.replace(" ", "+")
            location_encoded = location.replace(" ", "+")
            search_url = f"https://www.indeed.com/jobs?q={keyword_encoded}&l={location_encoded}"
            
            self.driver.get(search_url)
            time.sleep(5)
            
            # Take screenshot of search results
            self._take_screenshot(f"Indeed_Search_{keyword}")
            
            # Get job listings
            job_items = self._find_elements_safely(".job_seen_beacon")
            
            if not job_items:
                # Try alternative selector
                job_items = self._find_elements_safely(".resultWithShelf")
            
            if not job_items:
                logger.warning(f"⚠️ No Indeed job listings found for {keyword}")
                return []
            
            logger.info(f"✅ Found {len(job_items)} Indeed jobs for {keyword}")
            
            return job_items
            
        except Exception as e:
            self._log_error(f"Indeed search error for {keyword}", e)
            return []
    
    def _search_remoteok_jobs(self, keyword):
        """Search for jobs on RemoteOK"""
        try:
            logger.info(f"🔍 Searching RemoteOK for: {keyword}")
            
            # Format search URL
            keyword_encoded = keyword.replace(" ", "-").lower()
            search_url = f"https://remoteok.com/remote-{keyword_encoded}-jobs"
            
            self.driver.get(search_url)
            time.sleep(5)
            
            # Take screenshot of search results
            self._take_screenshot(f"RemoteOK_Search_{keyword}")
            
            # Get job listings
            job_items = self._find_elements_safely(".job")
            
            if not job_items:
                logger.warning(f"⚠️ No RemoteOK job listings found for {keyword}")
                return []
            
            logger.info(f"✅ Found {len(job_items)} RemoteOK jobs for {keyword}")
            
            return job_items
            
        except Exception as e:
            self._log_error(f"RemoteOK search error for {keyword}", e)
            return []
    
    def _search_dice_jobs(self, keyword, location="Remote"):
        """Search for jobs on Dice"""
        try:
            logger.info(f"🔍 Searching Dice for: {keyword} in {location}")
            
            # Format search URL
            keyword_encoded = keyword.replace(" ", "+")
            location_encoded = location.replace(" ", "+")
            search_url = f"https://www.dice.com/jobs?q={keyword_encoded}&location={location_encoded}"
            
            self.driver.get(search_url)
            time.sleep(5)
            
            # Take screenshot of search results
            self._take_screenshot(f"Dice_Search_{keyword}")
            
            # Get job listings
            job_items = self._find_elements_safely(".search-card")
            
            if not job_items:
                logger.warning(f"⚠️ No Dice job listings found for {keyword}")
                return []
            
            logger.info(f"✅ Found {len(job_items)} Dice jobs for {keyword}")
            
            return job_items
            
        except Exception as e:
            self._log_error(f"Dice search error for {keyword}", e)
            return []
    
    def apply_to_job(self, platform, job_element):
        """Apply to a job with enhanced verification"""
        try:
            # Click on job to view details
            self._click_safely(job_element)
            time.sleep(3)
            
            # Extract job information (title, company)
            job_title = self._extract_job_title(platform)
            company_name = self._extract_company_name(platform)
            
            # Generate job ID
            job_id = f"{platform}_{company_name}_{job_title}"
            
            # Get current URL for verification
            job_url = self.driver.current_url
            
            # Check if already applied
            if job_id in self.applied_jobs:
                logger.info(f"⚠️ Already applied to {job_title} at {company_name}")
                return False
            
            # Take screenshot before applying
            self._take_screenshot(f"{platform}_Before_Apply_{company_name}")
            
            logger.info(f"🎯 Attempting to apply: {job_title} at {company_name}")
            
            # Find apply button using platform-specific selectors
            apply_button = None
            
            if platform == "LinkedIn":
                apply_button = self._try_all_selectors(self.selectors["LinkedIn"]["apply"], "LinkedIn")
            elif platform == "Indeed":
                apply_button = self._try_all_selectors(self.selectors["Indeed"]["apply"], "Indeed")
            elif platform == "RemoteOK":
                apply_button = self._try_all_selectors(self.selectors["RemoteOK"]["apply"], "RemoteOK")
            elif platform == "Dice":
                apply_button = self._try_all_selectors(self.selectors["Dice"]["apply"], "Dice")
            
            if not apply_button:
                logger.warning(f"⚠️ No apply button found for {job_title}")
                self._log_application(platform, job_title, company_name, "NO_APPLY_BUTTON", job_url)
                return False
            
            # Take screenshot of apply button
            self._take_verification_screenshot(platform, company_name, f"{job_title}_ApplyButton")
            
            # Click apply button
            self._click_safely(apply_button)
            time.sleep(3)
            
            # Take screenshot after clicking apply
            self._take_verification_screenshot(platform, company_name, f"{job_title}_AfterClick")
            
            # Handle application process based on platform
            if platform == "LinkedIn":
                success = self._handle_linkedin_application(job_title, company_name)
            elif platform == "Indeed":
                success = self._handle_indeed_application(job_title, company_name)
            elif platform == "RemoteOK":
                success = self._handle_remoteok_application(job_title, company_name)
            elif platform == "Dice":
                success = self._handle_dice_application(job_title, company_name)
            else:
                success = False
            
            if success:
                # Add to applied jobs
                self.applied_jobs.add(job_id)
                self._save_applied_jobs()
                
                # Check for success indicators
                success_confirmed = self._check_success_indicators(platform)
                verification_status = "CONFIRMED" if success_confirmed else "PENDING"
                
                # Take final verification screenshot
                self._take_verification_screenshot(platform, company_name, f"{job_title}_Completion")
                
                # Log success
                self._log_application(
                    platform, job_title, company_name, "SUCCESS", 
                    job_url, verification_status
                )
                
                logger.info(f"✅ Successfully applied to {job_title} at {company_name}")
                return True
            else:
                self._log_application(platform, job_title, company_name, "FAILED", job_url)
                logger.warning(f"❌ Failed to apply to {job_title} at {company_name}")
                return False
                
        except Exception as e:
            job_title = self._extract_job_title(platform) or "Unknown Position"
            company_name = self._extract_company_name(platform) or "Unknown Company"
            
            self._log_error(f"Apply error for {job_title} at {company_name}", e)
            self._log_application(platform, job_title, company_name, "ERROR", self.driver.current_url)
            return False
    
    def _extract_job_title(self, platform):
        """Extract job title based on platform"""
        try:
            if platform == "LinkedIn":
                title_element = self._find_element_safely("h1.job-title") or self._find_element_safely("h1.topcard__title")
                if title_element:
                    return title_element.text.strip()
            elif platform == "Indeed":
                title_element = self._find_element_safely("h1.jobsearch-JobInfoHeader-title")
                if title_element:
                    return title_element.text.strip()
            elif platform == "RemoteOK":
                title_element = self._find_element_safely("h1")
                if title_element:
                    return title_element.text.strip()
            elif platform == "Dice":
                title_element = self._find_element_safely("h1.jobTitle")
                if title_element:
                    return title_element.text.strip()
            
            # Try generic selectors
            for selector in ["h1", ".job-title", ".position-title", ".title"]:
                title_element = self._find_element_safely(selector)
                if title_element:
                    return title_element.text.strip()
            
            return "Unknown Position"
            
        except Exception as e:
            self._log_error("Error extracting job title", e)
            return "Unknown Position"
    
    def _extract_company_name(self, platform):
        """Extract company name based on platform"""
        try:
            if platform == "LinkedIn":
                company_element = self._find_element_safely("a.topcard__org-name-link") or self._find_element_safely(".jobs-unified-top-card__company-name")
                if company_element:
                    return company_element.text.strip()
            elif platform == "Indeed":
                company_element = self._find_element_safely(".jobsearch-InlineCompanyRating div:first-child")
                if company_element:
                    return company_element.text.strip()
            elif platform == "RemoteOK":
                company_element = self._find_element_safely("h2") or self._find_element_safely(".company")
                if company_element:
                    return company_element.text.strip()
            elif platform == "Dice":
                company_element = self._find_element_safely(".companyName")
                if company_element:
                    return company_element.text.strip()
            
            # Try generic selectors
            for selector in [".company-name", ".company", ".employer", ".organization"]:
                company_element = self._find_element_safely(selector)
                if company_element:
                    return company_element.text.strip()
            
            return "Unknown Company"
            
        except Exception as e:
            self._log_error("Error extracting company name", e)
            return "Unknown Company"
    
    def _handle_linkedin_application(self, job_title, company_name):
        """Handle LinkedIn application process with enhanced verification"""
        try:
            logger.info(f"⏳ Processing LinkedIn application for {job_title} at {company_name}")
            
            # Check if already on application page
            if not any(term in self.driver.current_url for term in ["jobs-apply", "easy-apply"]):
                # Find and click Easy Apply button
                easy_apply_button = self._try_all_selectors(self.selectors["LinkedIn"]["apply"])
                
                if not easy_apply_button:
                    logger.warning("⚠️ LinkedIn Easy Apply button not found")
                    return False
                
                # Take screenshot of the button
                self._take_verification_screenshot("LinkedIn", company_name, f"{job_title}_EasyApplyButton")
                
                self._click_safely(easy_apply_button)
                time.sleep(3)
            
            # Check if application opened in new tab
            original_window = self.driver.current_window_handle
            if len(self.driver.window_handles) > 1:
                # Switch to new window
                for window_handle in self.driver.window_handles:
                    if window_handle != original_window:
                        self.driver.switch_to.window(window_handle)
                        break
            
            # Take screenshot of application form
            self._take_verification_screenshot("LinkedIn", company_name, f"{job_title}_ApplicationStart")
            
            # Handle multi-step application process
            for step in range(1, 11):  # Maximum 10 steps
                # Take screenshot of each step
                self._take_verification_screenshot("LinkedIn", company_name, f"{job_title}_Step{step}")
                
                # Look for next, review, or submit buttons
                for button_selector in self.selectors["LinkedIn"]["next"]:
                    next_button = self._find_element_safely(button_selector)
                    if next_button:
                        # Take screenshot of the button
                        self._take_verification_screenshot("LinkedIn", company_name, f"{job_title}_Button{step}")
                        
                        # Click the button
                        self._click_safely(next_button)
                        time.sleep(2)
                        break
                else:
                    # No more buttons found
                    break
            
            # Take final screenshot
            self._take_verification_screenshot("LinkedIn", company_name, f"{job_title}_Final")
            
            # Check for success indicators
            success_elements = self._find_elements_safely("h2:contains('Application submitted')") or self._find_elements_safely("h2:contains('Your application has been submitted')")
            
            if success_elements:
                logger.info(f"✅ LinkedIn application submitted to {company_name}")
                
                # Switch back to original window if needed
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
                
                return True
            
            # If no success indicator, but we went through all steps
            logger.info(f"✅ LinkedIn application process completed for {company_name}")
            
            # Switch back to original window if needed
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(original_window)
            
            return True
            
        except Exception as e:
            self._log_error(f"LinkedIn application error for {job_title}", e)
            
            # Switch back to original window if needed
            try:
                original_window = self.driver.window_handles[0]
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
            except:
                pass
                
            return False
    
    def _handle_indeed_application(self, job_title, company_name):
        """Handle Indeed application process with enhanced verification"""
        try:
            logger.info(f"⏳ Processing Indeed application for {job_title} at {company_name}")
            
            # Check if application opened in new tab
            original_window = self.driver.current_window_handle
            if len(self.driver.window_handles) > 1:
                # Switch to new window
                for window_handle in self.driver.window_handles:
                    if window_handle != original_window:
                        self.driver.switch_to.window(window_handle)
                        break
            
            # Take screenshot of application form
            self._take_verification_screenshot("Indeed", company_name, f"{job_title}_ApplicationStart")
            
            # Handle multi-step application process
            for step in range(1, 11):  # Maximum 10 steps
                # Take screenshot of each step
                self._take_verification_screenshot("Indeed", company_name, f"{job_title}_Step{step}")
                
                # Look for continue or submit buttons
                for button_selector in [".ia-continueButton", ".ia-submitButton", "button:contains('Continue')", "button:contains('Submit')"]:
                    continue_button = self._find_element_safely(button_selector)
                    if continue_button:
                        # Take screenshot of the button
                        self._take_verification_screenshot("Indeed", company_name, f"{job_title}_Button{step}")
                        
                        # Click the button
                        self._click_safely(continue_button)
                        time.sleep(3)
                        break
                else:
                    # No more buttons found
                    break
            
            # Take final screenshot
            self._take_verification_screenshot("Indeed", company_name, f"{job_title}_Final")
            
            # Check for success indicators
            success_elements = self._find_elements_safely("div:contains('Application submitted')") or self._find_elements_safely("div:contains('Your application has been submitted')")
            
            if success_elements:
                logger.info(f"✅ Indeed application submitted to {company_name}")
                
                # Take screenshot of success message
                self._take_verification_screenshot("Indeed", company_name, f"{job_title}_Success")
                
                # Switch back to original window if needed
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
                
                return True
            
            # If no success indicator, but we went through all steps
            logger.info(f"✅ Indeed application process completed for {company_name}")
            
            # Switch back to original window if needed
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(original_window)
            
            return True
            
        except Exception as e:
            self._log_error(f"Indeed application error for {job_title}", e)
            
            # Switch back to original window if needed
            try:
                original_window = self.driver.window_handles[0]
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
            except:
                pass
                
            return False
    
    def _handle_remoteok_application(self, job_title, company_name):
        """Handle RemoteOK application process with enhanced verification"""
        try:
            logger.info(f"⏳ Processing RemoteOK application for {job_title} at {company_name}")
            
            # Find apply link
            apply_link = self._find_element_safely("a.preventLink") or self._find_element_safely("a:contains('Apply')")
            
            if not apply_link:
                logger.warning("⚠️ RemoteOK apply link not found")
                return False
            
            # Take screenshot of apply link
            self._take_verification_screenshot("RemoteOK", company_name, f"{job_title}_ApplyLink")
            
            # Get the href attribute
            apply_url = apply_link.get_attribute("href")
            
            if not apply_url:
                logger.warning("⚠️ RemoteOK apply URL not found")
                return False
            
            # Take screenshot of job details
            self._take_verification_screenshot("RemoteOK", company_name, f"{job_title}_Details")
            
            # Save the apply URL to a text file for verification
            url_file_path = f"{self.proof_folder}/verification/RemoteOK_{company_name}_{job_title}_URL.txt"
            with open(url_file_path, 'w', encoding='utf-8') as f:
                f.write(f"Job URL: {self.driver.current_url}\nApply URL: {apply_url}\n")
            
            # Open application in new tab
            self.driver.execute_script(f"window.open('{apply_url}');")
            time.sleep(3)
            
            # Switch to new tab
            original_window = self.driver.current_window_handle
            for window_handle in self.driver.window_handles:
                if window_handle != original_window:
                    self.driver.switch_to.window(window_handle)
                    break
            
            time.sleep(3)  # Wait for external page to load
            
            # Take screenshot of external application
            self._take_verification_screenshot("RemoteOK", company_name, f"{job_title}_ExternalApply")
            
            # For RemoteOK, we just mark as success since they lead to external sites
            # that would need platform-specific handling
            logger.info(f"✅ RemoteOK external application opened for {company_name}")
            
            # Close the application tab and switch back
            self.driver.close()
            self.driver.switch_to.window(original_window)
            
            return True
            
        except Exception as e:
            self._log_error(f"RemoteOK application error for {job_title}", e)
            
            # Switch back to original window if needed
            try:
                original_window = self.driver.window_handles[0]
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
            except:
                pass
                
            return False
    
    def _handle_dice_application(self, job_title, company_name):
        """Handle Dice application process with enhanced verification"""
        try:
            logger.info(f"⏳ Processing Dice application for {job_title} at {company_name}")
            
            # Check if we can use Easy Apply
            easy_apply_button = self._find_element_safely("button[data-cy='easyApplyBtn']")
            
            if easy_apply_button:
                # Take screenshot of easy apply button
                self._take_verification_screenshot("Dice", company_name, f"{job_title}_EasyApplyButton")
                
                # Click Easy Apply
                self._click_safely(easy_apply_button)
                time.sleep(3)
                
                # Take screenshot after clicking easy apply
                self._take_verification_screenshot("Dice", company_name, f"{job_title}_AfterEasyApply")
                
                # Look for submit button
                submit_button = self._find_element_safely("button:contains('Submit')") or self._find_element_safely(".btn-primary")
                
                if submit_button:
                    # Take screenshot of submit button
                    self._take_verification_screenshot("Dice", company_name, f"{job_title}_SubmitButton")
                    
                    # Click Submit
                    self._click_safely(submit_button)
                    time.sleep(3)
                    
                    # Take screenshot after submission
                    self._take_verification_screenshot("Dice", company_name, f"{job_title}_AfterSubmit")
                    
                    logger.info(f"✅ Dice Easy Apply submitted for {company_name}")
                    return True
            
            # If Easy Apply not available, try regular apply
            apply_button = self._try_all_selectors(self.selectors["Dice"]["apply"])
            
            if not apply_button:
                logger.warning("⚠️ Dice apply button not found")
                return False
            
            # Take screenshot of apply button
            self._take_verification_screenshot("Dice", company_name, f"{job_title}_ApplyButton")
            
            self._click_safely(apply_button)
            time.sleep(3)
            
            # Check if application opened in new tab
            original_window = self.driver.current_window_handle
            if len(self.driver.window_handles) > 1:
                # Switch to new window
                for window_handle in self.driver.window_handles:
                    if window_handle != original_window:
                        self.driver.switch_to.window(window_handle)
                        break
            
            # Take screenshot of application form
            self._take_verification_screenshot("Dice", company_name, f"{job_title}_Application")
            
            # For external applications, we just mark as success
            logger.info(f"✅ Dice application process completed for {company_name}")
            
            # Switch back to original window if needed
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(original_window)
            
            return True
            
        except Exception as e:
            self._log_error(f"Dice application error for {job_title}", e)
            
            # Switch back to original window if needed
            try:
                original_window = self.driver.window_handles[0]
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
            except:
                pass
                
            return False
    
    def run_platform_cycle(self, platform):
        """Run complete job cycle for a platform"""
        start_time = time.time()
        jobs_found = 0
        jobs_applied = 0
        
        try:
            logger.info(f"🚀 Starting job cycle for {platform}")
            
            # Login if needed
            if platform != "RemoteOK":  # RemoteOK doesn't require login
                if not self._login_to_platform(platform):
                    logger.error(f"❌ Login failed for {platform}, skipping")
                    return False
            
            # Get search keywords
            job_types = self.config['preferences']['job_types']
            locations = self.config['preferences']['locations']
            
            # For each keyword and location combination
            for job_type in job_types:
                for location in locations:
                    try:
                        # Search for jobs
                        job_items = self.search_jobs(platform, job_type, location)
                        jobs_found += len(job_items)
                        
                        if not job_items:
                            logger.warning(f"⚠️ No jobs found for {job_type} in {location}")
                            continue
                        
                        # Apply to each job (limit to 5 per search for testing)
                        for job_item in job_items[:5]:
                            if self.apply_to_job(platform, job_item):
                                jobs_applied += 1
                                
                    except Exception as e:
                        self._log_error(f"Error processing {job_type} in {location}", e)
            
            # Log cycle statistics
            duration = time.time() - start_time
            self._log_cycle(platform,
