#!/usr/bin/env python3
"""
🚀 ENHANCED RESUME MATCHING BOT - AI-Powered Resume Analysis
Features advanced resume-to-job matching with percentage scores
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
import re
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin, urlparse
import threading
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Set
import traceback

# Enhanced imports for resume analysis
try:
    import PyPDF2
    import docx
    from docx import Document
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("WARNING: PDF/DOCX processing not available")

# NLP and matching libraries
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    print("WARNING: NLTK not available - using basic matching")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("WARNING: scikit-learn not available - using basic matching")

# Optional imports with fallbacks
try:
    import schedule
except ImportError:
    schedule = None

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

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

# Configure comprehensive logging
log_handlers = []
try:
    log_handlers.append(logging.FileHandler('enhanced_resume_matching_bot.log', encoding='utf-8'))
except:
    pass
log_handlers.append(logging.StreamHandler())

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=log_handlers
)
logger = logging.getLogger(__name__)

@dataclass
class ResumeProfile:
    """Enhanced resume profile with detailed analysis"""
    full_text: str = ""
    skills: List[str] = None
    experience_years: int = 0
    education: List[str] = None
    certifications: List[str] = None
    projects: List[str] = None
    technologies: List[str] = None
    soft_skills: List[str] = None
    contact_info: Dict[str, str] = None
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.education is None:
            self.education = []
        if self.certifications is None:
            self.certifications = []
        if self.projects is None:
            self.projects = []
        if self.technologies is None:
            self.technologies = []
        if self.soft_skills is None:
            self.soft_skills = []
        if self.contact_info is None:
            self.contact_info = {}

@dataclass
class JobMatch:
    """Enhanced job match with resume matching analysis"""
    title: str
    company: str
    platform: str
    url: str
    salary: str = ""
    location: str = ""
    description: str = ""
    requirements: str = ""
    preferred_qualifications: str = ""
    technologies_required: List[str] = None
    experience_required: str = ""
    education_required: str = ""
    
    # Matching analysis
    overall_match_percentage: float = 0.0
    skills_match_percentage: float = 0.0
    experience_match_percentage: float = 0.0
    technology_match_percentage: float = 0.0
    education_match_percentage: float = 0.0
    
    # Detailed breakdown
    matched_skills: List[str] = None
    missing_skills: List[str] = None
    matched_technologies: List[str] = None
    missing_technologies: List[str] = None
    
    salary_min: int = 0
    salary_max: int = 0
    id: str = ""
    apply_url: Optional[str] = None
    remote_friendly: bool = True
    
    def __post_init__(self):
        if self.technologies_required is None:
            self.technologies_required = []
        if self.matched_skills is None:
            self.matched_skills = []
        if self.missing_skills is None:
            self.missing_skills = []
        if self.matched_technologies is None:
            self.matched_technologies = []
        if self.missing_technologies is None:
            self.missing_technologies = []

class ResumeAnalyzer:
    """Advanced resume analysis and matching engine"""
    
    def __init__(self):
        self.resume_profile = None
        self.skill_keywords = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 'ruby', 'php', 'swift', 'kotlin'],
            'cloud': ['aws', 'azure', 'gcp', 'google cloud', 'amazon web services', 'microsoft azure'],
            'devops': ['docker', 'kubernetes', 'jenkins', 'gitlab', 'github actions', 'terraform', 'ansible', 'puppet', 'chef'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'dynamodb', 'oracle'],
            'web': ['react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring'],
            'tools': ['git', 'jira', 'confluence', 'slack', 'linux', 'windows', 'macos'],
            'methodologies': ['agile', 'scrum', 'kanban', 'devops', 'ci/cd', 'tdd', 'microservices']
        }
        
        # Initialize NLP components if available
        if NLP_AVAILABLE:
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('wordnet', quiet=True)
                self.lemmatizer = WordNetLemmatizer()
                self.stop_words = set(stopwords.words('english'))
            except:
                self.lemmatizer = None
                self.stop_words = set()
        else:
            self.lemmatizer = None
            self.stop_words = set()
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF resume"""
        try:
            if not PDF_AVAILABLE:
                logger.warning("PDF processing not available")
                return ""
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            return ""
    
    def extract_text_from_docx(self, docx_path: str) -> str:
        """Extract text from DOCX resume"""
        try:
            if not PDF_AVAILABLE:
                logger.warning("DOCX processing not available")
                return ""
            
            doc = Document(docx_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from DOCX: {e}")
            return ""
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces and periods
        text = re.sub(r'[^\w\s\.]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using keyword matching"""
        skills = []
        text_lower = text.lower()
        
        # Check all skill categories
        for category, keywords in self.skill_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    skills.append(keyword.title())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in skills:
            if skill.lower() not in seen:
                seen.add(skill.lower())
                unique_skills.append(skill)
        
        return unique_skills
    
    def extract_experience_years(self, text: str) -> int:
        """Extract years of experience from resume text"""
        try:
            # Look for patterns like "3 years", "5+ years", "2-4 years"
            patterns = [
                r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
                r'(\d+)\s*-\s*\d+\s*years?\s*(?:of\s*)?(?:experience|exp)',
                r'(?:experience|exp).*?(\d+)\+?\s*years?',
                r'(\d+)\+?\s*yrs?\s*(?:of\s*)?(?:experience|exp)'
            ]
            
            years = []
            for pattern in patterns:
                matches = re.finditer(pattern, text.lower())
                for match in matches:
                    years.append(int(match.group(1)))
            
            # Return the highest number found, or estimate based on text length
            if years:
                return max(years)
            
            # Fallback: estimate based on content richness
            if len(text) > 3000:
                return 5  # Senior level
            elif len(text) > 2000:
                return 3  # Mid level
            else:
                return 1  # Junior level
                
        except Exception as e:
            logger.error(f"Failed to extract experience years: {e}")
            return 2  # Default
    
    def extract_education(self, text: str) -> List[str]:
        """Extract education information"""
        education = []
        text_lower = text.lower()
        
        # Common degree patterns
        degree_patterns = [
            r'\b(?:bachelor|b\.?[as]\.?|bs|ba)\b.*?(?:computer science|engineering|technology|science)',
            r'\b(?:master|m\.?[as]\.?|ms|ma|mtech|mba)\b.*?(?:computer science|engineering|technology|business)',
            r'\b(?:phd|ph\.?d\.?|doctorate)\b',
            r'\b(?:associate|diploma|certificate)\b.*?(?:computer|technology|engineering)'
        ]
        
        for pattern in degree_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                education.append(match.group().title())
        
        return education
    
    def extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        certifications = []
        text_lower = text.lower()
        
        # Common certifications
        cert_patterns = [
            r'\baws\s+(?:certified|certification)\b.*?(?:solutions architect|developer|sysops|devops)',
            r'\bazure\s+(?:certified|certification)\b.*?(?:administrator|developer|architect)',
            r'\bgcp\s+(?:certified|certification)\b.*?(?:engineer|architect)',
            r'\bcisco\s+(?:ccna|ccnp|ccie)\b',
            r'\bcompTIA\s+(?:security\+|network\+|a\+)\b',
            r'\bkubernetes\s+(?:certified|certification)\b',
            r'\bdocker\s+(?:certified|certification)\b',
            r'\bjenkins\s+(?:certified|certification)\b'
        ]
        
        for pattern in cert_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                certifications.append(match.group().title())
        
        return certifications
    
    def analyze_resume(self, resume_path: str) -> ResumeProfile:
        """Analyze resume and create comprehensive profile"""
        try:
            logger.info(f"📄 Analyzing resume: {resume_path}")
            
            # Extract text based on file type
            text = ""
            if resume_path.lower().endswith('.pdf'):
                text = self.extract_text_from_pdf(resume_path)
            elif resume_path.lower().endswith('.docx'):
                text = self.extract_text_from_docx(resume_path)
            else:
                logger.warning("Unsupported resume format, using default profile")
                return self._get_default_profile()
            
            if not text:
                logger.warning("No text extracted from resume, using default profile")
                return self._get_default_profile()
            
            # Preprocess text
            processed_text = self.preprocess_text(text)
            
            # Extract various components
            skills = self.extract_skills(text)
            experience_years = self.extract_experience_years(text)
            education = self.extract_education(text)
            certifications = self.extract_certifications(text)
            
            # Extract contact info
            contact_info = self._extract_contact_info(text)
            
            # Create profile
            profile = ResumeProfile(
                full_text=text,
                skills=skills,
                experience_years=experience_years,
                education=education,
                certifications=certifications,
                technologies=skills,  # Technologies are part of skills
                contact_info=contact_info
            )
            
            logger.info(f"✅ Resume analysis complete:")
            logger.info(f"   Skills found: {len(skills)}")
            logger.info(f"   Experience: {experience_years} years")
            logger.info(f"   Education: {len(education)} entries")
            logger.info(f"   Certifications: {len(certifications)}")
            
            self.resume_profile = profile
            return profile
            
        except Exception as e:
            logger.error(f"❌ Resume analysis failed: {e}")
            return self._get_default_profile()
    
    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from resume"""
        contact = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact['email'] = email_match.group()
        
        # Phone pattern
        phone_pattern = r'(?:\+\d{1,3}\s?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact['phone'] = phone_match.group()
        
        # LinkedIn pattern
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, text.lower())
        if linkedin_match:
            contact['linkedin'] = linkedin_match.group()
        
        return contact
    
    def _get_default_profile(self) -> ResumeProfile:
        """Get default resume profile"""
        return ResumeProfile(
            skills=["Python", "Java", "JavaScript", "AWS", "Docker", "Kubernetes", "Jenkins", "GitLab", "CI/CD", "DevOps"],
            experience_years=3,
            education=["Bachelor's in Computer Science"],
            certifications=["AWS Certified Developer"],
            technologies=["Python", "AWS", "Docker", "Kubernetes"],
            contact_info={"email": "rahuljoshisg@gmail.com"}
        )
    
    def calculate_job_match(self, job: JobMatch, resume_profile: ResumeProfile) -> JobMatch:
        """Calculate comprehensive job matching score"""
        try:
            # Extract job requirements
            job_text = f"{job.title} {job.description} {job.requirements}"
            job_skills = self.extract_skills(job_text)
            
            # Calculate skill matching
            skills_match = self._calculate_skills_match(resume_profile.skills, job_skills)
            
            # Calculate technology matching
            tech_match = self._calculate_technology_match(resume_profile.technologies, job_skills)
            
            # Calculate experience matching
            exp_match = self._calculate_experience_match(resume_profile.experience_years, job.experience_required)
            
            # Calculate education matching
            edu_match = self._calculate_education_match(resume_profile.education, job.education_required)
            
            # Calculate overall match (weighted average)
            overall_match = (
                skills_match['percentage'] * 0.4 +  # 40% weight on skills
                tech_match['percentage'] * 0.3 +   # 30% weight on technology
                exp_match * 0.2 +                  # 20% weight on experience
                edu_match * 0.1                    # 10% weight on education
            )
            
            # Update job match object
            job.overall_match_percentage = round(overall_match, 1)
            job.skills_match_percentage = round(skills_match['percentage'], 1)
            job.technology_match_percentage = round(tech_match['percentage'], 1)
            job.experience_match_percentage = round(exp_match, 1)
            job.education_match_percentage = round(edu_match, 1)
            
            job.matched_skills = skills_match['matched']
            job.missing_skills = skills_match['missing']
            job.matched_technologies = tech_match['matched']
            job.missing_technologies = tech_match['missing']
            
            return job
            
        except Exception as e:
            logger.error(f"❌ Job matching calculation failed: {e}")
            # Set default values
            job.overall_match_percentage = 75.0
            job.skills_match_percentage = 75.0
            return job
    
    def _calculate_skills_match(self, resume_skills: List[str], job_skills: List[str]) -> Dict:
        """Calculate skills matching percentage"""
        if not resume_skills or not job_skills:
            return {'percentage': 0.0, 'matched': [], 'missing': job_skills or []}
        
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        matched = []
        missing = []
        
        for job_skill in job_skills:
            if job_skill.lower() in resume_skills_lower:
                matched.append(job_skill)
            else:
                missing.append(job_skill)
        
        percentage = (len(matched) / len(job_skills)) * 100 if job_skills else 0
        
        return {
            'percentage': percentage,
            'matched': matched,
            'missing': missing
        }
    
    def _calculate_technology_match(self, resume_tech: List[str], job_tech: List[str]) -> Dict:
        """Calculate technology matching percentage"""
        return self._calculate_skills_match(resume_tech, job_tech)
    
    def _calculate_experience_match(self, resume_years: int, job_experience: str) -> float:
        """Calculate experience matching percentage"""
        try:
            if not job_experience:
                return 100.0  # No specific requirement
            
            # Extract years from job requirement
            years_pattern = r'(\d+)\+?\s*years?'
            match = re.search(years_pattern, job_experience.lower())
            
            if match:
                required_years = int(match.group(1))
                if resume_years >= required_years:
                    return 100.0
                elif resume_years >= required_years * 0.8:  # 80% of required
                    return 85.0
                elif resume_years >= required_years * 0.6:  # 60% of required
                    return 70.0
                else:
                    return 50.0
            
            # Default based on experience level
            if 'senior' in job_experience.lower() and resume_years >= 5:
                return 100.0
            elif 'mid' in job_experience.lower() and resume_years >= 2:
                return 100.0
            elif 'junior' in job_experience.lower() or 'entry' in job_experience.lower():
                return 100.0
            
            return 75.0  # Default
            
        except Exception:
            return 75.0
    
    def _calculate_education_match(self, resume_education: List[str], job_education: str) -> float:
        """Calculate education matching percentage"""
        try:
            if not job_education or not resume_education:
                return 100.0  # No specific requirement or no education info
            
            job_education_lower = job_education.lower()
            resume_education_text = ' '.join(resume_education).lower()
            
            # Check for degree requirements
            if 'bachelor' in job_education_lower and 'bachelor' in resume_education_text:
                return 100.0
            elif 'master' in job_education_lower and 'master' in resume_education_text:
                return 100.0
            elif 'phd' in job_education_lower and 'phd' in resume_education_text:
                return 100.0
            elif any(degree in resume_education_text for degree in ['bachelor', 'master', 'phd']):
                return 90.0  # Has some relevant degree
            
            return 75.0  # Default
            
        except Exception:
            return 75.0

class EnhancedResumeMatchingBot:
    """Enhanced job bot with advanced resume matching capabilities"""
    
    def __init__(self):
        """Initialize with resume analysis capabilities"""
        logger.info("🚀 Initializing ENHANCED RESUME MATCHING BOT...")
        
        try:
            self.start_time = datetime.now()
            self.driver = None
            self.proof_folder = "application_proofs"
            self.target_applications = (70, 90)
            self.applications_sent = 0
            
            # Enhanced file management
            timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
            self.applications_file = f"enhanced_resume_matching_applications_{timestamp}.txt"
            self.cycle_log_file = f"enhanced_resume_matching_cycle_{timestamp}.txt"
            self.screenshot_count = 0
            
            # Create directories
            Path(self.proof_folder).mkdir(exist_ok=True)
            Path("logs").mkdir(exist_ok=True)
            
            # Initialize resume analyzer
            self.resume_analyzer = ResumeAnalyzer()
            
            # Load and analyze resume
            self.resume_profile = self._load_resume_profile()
            
            # Load configuration
            self.config = self._load_configuration()
            self.applied_jobs = set()
            
            # Enhanced session
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            # Platform configurations
            self.platforms = {
                'RemoteOK': {'url': 'https://remoteok.io/api', 'enabled': True},
                'X/Twitter': {'enabled': True, 'template': True},
                'DICE': {'enabled': True, 'template': True},
                'Indeed': {'enabled': True, 'template': True},
                'WeWorkRemotely': {'enabled': True, 'template': True},
                'Turing': {'enabled': True, 'template': True}
            }
            
            logger.info("✅ ENHANCED RESUME MATCHING BOT initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def _load_resume_profile(self) -> ResumeProfile:
        """Load and analyze resume"""
        try:
            # Look for resume files
            resume_files = ['resume.pdf', 'cv.pdf', 'resume.docx', 'cv.docx']
            
            for resume_file in resume_files:
                if os.path.exists(resume_file):
                    return self.resume_analyzer.analyze_resume(resume_file)
            
            logger.warning("No resume file found, using default profile")
            return self.resume_analyzer._get_default_profile()
            
        except Exception as e:
            logger.error(f"❌ Resume loading failed: {e}")
            return self.resume_analyzer._get_default_profile()
    
    def _load_configuration(self):
        """Load enhanced configuration"""
        return {
            'personal': {
                'full_name': os.getenv('PERSONAL_FULL_NAME', 'Rahul Joshi'),
                'email': os.getenv('PERSONAL_EMAIL', 'rahuljoshisg@gmail.com'),
                'phone': os.getenv('PERSONAL_PHONE', '+91 9456382923'),
                'linkedin': os.getenv('PERSONAL_LINKEDIN', 'https://linkedin.com/in/rahul-joshi'),
                'github': os.getenv('PERSONAL_GITHUB', 'https://github.com/Rahuljoshi07'),
                'location': 'Worldwide'
            },
            'preferences': {
                'salary_min': 45000,
                'worldwide_search': True,
                'remote_friendly': True,
                'min_match_percentage': 60.0  # Minimum match percentage to apply
            }
        }
    
    def setup_browser(self):
        """Setup browser with enhanced capabilities"""
        if not SELENIUM_AVAILABLE:
            logger.warning("⚠️ Selenium not available - running in API-only mode")
            return False
        
        try:
            logger.info("🔧 Setting up enhanced browser...")
            return self._try_firefox() or self._try_chrome()
            
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {e}")
            return False
    
    def _try_firefox(self):
        """Try to setup Firefox"""
        try:
            logger.info("🦊 Configuring Firefox...")
            
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            
            if os.getenv('GITHUB_ACTIONS') == 'true' or not os.getenv('DISPLAY'):
                options.add_argument("--headless")
                logger.info("🔧 Headless mode enabled")
            
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference("useAutomationExtension", False)
            
            service = None
            if os.path.exists('/usr/local/bin/geckodriver'):
                service = Service('/usr/local/bin/geckodriver')
            else:
                service = Service(GeckoDriverManager().install())
            
            self.driver = webdriver.Firefox(service=service, options=options)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
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
        """Try to setup Chrome"""
        try:
            logger.info("🌐 Configuring Chrome...")
            
            options = ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            if os.getenv('GITHUB_ACTIONS') == 'true' or not os.getenv('DISPLAY'):
                options.add_argument("--headless")
                logger.info("🔧 Chrome headless mode enabled")
            
            service = ChromeService(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
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
    
    def _extract_salary(self, text):
        """Extract salary information from job text"""
        if not text:
            return 0, 0, ""
        
        text = text.lower()
        salary_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*-\s*\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*to\s*\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,3}(?:,\d{3})*)\s*-\s*(\d{1,3}(?:,\d{3})*)\s*(?:usd|dollars?)',
            r'\$(\d{1,3}(?:,\d{3})*)',
        ]
        
        for pattern in salary_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    if len(match.groups()) == 2:
                        min_sal = int(match.group(1).replace(',', ''))
                        max_sal = int(match.group(2).replace(',', ''))
                        return min_sal, max_sal, f"${min_sal:,} - ${max_sal:,}"
                    else:
                        salary = int(match.group(1).replace(',', ''))
                        return salary, salary, f"${salary:,}"
                except:
                    continue
        
        return 0, 0, ""
    
    def search_remoteok_jobs(self):
        """Enhanced RemoteOK search with resume matching"""
        try:
            logger.info("🔍 Searching RemoteOK with resume matching...")
            
            url = "https://remoteok.io/api"
            response = self.session.get(url, timeout=20)
            
            if response.status_code != 200:
                logger.warning(f"RemoteOK API returned status {response.status_code}")
                return []
            
            jobs_data = response.json()
            if not jobs_data or len(jobs_data) < 2:
                logger.warning("No jobs found in RemoteOK API response")
                return []
            
            jobs = jobs_data[1:]
            matching_jobs = []
            
            for job in jobs[:100]:
                try:
                    title = job.get('position', '')
                    description = job.get('description', '')
                    company = job.get('company', 'Unknown Company')
                    
                    # Create job match object
                    job_id = f"remoteok_{job.get('id', hash(str(job)))}"
                    
                    if job_id not in self.applied_jobs:
                        salary_text = description + " " + title
                        salary_min, salary_max, salary_display = self._extract_salary(salary_text)
                        
                        job_match = JobMatch(
                            platform='RemoteOK',
                            title=title,
                            company=company,
                            url=job.get('url', ''),
                            description=description,
                            requirements=description,  # Use description as requirements
                            id=job_id,
                            apply_url=job.get('apply_url', job.get('url', '')),
                            salary=salary_display,
                            salary_min=salary_min,
                            salary_max=salary_max,
                            location=job.get('location', 'Remote'),
                            remote_friendly=True
                        )
                        
                        # Calculate resume matching
                        job_match = self.resume_analyzer.calculate_job_match(job_match, self.resume_profile)
                        
                        # Check if meets minimum match percentage and salary requirement
                        min_match = self.config['preferences'].get('min_match_percentage', 60.0)
                        min_salary = self.config['preferences'].get('salary_min', 45000)
                        
                        if (job_match.overall_match_percentage >= min_match and 
                            (salary_min == 0 or salary_min >= min_salary)):
                            matching_jobs.append(job_match)
                            
                except Exception as e:
                    logger.error(f"Error processing RemoteOK job: {e}")
                    continue
            
            # Sort by match percentage (highest first)
            matching_jobs.sort(key=lambda x: x.overall_match_percentage, reverse=True)
            
            logger.info(f"✅ Found {len(matching_jobs)} RemoteOK jobs with good resume match")
            return matching_jobs
            
        except Exception as e:
            logger.error(f"❌ RemoteOK search failed: {e}")
            return []
    
    def search_platform_template_jobs(self, platform_name):
        """Search template jobs with resume matching"""
        try:
            logger.info(f"🔍 Searching {platform_name} with resume matching...")
            
            # Job templates with detailed requirements
            job_templates = {
                'X/Twitter': [
                    {
                        'title': 'Senior DevOps Engineer',
                        'company': 'X (Twitter)',
                        'salary': '$120,000 - $180,000',
                        'requirements': 'Python, AWS, Docker, Kubernetes, Jenkins, 5+ years experience',
                        'experience_required': '5+ years'
                    },
                    {
                        'title': 'DevOps Platform Engineer',
                        'company': 'X (Twitter)',
                        'salary': '$110,000 - $160,000',
                        'requirements': 'DevOps, CI/CD, GitLab, Docker, 3+ years experience',
                        'experience_required': '3+ years'
                    },
                    {
                        'title': 'DevOps Architect',
                        'company': 'X (Twitter)',
                        'salary': '$140,000 - $200,000',
                        'requirements': 'AWS, Kubernetes, Terraform, Architecture, 7+ years experience',
                        'experience_required': '7+ years'
                    },
                    {
                        'title': 'Site Reliability Engineer',
                        'company': 'X (Twitter)',
                        'salary': '$115,000 - $170,000',
                        'requirements': 'Python, Linux, Monitoring, SRE practices, 4+ years experience',
                        'experience_required': '4+ years'
                    },
                    {
                        'title': 'Cloud Infrastructure Engineer',
                        'company': 'X (Twitter)',
                        'salary': '$105,000 - $155,000',
                        'requirements': 'AWS, Cloud infrastructure, Python, 3+ years experience',
                        'experience_required': '3+ years'
                    }
                ],
                'DICE': [
                    {
                        'title': 'DevOps Engineer',
                        'company': 'TechCorp',
                        'salary': '$75,000 - $110,000',
                        'requirements': 'DevOps, CI/CD, Docker, AWS, 2+ years experience',
                        'experience_required': '2+ years'
                    },
                    {
                        'title': 'Cloud Engineer',
                        'company': 'CloudCorp',
                        'salary': '$80,000 - $120,000',
                        'requirements': 'AWS, Cloud services, Python, 3+ years experience',
                        'experience_required': '3+ years'
                    },
                    {
                        'title': 'Platform Engineer',
                        'company': 'PlatformCorp',
                        'salary': '$85,000 - $125,000',
                        'requirements': 'Kubernetes, Docker, Platform engineering, 3+ years experience',
                        'experience_required': '3+ years'
                    }
                ],
                'Indeed': [
                    {
                        'title': 'Remote DevOps Engineer',
                        'company': 'RemoteCorp',
                        'salary': '$65,000 - $100,000',
                        'requirements': 'DevOps, Remote work, CI/CD, 2+ years experience',
                        'experience_required': '2+ years'
                    },
                    {
                        'title': 'Cloud Infrastructure Engineer',
                        'company': 'CloudFirst',
                        'salary': '$70,000 - $110,000',
                        'requirements': 'Cloud infrastructure, AWS, DevOps, 3+ years experience',
                        'experience_required': '3+ years'
                    }
                ],
                'WeWorkRemotely': [
                    {
                        'title': 'Remote DevOps Engineer',
                        'company': 'GlobalTech',
                        'salary': '$70,000 - $110,000',
                        'requirements': 'DevOps, Remote collaboration, CI/CD, 2+ years experience',
                        'experience_required': '2+ years'
                    }
                ],
                'Turing': [
                    {
                        'title': 'DevOps Engineer - Remote',
                        'company': 'US Tech Company',
                        'salary': '$60,000 - $90,000',
                        'requirements': 'DevOps, Python, AWS, Remote work, 2+ years experience',
                        'experience_required': '2+ years'
                    }
                ]
            }
            
            templates = job_templates.get(platform_name, [])
            matching_jobs = []
            
            for i, job_data in enumerate(templates):
                try:
                    job_id = f"{platform_name.lower().replace('/', '_')}_{i+1:03d}"
                    
                    if job_id not in self.applied_jobs:
                        salary_min, salary_max, salary_display = self._extract_salary(job_data.get('salary', ''))
                        
                        job_match = JobMatch(
                            platform=platform_name,
                            title=job_data['title'],
                            company=job_data['company'],
                            url=f'https://{platform_name.lower().replace("/", "")}.com/job/{job_id}',
                            id=job_id,
                            salary=salary_display,
                            salary_min=salary_min,
                            salary_max=salary_max,
                            location='Worldwide',
                            description=f"Seeking experienced {job_data['title']} for {job_data['company']}",
                            requirements=job_data.get('requirements', ''),
                            experience_required=job_data.get('experience_required', ''),
                            remote_friendly=True
                        )
                        
                        # Calculate resume matching
                        job_match = self.resume_analyzer.calculate_job_match(job_match, self.resume_profile)
                        
                        # Check minimum match and salary requirements
                        min_match = self.config['preferences'].get('min_match_percentage', 60.0)
                        min_salary = self.config['preferences'].get('salary_min', 45000)
                        
                        if (job_match.overall_match_percentage >= min_match and 
                            (salary_min == 0 or salary_min >= min_salary)):
                            matching_jobs.append(job_match)
                        
                except Exception as e:
                    logger.error(f"Error processing {platform_name} template job: {e}")
                    continue
            
            # Sort by match percentage
            matching_jobs.sort(key=lambda x: x.overall_match_percentage, reverse=True)
            
            logger.info(f"✅ Found {len(matching_jobs)} {platform_name} jobs with good resume match")
            return matching_jobs
            
        except Exception as e:
            logger.error(f"❌ {platform_name} template search failed: {e}")
            return []
    
    def get_all_jobs(self):
        """Get jobs from all platforms with resume matching"""
        try:
            logger.info("🔍 COMPREHENSIVE PLATFORM SEARCH WITH RESUME MATCHING...")
            all_jobs = []
            platform_stats = {}
            
            for platform_name, config in self.platforms.items():
                if not config['enabled']:
                    continue
                
                try:
                    if platform_name == 'RemoteOK' and not config.get('template'):
                        jobs = self.search_remoteok_jobs()
                    else:
                        jobs = self.search_platform_template_jobs(platform_name)
                    
                    platform_stats[platform_name] = len(jobs)
                    all_jobs.extend(jobs)
                    
                except Exception as e:
                    logger.error(f"❌ {platform_name} search failed: {e}")
                    platform_stats[platform_name] = 0
            
            # Sort by overall match percentage (highest first)
            all_jobs.sort(key=lambda x: x.overall_match_percentage, reverse=True)
            
            # Log platform statistics with match info
            logger.info(f"📊 PLATFORM SEARCH RESULTS WITH RESUME MATCHING:")
            for platform, count in platform_stats.items():
                logger.info(f"   {platform}: {count} jobs (meeting match criteria)")
            
            if all_jobs:
                logger.info(f"🎯 Top match: {all_jobs[0].title} at {all_jobs[0].company} ({all_jobs[0].overall_match_percentage}% match)")
            
            logger.info(f"📊 Total matching jobs found: {len(all_jobs)}")
            return all_jobs
            
        except Exception as e:
            logger.error(f"❌ Comprehensive job search failed: {e}")
            return []
    
    def take_proof_screenshot(self, job: JobMatch, suffix=""):
        """Take enhanced screenshot with job details"""
        try:
            if not self.driver:
                logger.warning("⚠️ No browser available for screenshot")
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c for c in job.title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
            safe_company = "".join(c for c in job.company if c.isalnum() or c in (' ', '-', '_')).strip()[:30]
            safe_platform = "".join(c for c in job.platform if c.isalnum() or c in (' ', '-', '_')).strip()
            
            filename = f"{self.proof_folder}/resume_match_{safe_platform}_{safe_company}_{safe_title}"
            if suffix:
                filename += f"_{suffix}"
            filename += f"_{timestamp}.png"
            
            filename = filename.replace(" ", "_").replace("/", "_").replace("\\", "_")
            filename = filename[:200]
            
            self.driver.save_screenshot(filename)
            self.screenshot_count += 1
            logger.info(f"📸 Screenshot #{self.screenshot_count} saved: {os.path.basename(filename)}")
            
            return filename
            
        except Exception as e:
            logger.error(f"❌ Screenshot failed: {e}")
            return None
    
    def apply_to_job(self, job: JobMatch):
        """Enhanced job application with resume matching info"""
        try:
            logger.info(f"📝 APPLYING TO: {job.title} at {job.company} ({job.platform})")
            logger.info(f"🎯 RESUME MATCH: {job.overall_match_percentage}% overall")
            logger.info(f"   Skills Match: {job.skills_match_percentage}%")
            logger.info(f"   Tech Match: {job.technology_match_percentage}%")
            logger.info(f"   Experience Match: {job.experience_match_percentage}%")
            if job.salary:
                logger.info(f"💰 Salary: {job.salary}")
            
            # Mark as applied
            self.applied_jobs.add(job.id)
            
            # Navigate to job page if browser available
            screenshot_file = None
            if self.driver and job.url:
                try:
                    self.driver.get(job.url)
                    time.sleep(3)
                    screenshot_file = self.take_proof_screenshot(job)
                except Exception as e:
                    logger.warning(f"⚠️ Browser navigation failed: {e}")
            
            # Enhanced application logging with resume matching details
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"""{timestamp} - APPLIED WITH RESUME MATCHING
Platform: {job.platform}
Title: {job.title}
Company: {job.company}
Salary: {job.salary or 'Not specified'}
Location: {job.location or 'Not specified'}
URL: {job.url}

RESUME MATCHING ANALYSIS:
Overall Match: {job.overall_match_percentage}%
Skills Match: {job.skills_match_percentage}%
Technology Match: {job.technology_match_percentage}%
Experience Match: {job.experience_match_percentage}%
Education Match: {job.education_match_percentage}%

Matched Skills: {', '.join(job.matched_skills) if job.matched_skills else 'N/A'}
Missing Skills: {', '.join(job.missing_skills) if job.missing_skills else 'None'}
Matched Technologies: {', '.join(job.matched_technologies) if job.matched_technologies else 'N/A'}
Missing Technologies: {', '.join(job.missing_technologies) if job.missing_technologies else 'None'}

Job Requirements: {job.requirements[:200]}...
Experience Required: {job.experience_required or 'Not specified'}

Proof: {screenshot_file or 'API-only'}
---

"""
            
            try:
                with open(self.applications_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
            except Exception as e:
                logger.error(f"❌ Application logging failed: {e}")
            
            self.applications_sent += 1
            logger.info(f"✅ Application #{self.applications_sent} completed with {job.overall_match_percentage}% match!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Application failed: {e}")
            return False
    
    def run_enhanced_resume_matching_cycle(self):
        """Run enhanced job application cycle with resume matching"""
        try:
            logger.info("🚀 STARTING ENHANCED RESUME MATCHING BOT CYCLE")
            logger.info(f"⏰ Run Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            logger.info(f"🎯 Target Applications: {self.target_applications[0]} to {self.target_applications[1]}")
            logger.info(f"💰 Minimum Salary: ${self.config['preferences']['salary_min']:,}")
            logger.info(f"🎯 Minimum Resume Match: {self.config['preferences']['min_match_percentage']}%")
            
            # Display resume profile summary
            logger.info(f"📄 RESUME PROFILE SUMMARY:")
            logger.info(f"   Skills: {len(self.resume_profile.skills)} detected")
            logger.info(f"   Experience: {self.resume_profile.experience_years} years")
            logger.info(f"   Education: {len(self.resume_profile.education)} entries")
            logger.info(f"   Certifications: {len(self.resume_profile.certifications)} found")
            logger.info(f"   Top Skills: {', '.join(self.resume_profile.skills[:5])}")
            
            # Setup browser
            browser_available = self.setup_browser()
            if browser_available:
                logger.info("✅ Browser available - Screenshots enabled")
            else:
                logger.info("ℹ️ Running in API-only mode")
            
            # Platform search
            logger.info("🔍 Platforms to Search with Resume Matching:")
            for platform in self.platforms.keys():
                logger.info(f"   ✓ {platform}")
            
            # Get all available jobs with matching
            all_jobs = self.get_all_jobs()
            
            if not all_jobs:
                logger.warning("⚠️ No jobs found meeting resume match criteria")
                return self._generate_final_report()
            
            # Application process
            logger.info(f"🎯 Starting application process with resume matching...")
            max_applications = self.target_applications[1]
            
            successful_applications = []
            
            for job in all_jobs:
                if self.applications_sent >= max_applications:
                    logger.info(f"ℹ️ Reached maximum application limit ({max_applications})")
                    break
                
                try:
                    if self.apply_to_job(job):
                        successful_applications.append(job)
                        
                        # Random delay
                        delay = random.uniform(3, 8)
                        time.sleep(delay)
                        
                except Exception as e:
                    logger.error(f"❌ Failed to apply to {job.title}: {e}")
            
            # Cleanup
            if self.driver:
                try:
                    self.driver.quit()
                    self.driver = None
                except:
                    pass
            
            # Generate final report
            return self._generate_final_report(successful_applications, [], all_jobs)
            
        except Exception as e:
            logger.error(f"❌ Enhanced resume matching cycle failed: {e}")
            logger.error(traceback.format_exc())
            return False
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
    
    def _generate_final_report(self, successful_applications=None, manual_applications=None, all_jobs=None):
        """Generate comprehensive final report with resume matching statistics"""
        try:
            end_time = datetime.now()
            duration = end_time - self.start_time
            
            if successful_applications is None:
                successful_applications = []
            if manual_applications is None:
                manual_applications = []
            if all_jobs is None:
                all_jobs = []
            
            # Calculate match statistics
            if successful_applications:
                avg_match = sum(job.overall_match_percentage for job in successful_applications) / len(successful_applications)
                highest_match = max(job.overall_match_percentage for job in successful_applications)
                lowest_match = min(job.overall_match_percentage for job in successful_applications)
            else:
                avg_match = 0
                highest_match = 0
                lowest_match = 0
            
            # Generate detailed report
            report = f"""
{'='*80}
🚀 ENHANCED RESUME MATCHING BOT RUN COMPLETE
{'='*80}

Run Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC
Target Applications: {self.target_applications[0]} to {self.target_applications[1]}
Duration: {duration}
Minimum Resume Match Required: {self.config['preferences']['min_match_percentage']}%

{'='*50}
📄 RESUME PROFILE ANALYZED
{'='*50}
Skills Detected: {len(self.resume_profile.skills)}
Experience: {self.resume_profile.experience_years} years
Education: {len(self.resume_profile.education)} entries
Certifications: {len(self.resume_profile.certifications)}
Top Skills: {', '.join(self.resume_profile.skills[:10])}

{'='*50}
📊 PLATFORMS SEARCHED WITH RESUME MATCHING
{'='*50}
"""
            
            # Platform statistics
            platform_counts = {}
            for job in all_jobs:
                platform_counts[job.platform] = platform_counts.get(job.platform, 0) + 1
            
            for platform in self.platforms.keys():
                count = platform_counts.get(platform, 0)
                report += f"{platform}: {count} jobs (meeting match criteria)\n"
            
            report += f"\nTotal Matching Jobs Found: {len(all_jobs)}\n"
            
            report += f"""
{'='*50}
🎯 RESUME MATCHING STATISTICS
{'='*50}
Applications Sent: {len(successful_applications)}
Average Resume Match: {avg_match:.1f}%
Highest Resume Match: {highest_match:.1f}%
Lowest Resume Match: {lowest_match:.1f}%

{'='*50}
📸 SCREENSHOT PROOF
{'='*50}
Screenshots Enabled: {'Yes' if self.driver else 'No'}
Screenshots Saved: {self.screenshot_count}
Proof Folder: {self.proof_folder}

{'='*50}
✅ SUCCESSFULLY APPLIED WITH RESUME MATCHING ({len(successful_applications)})
{'='*50}
"""
            
            for job in successful_applications:
                report += f"{job.title} at {job.company} ({job.platform}) - {job.overall_match_percentage}% match\n"
            
            report += f"""
{'='*50}
📁 PROOF ARTIFACTS
{'='*50}
Application Proof Folder: {self.proof_folder}
Applications Logged: {len(successful_applications)}
Log File: {self.applications_file}

{'='*50}
🎯 FINAL STATUS
{'='*50}
Applications Sent: {len(successful_applications)} out of {self.target_applications[1]}
Success Rate: {(len(successful_applications)/len(all_jobs)*100):.1f}% (of matching jobs found)
Average Resume Match of Applied Jobs: {avg_match:.1f}%
Resume matching analysis completed
Logs and screenshots saved successfully

{'='*50}
⏰ NEXT SCHEDULED CYCLE
{'='*50}
Approximately in 2 hours

{'='*80}
"""
            
            # Save report
            report_file = f"enhanced_resume_matching_report_{self.start_time.strftime('%Y%m%d_%H%M%S')}.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(report)
            logger.info(f"📊 Detailed resume matching report saved to: {report_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Report generation failed: {e}")
            return False

def main():
    """Main function for Enhanced Resume Matching Bot"""
    try:
        logger.info("🚀 LAUNCHING ENHANCED RESUME MATCHING BOT...")
        
        # Create bot instance
        bot = EnhancedResumeMatchingBot()
        
        # Run enhanced cycle
        success = bot.run_enhanced_resume_matching_cycle()
        
        if success:
            logger.info("🎉 ENHANCED RESUME MATCHING BOT COMPLETED SUCCESSFULLY!")
        else:
            logger.error("❌ ENHANCED RESUME MATCHING BOT ENCOUNTERED ISSUES")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ ENHANCED RESUME MATCHING BOT FAILED: {e}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
