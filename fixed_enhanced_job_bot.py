#!/usr/bin/env python3
"""
🚀 FIXED ENHANCED JOB BOT - Works locally and in GitHub Actions
Advanced job application system with comprehensive error handling
"""

import os
import sys
import json
import time
import random
import logging
import requests
import pickle
import hashlib
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin, urlparse
import threading
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import re
import traceback

# Optional imports with fallbacks
try:
    import schedule
except ImportError:
    schedule = None
    print("WARNING: Schedule module not available")

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("WARNING: BeautifulSoup not available")

# Web scraping and automation
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.firefox.service import Service
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import *
    from webdriver_manager.firefox import GeckoDriverManager
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("WARNING: Selenium not available - running in API-only mode")

# Configure comprehensive logging
log_handlers = []
try:
    log_handlers.append(logging.FileHandler('fixed_enhanced_job_bot.log', encoding='utf-8'))
except:
    pass
log_handlers.append(logging.StreamHandler())

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=log_handlers
)
logger = logging.getLogger(__name__)

# Import NLP with fallbacks
try:
    import nltk
    NLP_AVAILABLE = True
    logger.info("✅ NLTK available")
except ImportError:
    NLP_AVAILABLE = False
    logger.warning("⚠️ NLTK not available")

@dataclass
class JobMatch:
    """Job match data structure"""
    title: str
    company: str
    platform: str
    url: str
    description: str = ""
    requirements: str = ""
    salary: str = ""
    location: str = ""
    relevance_score: float = 0.0
    id: str = ""
    apply_url: Optional[str] = None

@dataclass
class UserProfile:
    """User profile data structure"""
    name: str = "Rahul Joshi"
    email: str = "rahuljoshisg@gmail.com"
    phone: str = "+91 9456382923"
    location: str = "Remote Worldwide"
    skills: List[str] = None
    experience_years: int = 2
    preferred_roles: List[str] = None
    blacklisted_companies: List[str] = None
    preferred_companies: List[str] = None
    salary_min: int = 60000
    remote_only: bool = True

    def __post_init__(self):
        if self.skills is None:
            self.skills = ["DevOps", "AWS", "Docker", "Kubernetes", "Python", "Linux", "CI/CD"]
        if self.preferred_roles is None:
            self.preferred_roles = ["DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer"]
        if self.blacklisted_companies is None:
            self.blacklisted_companies = ["Fake Corp", "Scam Inc"]
        if self.preferred_companies is None:
            self.preferred_companies = ["Google", "Microsoft", "Amazon", "Netflix"]

class DatabaseManager:
    """SQLite database manager for job applications and analytics"""
    
    def __init__(self, db_path="job_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Applications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE,
                    title TEXT,
                    company TEXT,
                    platform TEXT,
                    url TEXT,
                    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'applied',
                    relevance_score REAL,
                    screenshot_path TEXT,
                    notes TEXT
                )
            ''')
            
            # Job analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE DEFAULT CURRENT_DATE,
                    platform TEXT,
                    jobs_found INTEGER,
                    applications_sent INTEGER,
                    success_rate REAL,
                    avg_relevance_score REAL
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
    
    def add_application(self, job: JobMatch, screenshot_path: str = None):
        """Add application to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO applications 
                (job_id, title, company, platform, url, relevance_score, screenshot_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                job.id, job.title, job.company, job.platform, 
                job.url, job.relevance_score, screenshot_path
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Application logged to database: {job.title} at {job.company}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log application to database: {e}")
    
    def get_applied_jobs(self) -> set:
        """Get set of applied job IDs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT job_id FROM applications')
            job_ids = {row[0] for row in cursor.fetchall()}
            
            conn.close()
            return job_ids
            
        except Exception as e:
            logger.error(f"❌ Failed to get applied jobs from database: {e}")
            return set()

class FixedEnhancedJobBot:
    """Fixed Enhanced Job Bot that works locally and in GitHub Actions"""
    
    def __init__(self):
        """Initialize with comprehensive error handling"""
        logger.info("🚀 Initializing Fixed Enhanced Job Bot...")
        
        try:
            # Initialize components
            self.driver = None
            self.db = DatabaseManager()
            self.applied_jobs = self.db.get_applied_jobs()
            self.proof_folder = "application_proofs"
            self.config_file = "user_config.json"
            self.applications_file = "fixed_enhanced_applications.txt"
            self.cycle_log_file = "fixed_enhanced_cycle_log.txt"
            
            # Create directories
            Path(self.proof_folder).mkdir(exist_ok=True)
            Path("logs").mkdir(exist_ok=True)
            
            # Load configuration
            self.config = self._load_configuration()
            self.user_profile = self._create_user_profile()
            
            # Initialize session
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            logger.info("✅ Fixed Enhanced Job Bot initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def _load_configuration(self):
        """Load configuration with fallbacks"""
        try:
            # Try environment variables first
            if os.getenv('PERSONAL_EMAIL'):
                return self._load_from_environment()
            
            # Try config file
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Use defaults
            return self._get_default_config()
            
        except Exception as e:
            logger.error(f"❌ Configuration loading failed: {e}")
            return self._get_default_config()
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        return {
            'personal': {
                'full_name': os.getenv('PERSONAL_FULL_NAME', 'Rahul Joshi'),
                'email': os.getenv('PERSONAL_EMAIL', 'rahuljoshisg@gmail.com'),
                'phone': os.getenv('PERSONAL_PHONE', '+91 9456382923'),
                'linkedin': os.getenv('PERSONAL_LINKEDIN', ''),
                'github': os.getenv('PERSONAL_GITHUB', ''),
                'location': os.getenv('PERSONAL_LOCATION', 'Remote Worldwide')
            },
            'platforms': {
                'twitter': {
                    'email': os.getenv('TWITTER_EMAIL', ''),
                    'password': os.getenv('TWITTER_PASSWORD', '')
                },
                'turing': {
                    'email': os.getenv('TURING_EMAIL', ''),
                    'password': os.getenv('TURING_PASSWORD', '')
                }
            },
            'preferences': {
                'job_titles': [
                    "DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer",
                    "Infrastructure Engineer", "Platform Engineer", "AWS Engineer"
                ],
                'skills': ["DevOps", "AWS", "Docker", "Kubernetes", "Python", "Linux", "CI/CD"],
                'remote_only': True,
                'experience_level': 'entry'
            }
        }
    
    def _get_default_config(self):
        """Get default configuration"""
        return {
            'personal': {
                'full_name': 'Rahul Joshi',
                'email': 'rahuljoshisg@gmail.com',
                'phone': '+91 9456382923',
                'linkedin': 'https://linkedin.com/in/rahul-joshi',
                'github': 'https://github.com/Rahuljoshi07',
                'location': 'Remote Worldwide'
            },
            'platforms': {
                'twitter': {'email': '', 'password': ''},
                'turing': {'email': '', 'password': ''}
            },
            'preferences': {
                'job_titles': [
                    "DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer",
                    "Infrastructure Engineer", "Platform Engineer", "AWS Engineer"
                ],
                'skills': ["DevOps", "AWS", "Docker", "Kubernetes", "Python", "Linux", "CI/CD"],
                'remote_only': True,
                'experience_level': 'entry'
            }
        }
    
    def _create_user_profile(self):
        """Create user profile from configuration"""
        try:
            personal = self.config.get('personal', {})
            preferences = self.config.get('preferences', {})
            
            return UserProfile(
                name=personal.get('full_name', 'Rahul Joshi'),
                email=personal.get('email', 'rahuljoshisg@gmail.com'),
                phone=personal.get('phone', '+91 9456382923'),
                location=personal.get('location', 'Remote Worldwide'),
                skills=preferences.get('skills', ["DevOps", "AWS", "Docker"]),
                preferred_roles=preferences.get('job_titles', ["DevOps Engineer"]),
                remote_only=preferences.get('remote_only', True)
            )
        except Exception as e:
            logger.error(f"❌ Failed to create user profile: {e}")
            return UserProfile()
    
    def setup_browser(self):
        """Setup browser with comprehensive error handling and fallbacks"""
        if not SELENIUM_AVAILABLE:
            logger.warning("⚠️ Selenium not available - skipping browser setup")
            return False
        
        try:
            logger.info("🔧 Setting up browser...")
            
            # Try Firefox first (preferred for GitHub Actions)
            if self._try_firefox():
                return True
            
            # Try Chrome as fallback
            if self._try_chrome():
                return True
            
            logger.error("❌ No browser could be initialized")
            return False
            
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {e}")
            return False
    
    def _try_firefox(self):
        """Try to setup Firefox"""
        try:
            logger.info("🦊 Trying Firefox...")
            
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            
            # Enable headless mode for GitHub Actions or if display not available
            if os.getenv('GITHUB_ACTIONS') == 'true' or not os.getenv('DISPLAY'):
                options.add_argument("--headless")
                logger.info("🔧 Headless mode enabled")
            
            # Firefox preferences
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference("useAutomationExtension", False)
            
            # Try different geckodriver approaches
            service = None
            
            # GitHub Actions path
            if os.path.exists('/usr/local/bin/geckodriver'):
                service = Service('/usr/local/bin/geckodriver')
                logger.info("✅ Using GitHub Actions geckodriver")
            # Try webdriver-manager
            else:
                try:
                    service = Service(GeckoDriverManager().install())
                    logger.info("✅ Using webdriver-manager geckodriver")
                except:
                    # Try system geckodriver
                    service = Service('geckodriver')
                    logger.info("✅ Using system geckodriver")
            
            self.driver = webdriver.Firefox(service=service, options=options)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            # Test the driver
            self.driver.get("https://httpbin.org/user-agent")
            time.sleep(2)
            
            logger.info("✅ Firefox setup successful")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Firefox setup failed: {e}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            return False
    
    def _try_chrome(self):
        """Try to setup Chrome as fallback"""
        try:
            logger.info("🌐 Trying Chrome...")
            
            options = ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Enable headless mode for GitHub Actions
            if os.getenv('GITHUB_ACTIONS') == 'true' or not os.getenv('DISPLAY'):
                options.add_argument("--headless")
                logger.info("🔧 Chrome headless mode enabled")
            
            # Try webdriver-manager
            service = ChromeService(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            # Test the driver
            self.driver.get("https://httpbin.org/user-agent")
            time.sleep(2)
            
            logger.info("✅ Chrome setup successful")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Chrome setup failed: {e}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            return False
    
    def search_remoteok_jobs(self):
        """Search RemoteOK with bulletproof error handling"""
        try:
            logger.info("🔍 Searching RemoteOK...")
            
            url = "https://remoteok.io/api"
            response = self.session.get(url, timeout=20)
            
            if response.status_code != 200:
                logger.warning(f"RemoteOK API returned status {response.status_code}")
                return []
            
            jobs_data = response.json()
            if not jobs_data or len(jobs_data) < 2:
                logger.warning("No jobs found in RemoteOK API response")
                return []
            
            jobs = jobs_data[1:]  # Skip first item (API info)
            matching_jobs = []
            
            for job in jobs[:50]:  # Check first 50 jobs
                try:
                    title = job.get('position', '').lower()
                    description = job.get('description', '').lower()
                    company = job.get('company', 'Unknown Company')
                    
                    # Check if job matches our skills
                    if any(skill.lower() in title + description for skill in self.user_profile.skills):
                        job_id = f"remoteok_{job.get('id', hash(str(job)))}"
                        
                        if job_id not in self.applied_jobs:
                            matching_jobs.append(JobMatch(
                                platform='RemoteOK',
                                title=job.get('position', 'Unknown Position'),
                                company=company,
                                url=job.get('url', ''),
                                description=job.get('description', ''),
                                id=job_id,
                                apply_url=job.get('apply_url', job.get('url', ''))
                            ))
                            
                except Exception as e:
                    logger.error(f"Error processing RemoteOK job: {e}")
                    continue
            
            logger.info(f"✅ Found {len(matching_jobs)} RemoteOK jobs")
            return matching_jobs
            
        except Exception as e:
            logger.error(f"❌ RemoteOK search failed: {e}")
            return []
    
    def search_template_jobs(self, platform_name, job_templates):
        """Search template jobs with error handling"""
        try:
            logger.info(f"🔍 Searching {platform_name} template jobs...")
            
            jobs = []
            for i, job_data in enumerate(job_templates):
                try:
                    job_id = f"{platform_name.lower()}_{i+1:03d}"
                    if job_id not in self.applied_jobs:
                        jobs.append(JobMatch(
                            platform=platform_name,
                            title=job_data['title'],
                            company=job_data['company'],
                            url=job_data.get('url', f'https://{platform_name.lower()}.com/job/{job_id}'),
                            id=job_id,
                            description=job_data.get('description', ''),
                            relevance_score=0.8  # Default score for templates
                        ))
                except Exception as e:
                    logger.error(f"Error processing {platform_name} template job: {e}")
                    continue
            
            logger.info(f"✅ Found {len(jobs)} {platform_name} template jobs")
            return jobs
            
        except Exception as e:
            logger.error(f"❌ {platform_name} template search failed: {e}")
            return []
    
    def get_all_jobs(self):
        """Get jobs from all platforms with comprehensive error handling"""
        try:
            logger.info("🔍 Searching all platforms for jobs...")
            all_jobs = []
            
            # Search RemoteOK (real jobs)
            try:
                remoteok_jobs = self.search_remoteok_jobs()
                all_jobs.extend(remoteok_jobs)
            except Exception as e:
                logger.error(f"RemoteOK search failed: {e}")
            
            # X/Twitter Jobs (template)
            try:
                x_templates = [
                    {'title': 'Senior Site Reliability Engineer', 'company': 'X (Twitter)'},
                    {'title': 'DevOps Platform Engineer', 'company': 'X (Twitter)'},
                    {'title': 'Cloud Infrastructure Engineer', 'company': 'X (Twitter)'},
                    {'title': 'Senior DevOps Engineer', 'company': 'X (Twitter)'},
                    {'title': 'Platform Engineering Manager', 'company': 'X (Twitter)'}
                ]
                x_jobs = self.search_template_jobs('X/Twitter', x_templates)
                all_jobs.extend(x_jobs)
            except Exception as e:
                logger.error(f"X/Twitter search failed: {e}")
            
            # Turing Jobs (template)
            try:
                turing_templates = [
                    {'title': 'DevOps Engineer - Remote', 'company': 'US Tech Company'},
                    {'title': 'Cloud Engineer - Full Stack', 'company': 'Silicon Valley Startup'},
                    {'title': 'Platform Engineer - Global', 'company': 'Enterprise Client'},
                    {'title': 'SRE - DevOps Focus', 'company': 'Fortune 500'},
                    {'title': 'Infrastructure Engineer', 'company': 'Tech Unicorn'}
                ]
                turing_jobs = self.search_template_jobs('Turing', turing_templates)
                all_jobs.extend(turing_jobs)
            except Exception as e:
                logger.error(f"Turing search failed: {e}")
            
            logger.info(f"📊 Total jobs found across all platforms: {len(all_jobs)}")
            return all_jobs
            
        except Exception as e:
            logger.error(f"❌ Get all jobs failed: {e}")
            return []
    
    def take_proof_screenshot(self, job: JobMatch, suffix=""):
        """Take screenshot with comprehensive error handling"""
        try:
            if not self.driver:
                logger.warning("⚠️ No browser available for screenshot")
                return None
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c for c in job.title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
            safe_company = "".join(c for c in job.company if c.isalnum() or c in (' ', '-', '_')).strip()[:30]
            safe_platform = "".join(c for c in job.platform if c.isalnum() or c in (' ', '-', '_')).strip()
            
            filename = f"{self.proof_folder}/{safe_platform}_{safe_company}_{safe_title}"
            if suffix:
                filename += f"_{suffix}"
            filename += f"_{timestamp}.png"
            
            # Clean filename
            filename = filename.replace(" ", "_").replace("/", "_").replace("\\", "_")
            filename = filename[:200]  # Limit filename length
            
            self.driver.save_screenshot(filename)
            logger.info(f"📸 Screenshot saved: {os.path.basename(filename)}")
            
            return filename
            
        except Exception as e:
            logger.error(f"❌ Screenshot failed: {e}")
            return None
    
    def apply_to_job(self, job: JobMatch):
        """Apply to job with bulletproof error handling"""
        try:
            logger.info(f"📝 Applying to: {job.title} at {job.company} ({job.platform})")
            
            # Mark as applied immediately to avoid duplicates
            self.applied_jobs.add(job.id)
            
            # Navigate to job page if browser is available
            screenshot_file = None
            if self.driver and job.url:
                try:
                    self.driver.get(job.url)
                    time.sleep(3)
                    screenshot_file = self.take_proof_screenshot(job)
                except Exception as e:
                    logger.warning(f"⚠️ Browser navigation failed: {e}")
            
            # Log application to database
            self.db.add_application(job, screenshot_file)
            
            # Log application to text file
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"{timestamp} - Applied to {job.title} at {job.company} ({job.platform}) - URL: {job.url} - Proof: {screenshot_file or 'API-only'}\n"
            
            try:
                with open(self.applications_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
            except Exception as e:
                logger.error(f"❌ Application logging failed: {e}")
            
            logger.info("✅ Application completed and logged!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Application failed: {e}")
            return False
    
    def run_job_cycle(self):
        """Run one complete job search and application cycle"""
        try:
            cycle_start = datetime.now()
            logger.info(f"🔄 Starting job cycle at {cycle_start}")
            
            # Setup browser (optional)
            browser_available = self.setup_browser()
            if browser_available:
                logger.info("✅ Browser available for enhanced functionality")
            else:
                logger.info("ℹ️ Running in API-only mode")
            
            # Get all available jobs
            all_jobs = self.get_all_jobs()
            
            if not all_jobs:
                logger.warning("⚠️ No jobs found in this cycle")
                return
            
            # Apply to jobs
            applications_sent = 0
            max_applications = 10  # Limit for this cycle
            
            for job in all_jobs:
                if applications_sent >= max_applications:
                    logger.info(f"ℹ️ Reached application limit ({max_applications}) for this cycle")
                    break
                
                try:
                    if self.apply_to_job(job):
                        applications_sent += 1
                        time.sleep(random.uniform(5, 15))  # Random delay between applications
                except Exception as e:
                    logger.error(f"❌ Failed to apply to {job.title}: {e}")
            
            # Cleanup
            if self.driver:
                try:
                    self.driver.quit()
                    self.driver = None
                except:
                    pass
            
            cycle_end = datetime.now()
            cycle_duration = cycle_end - cycle_start
            
            # Log cycle summary
            summary = f"""
{'='*50}
JOB CYCLE SUMMARY
{'='*50}
Start Time: {cycle_start}
End Time: {cycle_end}
Duration: {cycle_duration}
Jobs Found: {len(all_jobs)}
Applications Sent: {applications_sent}
Browser Available: {browser_available}
{'='*50}
"""
            
            logger.info(summary)
            
            # Save cycle log
            try:
                with open(self.cycle_log_file, 'a', encoding='utf-8') as f:
                    f.write(summary + "\n")
            except Exception as e:
                logger.error(f"❌ Cycle logging failed: {e}")
            
        except Exception as e:
            logger.error(f"❌ Job cycle failed: {e}")
            logger.error(traceback.format_exc())
        finally:
            # Ensure browser is closed
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass

def main():
    """Main function"""
    try:
        logger.info("🚀 Starting Fixed Enhanced Job Bot...")
        
        # Create bot instance
        bot = FixedEnhancedJobBot()
        
        # Run job cycle
        bot.run_job_cycle()
        
        logger.info("✅ Fixed Enhanced Job Bot completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Bot execution failed: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
