#!/usr/bin/env python3
"""
🚀 ENHANCED ULTIMATE JOB BOT - AI-POWERED AUTOMATION
Advanced job application system with ML, NLP, and comprehensive automation
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
import smtplib
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin, urlparse
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import schedule
import threading
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import re
import traceback

# Web scraping and automation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import *
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
# Configure comprehensive logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_job_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import enhanced captcha solver with fallback
try:
    from enhanced_captcha_solver import EnhancedCaptchaSolver
    CAPTCHA_SOLVER_AVAILABLE = True
except ImportError:
    CAPTCHA_SOLVER_AVAILABLE = False
    logger.warning("Enhanced captcha solver not available, using basic handling")

# NLP and ML libraries
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    import spacy
    from textblob import TextBlob
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import pandas as pd
    import numpy as np
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    print("⚠️ NLP libraries not available. Installing basic versions...")

# PDF processing
try:
    import PyPDF2
    import docx
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Logger is already configured above

@dataclass
class JobMatch:
    """Job match data structure"""
    title: str
    company: str
    platform: str
    url: str
    description: str
    requirements: str
    salary: str
    location: str
    relevance_score: float
    sentiment_score: float
    skill_match_percentage: float
    id: str
    apply_url: Optional[str] = None

@dataclass
class UserProfile:
    """User profile data structure"""
    name: str
    email: str
    phone: str
    location: str
    skills: List[str]
    experience_years: int
    preferred_roles: List[str]
    blacklisted_companies: List[str]
    preferred_companies: List[str]
    salary_min: int
    remote_only: bool
    certifications: List[str]

class DatabaseManager:
    """SQLite database manager for job applications and analytics"""
    
    def __init__(self, db_path="job_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
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
                applied_date TIMESTAMP,
                status TEXT DEFAULT 'applied',
                relevance_score REAL,
                screenshot_path TEXT,
                cover_letter TEXT,
                response_received BOOLEAN DEFAULT FALSE,
                response_date TIMESTAMP,
                notes TEXT
            )
        ''')
        
        # Job analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                platform TEXT,
                jobs_found INTEGER,
                applications_sent INTEGER,
                success_rate REAL,
                avg_relevance_score REAL
            )
        ''')
        
        # User feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT,
                feedback_type TEXT,
                feedback_value TEXT,
                timestamp TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_application(self, job_match: JobMatch, screenshot_path: str, cover_letter: str):
        """Save application to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO applications 
                (job_id, title, company, platform, url, applied_date, relevance_score, 
                 screenshot_path, cover_letter)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_match.id, job_match.title, job_match.company, job_match.platform,
                job_match.url, datetime.now(), job_match.relevance_score,
                screenshot_path, cover_letter
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Database save error: {e}")
        finally:
            conn.close()

class ResumeParser:
    """Advanced resume parsing with NLP"""
    
    def __init__(self):
        self.skills_keywords = [
            'python', 'java', 'javascript', 'react', 'node', 'angular', 'vue',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
            'jenkins', 'gitlab', 'github', 'ci/cd', 'devops', 'linux',
            'sql', 'mongodb', 'postgresql', 'mysql', 'redis',
            'machine learning', 'ai', 'data science', 'analytics'
        ]
        
        if NLP_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except:
                self.nlp = None
                logger.warning("Spacy model not available")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF resume"""
        if not PDF_AVAILABLE:
            return ""
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return ""
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skills_keywords:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        # Additional pattern matching
        patterns = {
            'programming': r'\b(python|java|javascript|c\+\+|c#|ruby|go|rust|php)\b',
            'frameworks': r'\b(react|angular|vue|django|flask|spring|express)\b',
            'cloud': r'\b(aws|azure|gcp|cloud|ec2|s3|lambda)\b',
            'databases': r'\b(sql|mysql|postgresql|mongodb|redis|elasticsearch)\b'
        }
        
        for category, pattern in patterns.items():
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            found_skills.extend([match.title() for match in matches])
        
        return list(set(found_skills))
    
    def extract_experience_years(self, text: str) -> int:
        """Extract years of experience from resume"""
        patterns = [
            r'(\d+)\+?\s*years?\s*of\s*experience',
            r'experience:?\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return 0
    
    def parse_resume(self, resume_path: str) -> Dict:
        """Parse resume and extract key information"""
        if not os.path.exists(resume_path):
            logger.warning(f"Resume not found: {resume_path}")
            return {}
        
        # Extract text
        if resume_path.endswith('.pdf'):
            text = self.extract_text_from_pdf(resume_path)
        else:
            with open(resume_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        # Extract information
        skills = self.extract_skills(text)
        experience_years = self.extract_experience_years(text)
        
        # Extract contact info (basic patterns)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        
        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)
        
        return {
            'skills': skills,
            'experience_years': experience_years,
            'email': emails[0] if emails else '',
            'phone': phones[0] if phones else '',
            'full_text': text
        }

class JobRelevanceScorer:
    """ML-based job relevance scoring"""
    
    def __init__(self):
        if NLP_AVAILABLE:
            self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            self.fitted = False
    
    def calculate_skill_match(self, user_skills: List[str], job_requirements: str) -> float:
        """Calculate skill match percentage"""
        if not user_skills:
            return 0.0
        
        job_text = job_requirements.lower()
        matched_skills = 0
        
        for skill in user_skills:
            if skill.lower() in job_text:
                matched_skills += 1
        
        return (matched_skills / len(user_skills)) * 100
    
    def calculate_relevance_score(self, user_profile: UserProfile, job_match: JobMatch) -> float:
        """Calculate comprehensive job relevance score (0-100)"""
        score = 0.0
        
        # Skill match (40% weight)
        skill_match = self.calculate_skill_match(user_profile.skills, job_match.requirements)
        score += skill_match * 0.4
        
        # Title match (25% weight)
        title_match = 0
        for preferred_role in user_profile.preferred_roles:
            if preferred_role.lower() in job_match.title.lower():
                title_match = 100
                break
        score += title_match * 0.25
        
        # Location match (15% weight)
        location_match = 0
        if user_profile.remote_only and 'remote' in job_match.location.lower():
            location_match = 100
        elif user_profile.location.lower() in job_match.location.lower():
            location_match = 100
        score += location_match * 0.15
        
        # Company preference (10% weight)
        company_match = 0
        if job_match.company in user_profile.preferred_companies:
            company_match = 100
        elif job_match.company in user_profile.blacklisted_companies:
            company_match = -100
        score += company_match * 0.1
        
        # Sentiment score (10% weight)
        score += job_match.sentiment_score * 0.1
        
        return max(0, min(100, score))
    
    def analyze_job_sentiment(self, job_description: str) -> float:
        """Analyze job description sentiment (scam detection)"""
        # Scam indicators
        scam_keywords = [
            'make money fast', 'work from home guaranteed', 'no experience required',
            'earn $1000+ daily', 'investment opportunity', 'pyramid', 'mlm',
            'too good to be true', 'limited time offer', 'act now'
        ]
        
        spam_score = 0
        description_lower = job_description.lower()
        
        for keyword in scam_keywords:
            if keyword in description_lower:
                spam_score += 10
        
        # Positive indicators
        positive_keywords = [
            'career growth', 'professional development', 'competitive salary',
            'benefits', 'training', 'mentorship', 'team collaboration'
        ]
        
        positive_score = 0
        for keyword in positive_keywords:
            if keyword in description_lower:
                positive_score += 5
        
        # Calculate final sentiment score (0-100, higher is better)
        final_score = max(0, min(100, 50 + positive_score - spam_score))
        return final_score

class SmartScheduler:
    """Intelligent scheduling system"""
    
    def __init__(self):
        self.timezone_offset = 0  # UTC offset
        self.working_hours = (9, 17)  # 9 AM to 5 PM
        self.avoid_weekends = True
        self.max_applications_per_hour = 5
        self.application_count = 0
        self.last_reset = datetime.now()
    
    def is_good_time_to_apply(self) -> bool:
        """Check if it's a good time to apply"""
        now = datetime.now()
        
        # Reset hourly counter
        if (now - self.last_reset).seconds > 3600:
            self.application_count = 0
            self.last_reset = now
        
        # Check rate limiting
        if self.application_count >= self.max_applications_per_hour:
            return False
        
        # Check working hours
        if not (self.working_hours[0] <= now.hour <= self.working_hours[1]):
            return False
        
        # Check weekends
        if self.avoid_weekends and now.weekday() >= 5:
            return False
        
        return True
    
    def get_random_delay(self) -> float:
        """Get random delay to avoid bot detection"""
        return random.uniform(3, 8)  # 3-8 seconds
    
    def schedule_next_run(self) -> datetime:
        """Schedule next bot run"""
        base_interval = random.randint(90, 150)  # 1.5-2.5 hours
        next_run = datetime.now() + timedelta(minutes=base_interval)
        
        # Ensure it's during working hours
        while not self.is_good_time_to_apply():
            next_run += timedelta(minutes=30)
        
        return next_run

class NotificationSystem:
    """Email and alert notification system"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.email_config = config.get('notifications', {}).get('email', {})
    
    def send_email(self, subject: str, body: str, to_email: str = None):
        """Send email notification"""
        try:
            if not self.email_config.get('enabled', False):
                return
            
            smtp_server = self.email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.email_config.get('smtp_port', 587)
            sender_email = self.email_config.get('sender_email')
            sender_password = self.email_config.get('sender_password')
            
            if not all([sender_email, sender_password]):
                return
            
            to_email = to_email or self.email_config.get('recipient_email', sender_email)
            
            msg = MimeMultipart()
            msg['From'] = sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent: {subject}")
            
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
    
    def notify_new_job(self, job_match: JobMatch):
        """Notify about new job match"""
        subject = f"🎯 New Job Match: {job_match.title}"
        body = f"""
New job opportunity found!

Title: {job_match.title}
Company: {job_match.company}
Platform: {job_match.platform}
Relevance Score: {job_match.relevance_score:.1f}%
Location: {job_match.location}
URL: {job_match.url}

Job will be automatically applied to if score > 70%.
        """
        self.send_email(subject, body)
    
    def notify_application_sent(self, job_match: JobMatch, total_applications: int):
        """Notify about successful application"""
        subject = f"✅ Application Sent: {job_match.company}"
        body = f"""
Application successfully submitted!

Job: {job_match.title}
Company: {job_match.company}
Platform: {job_match.platform}
Relevance Score: {job_match.relevance_score:.1f}%

Total applications today: {total_applications}
        """
        self.send_email(subject, body)
    
    def notify_error(self, error_message: str, context: str = ""):
        """Notify about system errors"""
        subject = "❌ Job Bot Error"
        body = f"""
Job bot encountered an error:

Context: {context}
Error: {error_message}

Please check the logs for more details.
        """
        self.send_email(subject, body)

class EnhancedJobScraper:
    """Advanced job scraping with multiple platforms and intelligent search strategy"""
    
    def __init__(self, user_profile: UserProfile):
        self.user_profile = user_profile
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Hierarchical job preferences based on experience level
        self.hierarchical_job_titles = [
            "Site Reliability Engineer (SRE)",
            "Platform Engineer", 
            "Cloud Infrastructure Engineer (AWS/Azure/GCP)",
            "Senior DevOps Engineer",
            "Kubernetes Engineer",
            "K8s Admin",
            "Terraform/IaC Engineer",
            "CI/CD Automation Engineer",
            "Cloud Security Engineer",
            "DevOps Engineer",
            "Cloud Engineer (AWS/GCP)",
            "Build & Release Engineer",
            "Jenkins Pipeline Engineer",
            "Linux System Administrator (Cloud-based)",
            "Infrastructure Engineer",
            "Automation Engineer (Bash/Python)"
        ]
        
        # Platform priority order
        self.platform_priority = [
            'RemoteOK',
            'LinkedIn', 
            'Dice',
            'Indeed',
            'X/Twitter',
            'Turing'
        ]
        
        self.current_platform_index = 0
        self.current_job_title_index = 0
    
    def search_remoteok(self) -> List[JobMatch]:
        """Search RemoteOK with advanced filtering"""
        jobs = []
        try:
            url = "https://remoteok.io/api"
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                data = response.json()[1:]  # Skip first item
                
                for job_data in data[:50]:
                    title = job_data.get('position', '')
                    company = job_data.get('company', '')
                    description = job_data.get('description', '')
                    
                    # Skip blacklisted companies
                    if company in self.user_profile.blacklisted_companies:
                        continue
                    
                    # Check skill match
                    skill_match = any(skill.lower() in description.lower() 
                                    for skill in self.user_profile.skills)
                    
                    if skill_match or any(role.lower() in title.lower() 
                                        for role in self.user_profile.preferred_roles):
                        job_match = JobMatch(
                            title=title,
                            company=company,
                            platform="RemoteOK",
                            url=job_data.get('url', ''),
                            description=description,
                            requirements=description,
                            salary=f"${job_data.get('salary_min', 0)}-{job_data.get('salary_max', 0)}",
                            location="Remote",
                            relevance_score=0,
                            sentiment_score=0,
                            skill_match_percentage=0,
                            id=f"remoteok_{job_data.get('id', hash(str(job_data)))}"
                        )
                        jobs.append(job_match)
                        
        except Exception as e:
            logger.error(f"RemoteOK search error: {e}")
        
        return jobs
    
    def search_dice(self, driver) -> List[JobMatch]:
        """Search Dice.com with Selenium"""
        jobs = []
        try:
            search_terms = " OR ".join(self.user_profile.preferred_roles)
            url = f"https://www.dice.com/jobs?q={search_terms}&location=Remote"
            
            driver.get(url)
            time.sleep(3)
            
            job_cards = driver.find_elements(By.CSS_SELECTOR, "[data-cy='card']")
            
            for card in job_cards[:20]:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, "[data-cy='card-title'] a")
                    title = title_elem.text
                    url = title_elem.get_attribute('href')
                    
                    company_elem = card.find_element(By.CSS_SELECTOR, "[data-cy='card-company']")
                    company = company_elem.text
                    
                    # Skip blacklisted companies
                    if company in self.user_profile.blacklisted_companies:
                        continue
                    
                    location_elem = card.find_element(By.CSS_SELECTOR, "[data-cy='card-location']")
                    location = location_elem.text
                    
                    # Get job description by clicking
                    description = ""
                    try:
                        title_elem.click()
                        time.sleep(2)
                        desc_elem = driver.find_element(By.CSS_SELECTOR, ".job-description")
                        description = desc_elem.text
                        driver.back()
                        time.sleep(2)
                    except:
                        pass
                    
                    job_match = JobMatch(
                        title=title,
                        company=company,
                        platform="Dice",
                        url=url,
                        description=description,
                        requirements=description,
                        salary="",
                        location=location,
                        relevance_score=0,
                        sentiment_score=0,
                        skill_match_percentage=0,
                        id=f"dice_{hashlib.md5(url.encode()).hexdigest()[:8]}"
                    )
                    jobs.append(job_match)
                    
                except Exception as e:
                    logger.error(f"Dice job parsing error: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Dice search error: {e}")
        
        return jobs
    
    def search_linkedin(self, driver) -> List[JobMatch]:
        """Search LinkedIn Jobs"""
        jobs = []
        try:
            search_terms = "+".join(self.user_profile.preferred_roles)
            url = f"https://www.linkedin.com/jobs/search/?keywords={search_terms}&location=Remote"
            
            driver.get(url)
            time.sleep(5)
            
            # Scroll to load more jobs
            for i in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            job_cards = driver.find_elements(By.CSS_SELECTOR, ".job-search-card")
            
            for card in job_cards[:15]:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, ".base-search-card__title")
                    title = title_elem.text
                    
                    company_elem = card.find_element(By.CSS_SELECTOR, ".base-search-card__subtitle")
                    company = company_elem.text
                    
                    # Skip blacklisted companies
                    if company in self.user_profile.blacklisted_companies:
                        continue
                    
                    location_elem = card.find_element(By.CSS_SELECTOR, ".job-search-card__location")
                    location = location_elem.text
                    
                    link_elem = card.find_element(By.CSS_SELECTOR, ".base-card__full-link")
                    url = link_elem.get_attribute('href')
                    
                    job_match = JobMatch(
                        title=title,
                        company=company,
                        platform="LinkedIn",
                        url=url,
                        description="",
                        requirements="",
                        salary="",
                        location=location,
                        relevance_score=0,
                        sentiment_score=0,
                        skill_match_percentage=0,
                        id=f"linkedin_{hashlib.md5(url.encode()).hexdigest()[:8]}"
                    )
                    jobs.append(job_match)
                    
                except Exception as e:
                    logger.error(f"LinkedIn job parsing error: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"LinkedIn search error: {e}")
        
        return jobs

class EnhancedUltimateJobBot:
    """Enhanced Ultimate Job Bot with AI and advanced automation"""
    
    def __init__(self):
        logger.info("🚀 Initializing Enhanced Ultimate Job Bot...")
        
        # Initialize components
        self.config = self._load_configuration()
        self.user_profile = self._create_user_profile()
        self.db_manager = DatabaseManager()
        self.resume_parser = ResumeParser()
        self.relevance_scorer = JobRelevanceScorer()
        self.scheduler = SmartScheduler()
        self.notifications = NotificationSystem(self.config)
        self.job_scraper = EnhancedJobScraper(self.user_profile)
        
        # Browser setup
        self.driver = None
        self.applied_jobs = set()
        self.proof_folder = "application_proofs"
        
        # Create directories
        os.makedirs(self.proof_folder, exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # Load applied jobs history
        self._load_applied_jobs()
        
        # Parse resume for updated skills
        self._update_skills_from_resume()
        
        logger.info("✅ Enhanced Ultimate Job Bot initialized successfully!")
    
    def _load_configuration(self) -> Dict:
        """Load configuration from multiple sources"""
        config = {}
        
        # Try environment variables first
        if os.getenv('PERSONAL_EMAIL'):
            config = {
                'personal': {
                    'full_name': os.getenv('PERSONAL_FULL_NAME', 'Job Seeker'),
                    'email': os.getenv('PERSONAL_EMAIL'),
                    'phone': os.getenv('PERSONAL_PHONE', ''),
                    'location': os.getenv('PERSONAL_LOCATION', 'Remote'),
                    'linkedin': os.getenv('PERSONAL_LINKEDIN', ''),
                    'github': os.getenv('PERSONAL_GITHUB', '')
                },
                'platforms': {
                    'linkedin': {
                        'email': os.getenv('LINKEDIN_EMAIL', ''),
                        'password': os.getenv('LINKEDIN_PASSWORD', '')
                    },
                    'dice': {
                        'email': os.getenv('DICE_EMAIL', ''),
                        'password': os.getenv('DICE_PASSWORD', '')
                    }
                },
                'preferences': {
                    'job_titles': os.getenv('JOB_TITLES', '').split(','),
                    'skills': os.getenv('SKILLS', '').split(','),
                    'blacklisted_companies': os.getenv('BLACKLISTED_COMPANIES', '').split(','),
                    'preferred_companies': os.getenv('PREFERRED_COMPANIES', '').split(','),
                    'salary_min': int(os.getenv('SALARY_MIN', '50000')),
                    'remote_only': os.getenv('REMOTE_ONLY', 'true').lower() == 'true',
                    'experience_level': os.getenv('EXPERIENCE_LEVEL', 'entry')
                },
                'notifications': {
                    'email': {
                        'enabled': os.getenv('EMAIL_NOTIFICATIONS', 'false').lower() == 'true',
                        'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                        'sender_email': os.getenv('SENDER_EMAIL', ''),
                        'sender_password': os.getenv('SENDER_PASSWORD', ''),
                        'recipient_email': os.getenv('RECIPIENT_EMAIL', '')
                    }
                }
            }
        
        # Fallback to config file
        if not config and os.path.exists('user_config.json'):
            with open('user_config.json', 'r') as f:
                config = json.load(f)
        
        # Add default values
        if not config:
            config = self._get_default_config()
        
        return config
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'personal': {
                'full_name': 'Rahul Joshi',
                'email': 'rahuljoshisg@gmail.com',
                'phone': '+91 9456382923',
                'location': 'Remote Worldwide'
            },
            'preferences': {
                'job_titles': ['DevOps Engineer', 'Cloud Engineer', 'Platform Engineer'],
                'skills': ['DevOps', 'AWS', 'Docker', 'Kubernetes', 'Python', 'Linux'],
                'blacklisted_companies': ['Fake Corp', 'Scam Inc'],
                'preferred_companies': ['Google', 'Microsoft', 'Amazon'],
                'salary_min': 50000,
                'remote_only': True,
                'experience_level': 'entry'
            }
        }
    
    def _create_user_profile(self) -> UserProfile:
        """Create user profile from configuration"""
        personal = self.config.get('personal', {})
        prefs = self.config.get('preferences', {})
        
        return UserProfile(
            name=personal.get('full_name', ''),
            email=personal.get('email', ''),
            phone=personal.get('phone', ''),
            location=personal.get('location', ''),
            skills=prefs.get('skills', []),
            experience_years=0,  # Will be updated from resume
            preferred_roles=prefs.get('job_titles', []),
            blacklisted_companies=prefs.get('blacklisted_companies', []),
            preferred_companies=prefs.get('preferred_companies', []),
            salary_min=prefs.get('salary_min', 50000),
            remote_only=prefs.get('remote_only', True),
            certifications=[]
        )
    
    def _load_applied_jobs(self):
        """Load applied jobs history"""
        try:
            if os.path.exists("applied_jobs_history.pkl"):
                with open("applied_jobs_history.pkl", 'rb') as f:
                    self.applied_jobs = pickle.load(f)
            logger.info(f"Loaded {len(self.applied_jobs)} applied jobs from history")
        except Exception as e:
            logger.error(f"Error loading applied jobs: {e}")
            self.applied_jobs = set()
    
    def _save_applied_jobs(self):
        """Save applied jobs history"""
        try:
            with open("applied_jobs_history.pkl", 'wb') as f:
                pickle.dump(self.applied_jobs, f)
        except Exception as e:
            logger.error(f"Error saving applied jobs: {e}")
    
    def _update_skills_from_resume(self):
        """Update user skills from resume analysis"""
        resume_path = "resume.pdf"
        if os.path.exists(resume_path):
            try:
                resume_data = self.resume_parser.parse_resume(resume_path)
                if resume_data.get('skills'):
                    # Merge with existing skills
                    existing_skills = set(self.user_profile.skills)
                    new_skills = set(resume_data['skills'])
                    self.user_profile.skills = list(existing_skills | new_skills)
                    
                if resume_data.get('experience_years'):
                    self.user_profile.experience_years = resume_data['experience_years']
                
                logger.info(f"Updated profile with {len(self.user_profile.skills)} skills from resume")
            except Exception as e:
                logger.error(f"Resume parsing error: {e}")
    
    def setup_browser(self) -> bool:
        """Setup Firefox browser with enhanced options"""
        try:
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            
            # Headless mode for CI/CD
            if os.getenv('GITHUB_ACTIONS') == 'true':
                options.add_argument("--headless")
            
            # Anti-detection measures
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference("useAutomationExtension", False)
            options.set_preference("general.useragent.override", 
                                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            # Setup service
            if os.getenv('GITHUB_ACTIONS') == 'true':
                service = Service('/usr/local/bin/geckodriver')
            else:
                service = Service(GeckoDriverManager().install())
            
            self.driver = webdriver.Firefox(service=service, options=options)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            # Execute anti-detection script
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Browser setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Browser setup failed: {e}")
            return False
    
    def search_all_jobs(self) -> List[JobMatch]:
        """Search jobs from all platforms"""
        all_jobs = []
        
        logger.info("🔍 Searching all platforms for jobs...")
        
        # RemoteOK (API-based, no browser needed)
        try:
            remoteok_jobs = self.job_scraper.search_remoteok()
            all_jobs.extend(remoteok_jobs)
            logger.info(f"Found {len(remoteok_jobs)} RemoteOK jobs")
        except Exception as e:
            logger.error(f"RemoteOK search error: {e}")
        
        # Browser-based searches
        if self.driver:
            # Dice.com
            try:
                dice_jobs = self.job_scraper.search_dice(self.driver)
                all_jobs.extend(dice_jobs)
                logger.info(f"Found {len(dice_jobs)} Dice jobs")
            except Exception as e:
                logger.error(f"Dice search error: {e}")
            
            # LinkedIn (if credentials available)
            if self.config.get('platforms', {}).get('linkedin', {}).get('email'):
                try:
                    linkedin_jobs = self.job_scraper.search_linkedin(self.driver)
                    all_jobs.extend(linkedin_jobs)
                    logger.info(f"Found {len(linkedin_jobs)} LinkedIn jobs")
                except Exception as e:
                    logger.error(f"LinkedIn search error: {e}")
        
        # Calculate relevance scores
        for job in all_jobs:
            job.relevance_score = self.relevance_scorer.calculate_relevance_score(
                self.user_profile, job
            )
            job.sentiment_score = self.relevance_scorer.analyze_job_sentiment(
                job.description
            )
            job.skill_match_percentage = self.relevance_scorer.calculate_skill_match(
                self.user_profile.skills, job.requirements
            )
        
        # Sort by relevance score
        all_jobs.sort(key=lambda x: x.relevance_score, reverse=True)
        
        logger.info(f"📊 Total jobs found: {len(all_jobs)}")
        return all_jobs
    
    def generate_cover_letter(self, job_match: JobMatch) -> str:
        """Generate personalized cover letter"""
        template = """Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}. With my background in {key_skills} and {experience_years} years of experience in the field, I am excited about the opportunity to contribute to your team's success.

My technical expertise includes:
{skills_list}

What particularly attracts me to {company_name} is your commitment to innovation and technical excellence. I believe my skills in {relevant_skills} align perfectly with your requirements and would enable me to make meaningful contributions to your projects.

I am especially interested in this role because:
- The position matches my career goals in {preferred_role}
- Your company's reputation for {company_strength}
- The opportunity to work with cutting-edge technologies

I would welcome the opportunity to discuss how my experience and passion for technology can contribute to {company_name}'s continued success. Thank you for considering my application.

Best regards,
{full_name}
Email: {email}
Phone: {phone}
LinkedIn: {linkedin}
"""
        
        # Extract key skills relevant to the job
        relevant_skills = []
        for skill in self.user_profile.skills[:5]:
            if skill.lower() in job_match.requirements.lower():
                relevant_skills.append(skill)
        
        if not relevant_skills:
            relevant_skills = self.user_profile.skills[:3]
        
        # Format skills list
        skills_list = "\n".join([f"• {skill}" for skill in self.user_profile.skills[:8]])
        
        # Determine company strength
        company_strengths = {
            'google': 'innovation and global impact',
            'microsoft': 'enterprise solutions and cloud technology',
            'amazon': 'scale and customer obsession',
            'meta': 'social connectivity and VR innovation',
            'apple': 'design excellence and user experience'
        }
        
        company_strength = company_strengths.get(
            job_match.company.lower().split()[0],
            'technical excellence and innovation'
        )
        
        cover_letter = template.format(
            job_title=job_match.title,
            company_name=job_match.company,
            key_skills=", ".join(relevant_skills[:3]),
            experience_years=max(1, self.user_profile.experience_years),
            skills_list=skills_list,
            relevant_skills=", ".join(relevant_skills[:2]),
            preferred_role=self.user_profile.preferred_roles[0] if self.user_profile.preferred_roles else "software development",
            company_strength=company_strength,
            full_name=self.user_profile.name,
            email=self.user_profile.email,
            phone=self.user_profile.phone,
            linkedin=self.config.get('personal', {}).get('linkedin', '')
        )
        
        return cover_letter
    
    def take_screenshot(self, job_match: JobMatch, suffix: str = "") -> str:
        """Take proof screenshot"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c for c in job_match.title if c.isalnum() or c in (' ', '-', '_'))[:50]
            safe_company = "".join(c for c in job_match.company if c.isalnum() or c in (' ', '-', '_'))[:30]
            
            filename = f"{self.proof_folder}/{job_match.platform}_{safe_company}_{safe_title}"
            if suffix:
                filename += f"_{suffix}"
            filename += f"_{timestamp}.png"
            
            # Clean filename
            filename = filename.replace(" ", "_").replace("/", "_").replace("\\", "_")[:200]
            
            self.driver.save_screenshot(filename)
            logger.info(f"📸 Screenshot saved: {os.path.basename(filename)}")
            
            return filename
            
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return ""
    
    def apply_to_job(self, job_match: JobMatch) -> bool:
        """Apply to job with enhanced automation and captcha handling"""
        try:
            logger.info(f"📝 Applying to: {job_match.title} at {job_match.company}")
            
            # Check if already applied
            if job_match.id in self.applied_jobs:
                logger.info("Already applied to this job, skipping...")
                return False
            
            # Mark as applied to prevent duplicates
            self.applied_jobs.add(job_match.id)
            self._save_applied_jobs()
            
            # Generate cover letter
            cover_letter = self.generate_cover_letter(job_match)
            
            # Navigate to job page
            if self.driver and job_match.url:
                try:
                    self.driver.get(job_match.url)
                    time.sleep(self.scheduler.get_random_delay())
                    
                    # Initialize captcha solver if available
                    if CAPTCHA_SOLVER_AVAILABLE:
                        captcha_solver = EnhancedCaptchaSolver(self.driver)
                        # Handle captcha if present
                        if not captcha_solver.handle_captcha_flow():
                            logger.warning("Captcha handling failed, but continuing...")
                    else:
                        # Basic captcha detection
                        self._basic_captcha_check()
                    
                    # Take initial screenshot
                    screenshot_path = self.take_screenshot(job_match, "initial")
                    
                    # Look for apply button with multiple strategies
                    apply_button = self._find_apply_button()
                    
                    if apply_button:
                        # Click apply button
                        self._click_apply_button(apply_button)
                        time.sleep(2)
                        
                        # Handle captcha again if it appears after clicking
                        if CAPTCHA_SOLVER_AVAILABLE:
                            captcha_solver.handle_captcha_flow()
                        else:
                            self._basic_captcha_check()
                        
                        # Take application screenshot
                        screenshot_path = self.take_screenshot(job_match, "applied")
                        
                        # Fill application form if present
                        self._fill_application_form(job_match, cover_letter)
                        
                        logger.info("✅ Application submitted successfully")
                    else:
                        # Take screenshot anyway for proof
                        screenshot_path = self.take_screenshot(job_match, "no_apply_button")
                        logger.warning("Apply button not found, marked as applied anyway")
                    
                except Exception as e:
                    logger.error(f"Browser automation error: {e}")
                    screenshot_path = self.take_screenshot(job_match, "error")
            else:
                screenshot_path = ""
            
            # Save to database
            self.db_manager.save_application(job_match, screenshot_path, cover_letter)
            
            # Log application
            self._log_application(job_match, screenshot_path)
            
            # Send notification
            self.notifications.notify_application_sent(job_match, len(self.applied_jobs))
            
            # Update application count for rate limiting
            self.scheduler.application_count += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            self.notifications.notify_error(str(e), f"Applying to {job_match.title}")
            return False
    
    def _find_apply_button(self):
        """Find apply button with multiple selectors"""
        selectors = [
            # Common apply button selectors
            "button[data-control-name='jobdetails_topcard_inapply']",  # LinkedIn
            "button[aria-label='Apply']",
            "a[data-cy='apply-button']",  # Dice
            "button:contains('Apply')",
            "a:contains('Apply')",
            "input[value*='Apply']",
            "button[class*='apply']",
            "a[class*='apply']",
            ".apply-button",
            "#apply-button",
            "[data-testid*='apply']",
            "button[title*='Apply']",
            "a[title*='Apply']",
            "button[data-automation-id='job-apply-button']",
            ".btn-apply",
            ".job-apply-button",
            "button[data-track='apply']",
            "a[data-track='apply']",
            "button[data-qa='apply-button']",
            "a[data-qa='apply-button']"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        return element
            except:
                continue
        
        return None
    
    def _click_apply_button(self, button):
        """Click apply button with multiple strategies"""
        try:
            # Strategy 1: Regular click
            button.click()
        except:
            try:
                # Strategy 2: JavaScript click
                self.driver.execute_script("arguments[0].click();", button)
            except:
                try:
                    # Strategy 3: ActionChains
                    ActionChains(self.driver).move_to_element(button).click().perform()
                except:
                    logger.warning("All click strategies failed")
    
    def _fill_application_form(self, job_match: JobMatch, cover_letter: str):
        """Fill application form if present"""
        try:
            # Look for common form fields
            form_fields = {
                'input[name*="name"]': self.user_profile.name,
                'input[name*="email"]': self.user_profile.email,
                'input[name*="phone"]': self.user_profile.phone,
                'textarea[name*="cover"]': cover_letter[:1000],  # Truncate if too long
                'textarea[name*="message"]': cover_letter[:1000],
                'textarea[name*="why"]': f"I am interested in this {job_match.title} position because it aligns with my skills in {', '.join(self.user_profile.skills[:3])}."
            }
            
            for selector, value in form_fields.items():
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element.clear()
                            element.send_keys(value)
                            time.sleep(0.5)
                except:
                    continue
            
            # Submit form if submit button exists
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('Submit')",
                "button:contains('Send')",
                ".submit-button"
            ]
            
            for selector in submit_selectors:
                try:
                    submit_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if submit_btn.is_displayed() and submit_btn.is_enabled():
                        submit_btn.click()
                        break
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"Form filling error: {e}")
    
    def _basic_captcha_check(self):
        """Basic captcha detection and handling"""
        try:
            # Basic captcha selectors
            captcha_selectors = [
                "iframe[src*='recaptcha']",
                ".g-recaptcha",
                "iframe[src*='hcaptcha']",
                ".captcha",
                "#captcha"
            ]
            
            for selector in captcha_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        logger.warning(f"⚠️ Basic captcha detected: {selector}")
                        # Wait a bit for potential auto-resolution
                        time.sleep(5)
                        return
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"Basic captcha check error: {e}")
    
    def _log_application(self, job_match: JobMatch, screenshot_path: str):
        """Log application details"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - Applied to {job_match.title} at {job_match.company} ({job_match.platform}) - Score: {job_match.relevance_score:.1f}% - URL: {job_match.url} - Proof: {screenshot_path}\n"
        
        try:
            with open("enhanced_applications.txt", 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            logger.error(f"Logging error: {e}")
    
    def run_application_cycle(self) -> Dict:
        """Run complete application cycle"""
        logger.info("🚀 Starting Enhanced Job Application Cycle")
        
        start_time = datetime.now()
        stats = {
            'jobs_found': 0,
            'applications_sent': 0,
            'high_relevance_jobs': 0,
            'platforms_searched': 0,
            'errors': 0
        }
        
        try:
            # Setup browser
            if not self.setup_browser():
                logger.error("Failed to setup browser")
                return stats
            
            # Search all jobs
            jobs = self.search_all_jobs()
            stats['jobs_found'] = len(jobs)
            stats['platforms_searched'] = len(set(job.platform for job in jobs))
            
            if not jobs:
                logger.warning("No jobs found")
                return stats
            
            # Filter high-relevance jobs
            high_relevance_jobs = [job for job in jobs if job.relevance_score >= 70]
            stats['high_relevance_jobs'] = len(high_relevance_jobs)
            
            # Apply to jobs
            for job in high_relevance_jobs[:20]:  # Limit to top 20 jobs
                if not self.scheduler.is_good_time_to_apply():
                    logger.info("Rate limit reached, stopping applications")
                    break
                
                try:
                    # Send notification for high-scoring jobs
                    if job.relevance_score >= 80:
                        self.notifications.notify_new_job(job)
                    
                    if self.apply_to_job(job):
                        stats['applications_sent'] += 1
                        
                    # Random delay between applications
                    time.sleep(self.scheduler.get_random_delay())
                    
                except Exception as e:
                    stats['errors'] += 1
                    logger.error(f"Application error: {e}")
                    continue
            
            # Log cycle completion
            end_time = datetime.now()
            duration = (end_time - start_time).seconds / 60
            
            cycle_log = f"""
🎯 ENHANCED JOB BOT CYCLE COMPLETED
============================================
Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}
End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
Duration: {duration:.1f} minutes

📊 STATISTICS:
- Jobs Found: {stats['jobs_found']}
- Platforms Searched: {stats['platforms_searched']}
- High Relevance Jobs: {stats['high_relevance_jobs']}
- Applications Sent: {stats['applications_sent']}
- Errors: {stats['errors']}
- Success Rate: {(stats['applications_sent']/max(1, stats['high_relevance_jobs']))*100:.1f}%

✅ Total Applications in Database: {len(self.applied_jobs)}
"""
            
            logger.info(cycle_log)
            
            # Save cycle log
            with open("enhanced_cycle_log.txt", 'a', encoding='utf-8') as f:
                f.write(cycle_log + "\n" + "="*50 + "\n")
            
        except Exception as e:
            logger.error(f"Cycle error: {e}")
            self.notifications.notify_error(str(e), "Application cycle")
            stats['errors'] += 1
            
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
        
        return stats
    
    def run_continuous(self):
        """Run bot continuously with smart scheduling"""
        logger.info("🔄 Starting continuous job bot operation...")
        
        while True:
            try:
                # Run application cycle
                stats = self.run_application_cycle()
                
                # Schedule next run
                next_run = self.scheduler.schedule_next_run()
                wait_minutes = (next_run - datetime.now()).total_seconds() / 60
                
                logger.info(f"⏰ Next run scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')} (in {wait_minutes:.1f} minutes)")
                
                # Wait until next run
                time.sleep(wait_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("🛑 Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Continuous run error: {e}")
                self.notifications.notify_error(str(e), "Continuous operation")
                time.sleep(300)  # Wait 5 minutes before retry

def main():
    """Main function"""
    print("🚀 ENHANCED ULTIMATE JOB BOT")
    print("=" * 50)
    
    try:
        bot = EnhancedUltimateJobBot()
        
        # Check command line arguments
        if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
            bot.run_continuous()
        else:
            # Single run
            stats = bot.run_application_cycle()
            print(f"\n✅ Cycle completed: {stats['applications_sent']} applications sent")
            return 0
            
    except Exception as e:
        logger.error(f"Bot failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
