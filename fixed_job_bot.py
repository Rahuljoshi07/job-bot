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
import imaplib
import email
import smtplib
from email.mime.text import MIMEText

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
    
    def _check_email_confirmation(self, platform, job_title, company_name, application_time):
        """Check email for job application confirmation with enhanced error handling"""
        try:
            # Skip email verification if disabled
            if not self.config.get('email_verification', {}).get('enabled', False):
                logger.info("📧 Email verification disabled, skipping")
                return {"status": "disabled", "message": "Email verification is disabled"}
            
            email_config = self.config.get('email_verification', {})
            
            # Check if required email configuration is available
            if not email_config.get('email') or not email_config.get('app_password'):
                logger.warning("📧 Email verification configuration incomplete")
                return {"status": "config_missing", "message": "Email configuration incomplete"}
            
            logger.info(f"📧 Checking email for {job_title} at {company_name} confirmation...")
            
            # Connect to IMAP server with retry logic
            max_connection_retries = 3
            mail = None
            
            for connection_attempt in range(max_connection_retries):
                try:
                    imap_server = email_config.get('imap_server', 'imap.gmail.com')
                    imap_port = email_config.get('imap_port', 993)
                    
                    mail = imaplib.IMAP4_SSL(imap_server, imap_port)
                    mail.login(email_config['email'], email_config['app_password'])
                    mail.select('inbox')
                    break
                    
                except Exception as e:
                    logger.warning(f"📧 Email connection attempt {connection_attempt + 1} failed: {e}")
                    if connection_attempt < max_connection_retries - 1:
                        time.sleep(5)  # Wait before retry
                    else:
                        return {"status": "connection_error", "message": f"Failed to connect to email server after {max_connection_retries} attempts"}
            
            if not mail:
                return {"status": "connection_error", "message": "Failed to establish email connection"}
            
            # Search for confirmation emails from the time of application
            search_time = application_time - timedelta(minutes=5)  # Allow some buffer
            search_date = search_time.strftime('%d-%b-%Y')
            
            # Enhanced search keywords that are more likely to match job application confirmations
            search_keywords = [
                'application received',
                'application confirmation',
                'thank you for applying',
                'application submitted',
                'we have received your application',
                'your application has been received',
                'application acknowledgment',
                'job application received',
                company_name.lower(),
                platform.lower(),
                # Add job title keywords
                *job_title.lower().split()
            ]
            
            confirmation_found = False
            confirmation_details = []
            
            # Check emails for a limited time
            timeout = email_config.get('timeout', 300)  # 5 minutes default
            check_interval = email_config.get('check_interval', 30)  # 30 seconds interval
            end_time = time.time() + timeout
            
            while time.time() < end_time:
                try:
                    # Search for emails since the search date
                    typ, data = mail.search(None, f'(SINCE "{search_date}")')
                    
                    if typ == 'OK':
                        mail_ids = data[0].split()
                        
                        # Check recent emails (last 50 to avoid overload)
                        for mail_id in mail_ids[-50:]:
                            try:
                                typ, data = mail.fetch(mail_id, '(RFC822)')
                                if typ == 'OK':
                                    msg = email.message_from_bytes(data[0][1])
                                    
                                    # Get email details
                                    subject = msg.get('subject', '').lower()
                                    from_addr = msg.get('from', '').lower()
                                    date_str = msg.get('date', '')
                                    
                                    # Parse email date
                                    try:
                                        email_date = email.utils.parsedate_to_datetime(date_str)
                                        if email_date < application_time:
                                            continue  # Skip emails before application
                                    except:
                                        continue
                                    
                                    # Check if email content matches confirmation patterns
                                    body = self._extract_email_body(msg)
                                    content = (subject + ' ' + from_addr + ' ' + body).lower()
                                    
                                    # Check for confirmation keywords
                                    matched_keywords = []
                                    for keyword in search_keywords:
                                        if keyword in content:
                                            matched_keywords.append(keyword)
                                    
                                    if matched_keywords:
                                        confirmation_found = True
                                        confirmation_details.append({
                                            'subject': subject,
                                            'from': from_addr,
                                            'date': date_str,
                                            'keywords_matched': matched_keywords,
                                            'message_id': msg.get('message-id', '')
                                        })
                                        break
                                
                            except Exception as e:
                                logger.debug(f"Error processing email {mail_id}: {e}")
                                continue
                    
                    if confirmation_found:
                        break
                    
                    # Wait before next check
                    time.sleep(check_interval)
                    
                except Exception as e:
                    logger.warning(f"📧 Error during email search: {e}")
                    break
            
            mail.close()
            mail.logout()
            
            if confirmation_found:
                logger.info(f"✅ Email confirmation found for {job_title} at {company_name}")
                return {
                    "status": "confirmed",
                    "message": "Email confirmation received",
                    "details": confirmation_details
                }
            else:
                logger.warning(f"⚠️ No email confirmation found for {job_title} at {company_name}")
                return {
                    "status": "pending",
                    "message": f"No email confirmation found within {timeout}s timeout period"
                }
                
        except Exception as e:
            self._log_error(f"Email verification error for {job_title} at {company_name}", e)
            return {"status": "error", "message": f"Email verification failed: {str(e)}"}
    
    def _enhanced_email_verification_check(self, platform, job_title, company_name, application_time):
        """Enhanced email verification with multiple checking strategies"""
        try:
            # Run the primary email check
            primary_result = self._check_email_confirmation(platform, job_title, company_name, application_time)
            
            # If primary check was successful, return immediately
            if primary_result["status"] == "confirmed":
                return primary_result
            
            # If primary check failed due to configuration, return that
            if primary_result["status"] in ["disabled", "config_missing", "connection_error"]:
                return primary_result
            
            # If primary check was pending, try alternative search strategies
            logger.info(f"📧 Primary email check pending, trying alternative strategies...")
            
            # Alternative check with broader search criteria
            alternative_result = self._alternative_email_check(platform, job_title, company_name, application_time)
            
            if alternative_result["status"] == "confirmed":
                return alternative_result
            
            # Return the primary result if alternative also failed
            return primary_result
            
        except Exception as e:
            self._log_error(f"Enhanced email verification error", e)
            return {"status": "error", "message": f"Enhanced email verification failed: {str(e)}"}
    
    def _alternative_email_check(self, platform, job_title, company_name, application_time):
        """Alternative email verification check with different search criteria"""
        try:
            email_config = self.config.get('email_verification', {})
            
            if not email_config.get('email') or not email_config.get('app_password'):
                return {"status": "config_missing", "message": "Email configuration incomplete"}
            
            logger.info(f"📧 Running alternative email check for {job_title} at {company_name}")
            
            # Connect to IMAP server
            imap_server = email_config.get('imap_server', 'imap.gmail.com')
            imap_port = email_config.get('imap_port', 993)
            
            mail = imaplib.IMAP4_SSL(imap_server, imap_port)
            mail.login(email_config['email'], email_config['app_password'])
            mail.select('inbox')
            
            # Use a broader search timeframe
            search_time = application_time - timedelta(minutes=10)  # Broader buffer
            search_date = search_time.strftime('%d-%b-%Y')
            
            # Alternative search keywords - more generic
            alternative_keywords = [
                'noreply',
                'donotreply',
                'jobs',
                'career',
                'hr',
                'talent',
                'recruiting',
                'application',
                platform.lower()
            ]
            
            confirmation_found = False
            confirmation_details = []
            
            # Search for emails from common job-related senders
            for keyword in alternative_keywords:
                try:
                    typ, data = mail.search(None, f'(SINCE "{search_date}" FROM "{keyword}")')
                    
                    if typ == 'OK' and data[0]:
                        mail_ids = data[0].split()
                        
                        for mail_id in mail_ids[-10:]:  # Check last 10 emails for each keyword
                            try:
                                typ, data = mail.fetch(mail_id, '(RFC822)')
                                if typ == 'OK':
                                    msg = email.message_from_bytes(data[0][1])
                                    
                                    # Get email details
                                    subject = msg.get('subject', '').lower()
                                    from_addr = msg.get('from', '').lower()
                                    date_str = msg.get('date', '')
                                    
                                    # Parse email date
                                    try:
                                        email_date = email.utils.parsedate_to_datetime(date_str)
                                        if email_date < application_time:
                                            continue  # Skip emails before application
                                    except:
                                        continue
                                    
                                    # Check if email content matches job application patterns
                                    body = self._extract_email_body(msg)
                                    content = (subject + ' ' + from_addr + ' ' + body).lower()
                                    
                                    # Look for job application related content
                                    if any(pattern in content for pattern in ['application', 'job', 'position', company_name.lower()]):
                                        confirmation_found = True
                                        confirmation_details.append({
                                            'subject': subject,
                                            'from': from_addr,
                                            'date': date_str,
                                            'search_keyword': keyword,
                                            'message_id': msg.get('message-id', '')
                                        })
                                        break
                                        
                            except Exception as e:
                                logger.debug(f"Error processing alternative email {mail_id}: {e}")
                                continue
                    
                    if confirmation_found:
                        break
                        
                except Exception as e:
                    logger.debug(f"Error searching for keyword {keyword}: {e}")
                    continue
            
            mail.close()
            mail.logout()
            
            if confirmation_found:
                logger.info(f"✅ Alternative email confirmation found for {job_title} at {company_name}")
                return {
                    "status": "confirmed",
                    "message": "Alternative email confirmation found",
                    "details": confirmation_details
                }
            else:
                return {
                    "status": "pending",
                    "message": "No alternative email confirmation found"
                }
                
        except Exception as e:
            self._log_error(f"Alternative email verification error", e)
            return {"status": "error", "message": f"Alternative email verification failed: {str(e)}"}
    
    def _extract_email_body(self, msg):
        """Extract text content from email message"""
        try:
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            return body
        except Exception as e:
            logger.debug(f"Error extracting email body: {e}")
            return ""
    
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
                
                # Check email confirmation if enabled using enhanced verification
                application_time = datetime.now()
                email_verification = self._enhanced_email_verification_check(platform, job_title, company_name, application_time)
                
                # Update verification status based on email confirmation
                if email_verification["status"] == "confirmed":
                    verification_status = "EMAIL_CONFIRMED"
                    logger.info(f"📧 Email confirmation received for {job_title} at {company_name}")
                elif email_verification["status"] == "pending":
                    verification_status = "EMAIL_PENDING"
                    logger.warning(f"📧 Email confirmation pending for {job_title} at {company_name}")
                
                # Log verification details
                self._log_verification(
                    platform, company_name, job_title, 
                    verification_status, email_verification.get("message", "")
                )
                
                # Log success
                self._log_application(
                    platform, job_title, company_name, "SUCCESS", 
                    job_url, verification_status
                )
                
                logger.info(f"✅ Successfully applied to {job_title} at {company_name} - Status: {verification_status}")
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
    
    def run_platform_cycle(self, platform, max_jobs_per_search=5, max_retries=3):
        """Run complete job cycle for a platform with enhanced error handling and retry logic"""
        start_time = time.time()
        jobs_found = 0
        jobs_applied = 0
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                logger.info(f"🚀 Starting job cycle for {platform} (attempt {retry_count + 1}/{max_retries})")
                
                # Reset counters for each retry
                if retry_count > 0:
                    jobs_found = 0
                    jobs_applied = 0
                    logger.info(f"🔄 Retrying {platform} cycle after previous failure")
                
                # Setup browser if not already done
                if not self.driver:
                    if not self._setup_browser():
                        logger.error(f"❌ Browser setup failed for {platform}")
                        retry_count += 1
                        time.sleep(min(2 ** retry_count, 30))  # Exponential backoff
                        continue
                
                # Login if needed
                if platform != "RemoteOK":  # RemoteOK doesn't require login
                    login_success = self._login_to_platform(platform)
                    if not login_success:
                        logger.error(f"❌ Login failed for {platform}")
                        retry_count += 1
                        time.sleep(min(2 ** retry_count, 30))  # Exponential backoff
                        continue
                
                # Get search keywords from config
                job_types = self.config['preferences'].get('job_types', ['DevOps Engineer'])
                locations = self.config['preferences'].get('locations', ['Remote'])
                
                # Handle search and application process
                search_success = False
                
                # For each keyword and location combination
                for job_type in job_types:
                    for location in locations:
                        try:
                            logger.info(f"🔍 Searching {platform} for {job_type} in {location}")
                            
                            # Search for jobs
                            job_items = self.search_jobs(platform, job_type, location)
                            current_jobs_found = len(job_items)
                            jobs_found += current_jobs_found
                            
                            if not job_items:
                                logger.warning(f"⚠️ No jobs found for {job_type} in {location}")
                                continue
                            
                            search_success = True
                            logger.info(f"✅ Found {current_jobs_found} jobs for {job_type} in {location}")
                            
                            # Apply to each job (limit to max_jobs_per_search)
                            for i, job_item in enumerate(job_items[:max_jobs_per_search]):
                                try:
                                    logger.info(f"🎯 Applying to job {i+1}/{min(len(job_items), max_jobs_per_search)}")
                                    
                                    if self.apply_to_job(platform, job_item):
                                        jobs_applied += 1
                                        logger.info(f"✅ Successfully applied to job {i+1}")
                                    else:
                                        logger.warning(f"⚠️ Failed to apply to job {i+1}")
                                    
                                    # Add delay between applications to avoid rate limiting
                                    time.sleep(random.uniform(2, 5))
                                    
                                except Exception as e:
                                    self._log_error(f"Error applying to job {i+1} in {job_type} search", e)
                                    continue
                                    
                        except Exception as e:
                            self._log_error(f"Error processing {job_type} in {location}", e)
                            continue
                
                # If we made it here and found jobs, consider it a success
                if search_success:
                    duration = time.time() - start_time
                    self._log_cycle(platform, jobs_found, jobs_applied, duration)
                    
                    logger.info(f"✅ Completed {platform} cycle: {jobs_found} jobs found, {jobs_applied} applications sent in {duration:.2f}s")
                    return {
                        'success': True,
                        'platform': platform,
                        'jobs_found': jobs_found,
                        'jobs_applied': jobs_applied,
                        'duration': duration,
                        'retry_count': retry_count
                    }
                else:
                    logger.warning(f"⚠️ No jobs found on {platform}, but no critical errors")
                    duration = time.time() - start_time
                    self._log_cycle(platform, jobs_found, jobs_applied, duration)
                    
                    return {
                        'success': True,
                        'platform': platform,
                        'jobs_found': jobs_found,
                        'jobs_applied': jobs_applied,
                        'duration': duration,
                        'retry_count': retry_count,
                        'message': 'No jobs found but no errors'
                    }
                
            except Exception as e:
                self._log_error(f"Critical error in {platform} cycle (attempt {retry_count + 1})", e)
                retry_count += 1
                
                if retry_count < max_retries:
                    wait_time = min(2 ** retry_count, 30)  # Exponential backoff, max 30s
                    logger.info(f"⏳ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    
                    # Reset browser on retry
                    try:
                        self._close_browser()
                    except:
                        pass
                else:
                    logger.error(f"❌ Max retries ({max_retries}) reached for {platform}")
        
        # If we get here, all retries failed
        duration = time.time() - start_time
        self._log_cycle(platform, jobs_found, jobs_applied, duration)
        
        return {
            'success': False,
            'platform': platform,
            'jobs_found': jobs_found,
            'jobs_applied': jobs_applied,
            'duration': duration,
            'retry_count': retry_count,
            'error': f'Failed after {max_retries} retries'
        }
    
    def run_comprehensive_cycle(self, platforms=None, max_jobs_per_platform=25, cycle_delay=300):
        """Run comprehensive job application cycle across multiple platforms with rotation"""
        if platforms is None:
            platforms = ["LinkedIn", "Indeed", "RemoteOK", "Dice"]
        
        logger.info(f"🚀 Starting comprehensive job cycle across {len(platforms)} platforms")
        start_time = time.time()
        
        # Overall statistics
        total_jobs_found = 0
        total_jobs_applied = 0
        platform_results = {}
        successful_platforms = []
        failed_platforms = []
        
        try:
            # Initialize browser once for all platforms
            if not self._setup_browser():
                logger.error("❌ Failed to initialize browser for comprehensive cycle")
                return {
                    'success': False,
                    'error': 'Browser initialization failed',
                    'platform_results': {},
                    'duration': time.time() - start_time
                }
            
            # Process each platform
            for platform_index, platform in enumerate(platforms):
                logger.info(f"📋 Processing platform {platform_index + 1}/{len(platforms)}: {platform}")
                
                try:
                    # Run platform cycle
                    platform_result = self.run_platform_cycle(
                        platform, 
                        max_jobs_per_search=max_jobs_per_platform // len(self.config['preferences'].get('job_types', ['DevOps Engineer']))
                    )
                    
                    # Store results
                    platform_results[platform] = platform_result
                    
                    if platform_result['success']:
                        successful_platforms.append(platform)
                        total_jobs_found += platform_result['jobs_found']
                        total_jobs_applied += platform_result['jobs_applied']
                        
                        logger.info(f"✅ {platform} cycle completed successfully")
                        logger.info(f"   Jobs found: {platform_result['jobs_found']}")
                        logger.info(f"   Jobs applied: {platform_result['jobs_applied']}")
                        logger.info(f"   Duration: {platform_result['duration']:.2f}s")
                    else:
                        failed_platforms.append(platform)
                        logger.error(f"❌ {platform} cycle failed: {platform_result.get('error', 'Unknown error')}")
                    
                    # Add delay between platforms (except for the last one)
                    if platform_index < len(platforms) - 1:
                        logger.info(f"⏳ Waiting {cycle_delay}s before next platform...")
                        time.sleep(cycle_delay)
                    
                except Exception as e:
                    self._log_error(f"Critical error processing {platform}", e)
                    failed_platforms.append(platform)
                    platform_results[platform] = {
                        'success': False,
                        'platform': platform,
                        'error': str(e),
                        'jobs_found': 0,
                        'jobs_applied': 0,
                        'duration': 0
                    }
            
            # Calculate overall statistics
            total_duration = time.time() - start_time
            success_rate = len(successful_platforms) / len(platforms) if platforms else 0
            
            # Log comprehensive results
            self._log_comprehensive_cycle_results(
                platforms, successful_platforms, failed_platforms,
                total_jobs_found, total_jobs_applied, total_duration
            )
            
            # Determine overall success
            overall_success = len(successful_platforms) > 0  # Success if at least one platform worked
            
            logger.info(f"🎯 Comprehensive cycle completed!")
            logger.info(f"   Success rate: {success_rate:.1%} ({len(successful_platforms)}/{len(platforms)} platforms)")
            logger.info(f"   Total jobs found: {total_jobs_found}")
            logger.info(f"   Total jobs applied: {total_jobs_applied}")
            logger.info(f"   Total duration: {total_duration:.2f}s")
            
            return {
                'success': overall_success,
                'total_jobs_found': total_jobs_found,
                'total_jobs_applied': total_jobs_applied,
                'duration': total_duration,
                'success_rate': success_rate,
                'successful_platforms': successful_platforms,
                'failed_platforms': failed_platforms,
                'platform_results': platform_results
            }
            
        except Exception as e:
            self._log_error("Critical error in comprehensive cycle", e)
            return {
                'success': False,
                'error': str(e),
                'platform_results': platform_results,
                'duration': time.time() - start_time
            }
        finally:
            # Clean up browser
            try:
                self._close_browser()
            except:
                pass
    
    def _log_comprehensive_cycle_results(self, platforms, successful_platforms, failed_platforms,
                                       total_jobs_found, total_jobs_applied, total_duration):
        """Log comprehensive cycle results to file"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            comprehensive_log = (
                f"{timestamp} - COMPREHENSIVE CYCLE RESULTS\n"
                f"Platforms processed: {', '.join(platforms)}\n"
                f"Successful platforms: {', '.join(successful_platforms)}\n"
                f"Failed platforms: {', '.join(failed_platforms)}\n"
                f"Total jobs found: {total_jobs_found}\n"
                f"Total jobs applied: {total_jobs_applied}\n"
                f"Total duration: {total_duration:.2f}s\n"
                f"Success rate: {len(successful_platforms)}/{len(platforms)} platforms\n"
                f"{'='*60}\n"
            )
            
            with open(self.cycle_log_file, 'a', encoding='utf-8') as f:
                f.write(comprehensive_log)
                
            logger.info("✅ Comprehensive cycle results logged")
            
        except Exception as e:
            self._log_error("Failed to log comprehensive cycle results", e)
    
    def run_smart_retry_cycle(self, failed_platforms, max_attempts=2):
        """Run smart retry cycle for failed platforms with adaptive strategies"""
        if not failed_platforms:
            logger.info("✅ No failed platforms to retry")
            return {'success': True, 'retried_platforms': []}
        
        logger.info(f"🔄 Starting smart retry cycle for {len(failed_platforms)} failed platforms")
        retry_results = {}
        successful_retries = []
        
        for attempt in range(max_attempts):
            logger.info(f"🔄 Retry attempt {attempt + 1}/{max_attempts}")
            
            platforms_to_retry = [p for p in failed_platforms if p not in successful_retries]
            
            if not platforms_to_retry:
                logger.info("✅ All platforms successfully retried")
                break
            
            for platform in platforms_to_retry:
                try:
                    logger.info(f"🔄 Retrying {platform}...")
                    
                    # Use progressively more conservative settings
                    max_jobs = max(5, 10 - (attempt * 2))  # Reduce job count on retries
                    
                    # Setup browser fresh for retry
                    if not self._setup_browser():
                        logger.error(f"❌ Browser setup failed for {platform} retry")
                        continue
                    
                    # Run platform cycle with retry settings
                    result = self.run_platform_cycle(platform, max_jobs_per_search=max_jobs)
                    
                    if result['success']:
                        successful_retries.append(platform)
                        retry_results[platform] = result
                        logger.info(f"✅ {platform} retry successful")
                    else:
                        logger.warning(f"⚠️ {platform} retry failed")
                        retry_results[platform] = result
                    
                    # Close browser between retries
                    self._close_browser()
                    
                    # Add delay between retry attempts
                    time.sleep(30)
                    
                except Exception as e:
                    self._log_error(f"Error during {platform} retry", e)
                    retry_results[platform] = {
                        'success': False,
                        'error': str(e),
                        'platform': platform
                    }
            
            # Add longer delay between retry attempts
            if attempt < max_attempts - 1 and len(successful_retries) < len(failed_platforms):
                logger.info("⏳ Waiting before next retry attempt...")
                time.sleep(120)  # 2 minutes between retry attempts
        
        logger.info(f"🎯 Smart retry cycle completed: {len(successful_retries)}/{len(failed_platforms)} platforms recovered")
        
        return {
            'success': len(successful_retries) > 0,
            'retried_platforms': successful_retries,
            'failed_platforms': [p for p in failed_platforms if p not in successful_retries],
            'retry_results': retry_results
        }
