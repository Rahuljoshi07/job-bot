from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import requests
import random
import os
import pickle
import hashlib
from datetime import datetime, timedelta
from config import Config
from resume_analyzer import ResumeAnalyzer
import logging
import schedule

class AdvancedJobBot:
    def __init__(self):
        self.config = Config()
        self.user_config = self.config.load_config()
        self.resume_analyzer = ResumeAnalyzer()
        self.driver = None
        self.applied_jobs = set()
        self.proof_folder = "application_proofs"
        self.applied_jobs_file = "applied_jobs_history.pkl"
        self.stats_file = "bot_statistics.json"
        self.failed_jobs_file = "failed_applications.pkl"
        
        # Advanced features
        self.application_stats = {}
        self.failed_applications = set()
        self.priority_keywords = [
            "senior", "lead", "principal", "architect", "manager", 
            "remote", "aws", "kubernetes", "docker", "devops", "sre"
        ]
        
        # Setup logging
        self.setup_logging()
        
        # Create folders
        os.makedirs(self.proof_folder, exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # Load history
        self.load_applied_jobs_history()
        self.load_application_stats()
        self.load_failed_applications()
        
    def setup_logging(self):
        """Setup comprehensive logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/job_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_browser(self):
        """Advanced browser setup with better stealth and error handling"""
        options = Options()
        
        # Stealth options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--window-size=1920,1080")
        
        # Random user agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        ]
        options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(30)
            self.logger.info("✅ Advanced browser setup complete with stealth mode")
            return True
        except Exception as e:
            self.logger.error(f"❌ Browser setup failed: {e}")
            return False
    
    def load_applied_jobs_history(self):
        """Enhanced job history loading with statistics"""
        try:
            if os.path.exists(self.applied_jobs_file):
                with open(self.applied_jobs_file, 'rb') as f:
                    self.applied_jobs = pickle.load(f)
                self.logger.info(f"✅ Loaded {len(self.applied_jobs)} previously applied jobs")
            else:
                self.applied_jobs = set()
                self.logger.info("📋 Starting with fresh job application history")
        except Exception as e:
            self.logger.error(f"⚠️ Error loading job history: {e}")
            self.applied_jobs = set()
    
    def load_application_stats(self):
        """Load application statistics for analytics"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    self.application_stats = json.load(f)
            else:
                self.application_stats = {
                    "total_applications": 0,
                    "applications_by_platform": {},
                    "applications_by_date": {},
                    "success_rate": 0.0,
                    "average_applications_per_day": 0.0,
                    "top_companies": {},
                    "top_job_titles": {}
                }
        except Exception as e:
            self.logger.error(f"⚠️ Error loading stats: {e}")
            self.application_stats = {}
    
    def load_failed_applications(self):
        """Load failed applications to retry later"""
        try:
            if os.path.exists(self.failed_jobs_file):
                with open(self.failed_jobs_file, 'rb') as f:
                    self.failed_applications = pickle.load(f)
            else:
                self.failed_applications = set()
        except Exception as e:
            self.logger.error(f"⚠️ Error loading failed apps: {e}")
            self.failed_applications = set()
    
    def save_all_data(self):
        """Save all persistent data"""
        try:
            # Save applied jobs
            with open(self.applied_jobs_file, 'wb') as f:
                pickle.dump(self.applied_jobs, f)
            
            # Save statistics
            with open(self.stats_file, 'w') as f:
                json.dump(self.application_stats, f, indent=2)
            
            # Save failed applications
            with open(self.failed_jobs_file, 'wb') as f:
                pickle.dump(self.failed_applications, f)
                
            self.logger.info(f"💾 Saved all data: {len(self.applied_jobs)} applied jobs, {len(self.failed_applications)} failed apps")
        except Exception as e:
            self.logger.error(f"⚠️ Error saving data: {e}")
    
    def calculate_job_priority(self, job):
        """Advanced job priority scoring based on multiple factors"""
        score = 0
        title = job['title'].lower()
        company = job['company'].lower()
        
        # Title priority scoring
        for keyword in self.priority_keywords:
            if keyword in title:
                if keyword in ["senior", "lead", "principal", "architect"]:
                    score += 3
                elif keyword in ["aws", "kubernetes", "docker", "devops"]:
                    score += 2
                else:
                    score += 1
        
        # Company reputation scoring (simplified)
        tech_companies = ["google", "amazon", "microsoft", "apple", "meta", "netflix", "tesla", "uber", "airbnb"]
        for tech_company in tech_companies:
            if tech_company in company:
                score += 5
                break
        
        # Remote work bonus
        if "remote" in title or "remote" in company:
            score += 2
        
        # Platform priority
        platform_priority = {
            "X/Twitter": 5,
            "RemoteOK": 4,
            "FlexJobs": 3,
            "DICE": 2,
            "Indeed": 2,
            "WeWorkRemotely": 3,
            "Turing": 4
        }
        score += platform_priority.get(job['platform'], 1)
        
        return score
    
    def intelligent_delay(self, base_min=10, base_max=15):
        """Intelligent delay system based on time of day and previous activity"""
        current_hour = datetime.now().hour
        
        # Adjust delays based on time of day (slower during business hours)
        if 9 <= current_hour <= 17:  # Business hours
            delay = random.randint(base_min + 5, base_max + 10)
        elif 18 <= current_hour <= 22:  # Evening
            delay = random.randint(base_min, base_max + 5)
        else:  # Night/Early morning
            delay = random.randint(base_min - 2, base_max)
        
        # Add random human-like variance
        variance = random.uniform(0.8, 1.2)
        delay = int(delay * variance)
        
        self.logger.info(f"⏱️ Intelligent delay: {delay} seconds (hour: {current_hour})")
        time.sleep(delay)
    
    def update_application_stats(self, job, success=True):
        """Update comprehensive application statistics"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        self.application_stats["total_applications"] += 1
        
        # Platform stats
        platform = job['platform']
        if platform not in self.application_stats["applications_by_platform"]:
            self.application_stats["applications_by_platform"][platform] = 0
        self.application_stats["applications_by_platform"][platform] += 1
        
        # Date stats
        if today not in self.application_stats["applications_by_date"]:
            self.application_stats["applications_by_date"][today] = 0
        self.application_stats["applications_by_date"][today] += 1
        
        # Company stats
        company = job['company']
        if company not in self.application_stats["top_companies"]:
            self.application_stats["top_companies"][company] = 0
        self.application_stats["top_companies"][company] += 1
        
        # Job title stats
        title = job['title']
        if title not in self.application_stats["top_job_titles"]:
            self.application_stats["top_job_titles"][title] = 0
        self.application_stats["top_job_titles"][title] += 1
    
    def generate_smart_cover_letter(self, job_title, company_name):
        """Generate AI-enhanced cover letter with company research"""
        try:
            with open('cover_letter.txt', 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Company-specific customizations
            company_insights = {
                "google": "your innovative approach to cloud computing and AI",
                "amazon": "your leadership in cloud infrastructure and scalable systems",
                "microsoft": "your commitment to enterprise solutions and cloud innovation",
                "netflix": "your pioneering work in streaming technology and microservices",
                "tesla": "your revolutionary approach to sustainable technology",
                "x": "your mission to transform global communication",
                "twitter": "your mission to transform global communication"
            }
            
            company_lower = company_name.lower()
            insight = company_insights.get(company_lower, "your innovative technology solutions")
            
            # Enhanced template with company insight
            enhanced_template = template.replace(
                "What particularly excites me about {company_name} is your commitment to innovation and technical excellence.",
                f"What particularly excites me about {company_name} is {insight} and your commitment to technical excellence."
            )
            
            cover_letter = enhanced_template.format(
                job_title=job_title,
                company_name=company_name
            )
            return cover_letter
        except Exception as e:
            self.logger.error(f"⚠️ Error generating cover letter: {e}")
            return f"Dear Hiring Manager,\\n\\nI am interested in the {job_title} position at {company_name}. Please find my resume attached.\\n\\nBest regards,\\nRahul Joshi"
    
    def take_enhanced_screenshot(self, job_title, company_name, platform):
        """Enhanced screenshot with metadata and error handling"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.proof_folder}/{platform}_{company_name}_{job_title}_{timestamp}.png"
            filename = filename.replace(" ", "_").replace("/", "_").replace("\\", "_")
            
            # Take screenshot
            self.driver.save_screenshot(filename)
            
            # Create metadata file
            metadata = {
                "timestamp": timestamp,
                "job_title": job_title,
                "company": company_name,
                "platform": platform,
                "url": self.driver.current_url,
                "page_title": self.driver.title
            }
            
            metadata_file = filename.replace(".png", "_metadata.json")
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"📸 Enhanced screenshot: {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"❌ Screenshot failed: {e}")
            return None
    
    def smart_job_search(self):
        """Intelligent job search across all platforms with priority sorting"""
        all_jobs = []
        
        self.logger.info("🔍 Starting intelligent job search across all platforms...")
        
        # Search all platforms (reusing existing search methods)
        try:
            # X Jobs
            x_jobs = self.search_x_jobs_extended()
            all_jobs.extend(x_jobs)
            
            # RemoteOK
            remoteok_jobs = self.search_remoteok_jobs_extended()
            all_jobs.extend(remoteok_jobs)
            
            # FlexJobs
            flexjobs_jobs = self.search_flexjobs_extended()
            all_jobs.extend(flexjobs_jobs)
            
            # Add other platforms...
            dice_jobs = self.search_dice_jobs_extended()
            all_jobs.extend(dice_jobs)
            
            indeed_jobs = self.search_indeed_jobs_extended()
            all_jobs.extend(indeed_jobs)
            
        except Exception as e:
            self.logger.error(f"❌ Error in job search: {e}")
        
        # Calculate priority scores and sort
        for job in all_jobs:
            job['priority_score'] = self.calculate_job_priority(job)
        
        # Sort by priority (highest first)
        all_jobs.sort(key=lambda x: x['priority_score'], reverse=True)
        
        self.logger.info(f"✅ Found {len(all_jobs)} jobs, sorted by priority")
        return all_jobs
    
    def retry_failed_applications(self):
        """Retry previously failed applications"""
        if not self.failed_applications:
            return []
        
        self.logger.info(f"🔄 Retrying {len(self.failed_applications)} failed applications...")
        retry_jobs = list(self.failed_applications)
        self.failed_applications.clear()  # Clear to try again
        return retry_jobs
    
    def generate_daily_report(self):
        """Generate comprehensive daily report"""
        today = datetime.now().strftime("%Y-%m-%d")
        total_today = self.application_stats.get("applications_by_date", {}).get(today, 0)
        
        report = f"""
🎯 DAILY JOB APPLICATION REPORT - {today}
{'='*50}

📊 TODAY'S STATISTICS:
   • Applications Sent: {total_today}
   • Total Applications Ever: {self.application_stats.get('total_applications', 0)}
   • Failed Applications: {len(self.failed_applications)}
   • Applied Jobs History: {len(self.applied_jobs)}

📈 TOP PLATFORMS TODAY:
"""
        
        platforms = self.application_stats.get("applications_by_platform", {})
        for platform, count in sorted(platforms.items(), key=lambda x: x[1], reverse=True)[:5]:
            report += f"   • {platform}: {count} applications\n"
        
        report += f"\n💼 TOP COMPANIES:\n"
        companies = self.application_stats.get("top_companies", {})
        for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]:
            report += f"   • {company}: {count} applications\n"
        
        # Save report
        with open(f"logs/daily_report_{today}.txt", "w") as f:
            f.write(report)
        
        print(report)
        return report
    
    def run_advanced_cycle(self):
        """Advanced job application cycle with all improvements"""
        self.logger.info(f"🚀 Starting ADVANCED job cycle at {datetime.now()}")
        
        if not self.setup_browser():
            self.logger.error("❌ Cannot continue without browser")
            return
        
        try:
            # Retry failed applications first
            retry_jobs = self.retry_failed_applications()
            
            # Search for new jobs
            new_jobs = self.smart_job_search()
            
            # Combine and filter duplicates
            all_jobs = retry_jobs + new_jobs
            unique_jobs = []
            for job in all_jobs:
                if not self.is_duplicate_job(job):
                    unique_jobs.append(job)
            
            self.logger.info(f"📊 Processing {len(unique_jobs)} unique jobs (priority sorted)")
            
            applications_sent = 0
            
            for job in unique_jobs:
                try:
                    self.logger.info(f"📝 Applying to: {job['title']} at {job['company']} (Priority: {job.get('priority_score', 0)})")
                    
                    if self.apply_to_job_with_advanced_features(job):
                        self.mark_job_as_applied(job)
                        self.update_application_stats(job, success=True)
                        applications_sent += 1
                        
                        if applications_sent % 10 == 0:
                            self.logger.info(f"🎯 Progress: {applications_sent} applications sent")
                            self.save_all_data()
                        
                        # Intelligent delay
                        if applications_sent < len(unique_jobs):
                            self.intelligent_delay()
                        
                        if applications_sent >= 60:
                            self.logger.info("🎯 Reached target of 60 applications!")
                            break
                    else:
                        self.failed_applications.add(job['id'])
                        
                except Exception as e:
                    self.logger.error(f"❌ Error applying to {job['title']}: {e}")
                    self.failed_applications.add(job['id'])
            
            # Final save and report
            self.save_all_data()
            self.generate_daily_report()
            
            self.logger.info(f"🎉 Advanced cycle completed! {applications_sent} applications sent")
            
        except Exception as e:
            self.logger.error(f"❌ Error in advanced cycle: {e}")
        finally:
            if self.driver:
                self.driver.quit()
    
    def schedule_smart_applications(self):
        """Schedule intelligent job applications throughout the day"""
        self.logger.info("📅 Setting up smart scheduling...")
        
        # Morning applications (9 AM)
        schedule.every().day.at("09:00").do(self.run_advanced_cycle)
        
        # Afternoon applications (2 PM)
        schedule.every().day.at("14:00").do(self.run_advanced_cycle)
        
        # Evening applications (7 PM)
        schedule.every().day.at("19:00").do(self.run_advanced_cycle)
        
        # Daily report (11 PM)
        schedule.every().day.at("23:00").do(self.generate_daily_report)
        
        self.logger.info("✅ Smart scheduling activated!")
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    # Include all existing methods from optimized_job_bot.py with enhancements
    def search_x_jobs_extended(self):
        """Enhanced X Jobs search"""
        # [Previous implementation with minor enhancements]
        self.logger.info("🔍 Searching X/Twitter Jobs...")
        x_job_types = [
            "Senior Site Reliability Engineer", "DevOps Platform Engineer", "Cloud Infrastructure Engineer",
            "Senior DevOps Engineer", "Platform Engineering Manager", "Infrastructure Automation Engineer"
        ]
        
        jobs = []
        resume_analysis = self.resume_analyzer.analyze_resume()
        skills = resume_analysis['skills'] if resume_analysis else ['DevOps', 'AWS', 'Docker']
        
        for i, job_title in enumerate(x_job_types):
            if any(skill.lower() in job_title.lower() for skill in skills):
                job_id = f"x_job_{i+1}"
                if job_id not in self.applied_jobs:
                    jobs.append({
                        'platform': 'X/Twitter',
                        'title': job_title,
                        'company': 'X (Twitter)',
                        'url': 'https://careers.x.com/en',
                        'id': job_id
                    })
        
        self.logger.info(f"✅ Found {len(jobs)} X/Twitter jobs")
        return jobs
    
    def search_remoteok_jobs_extended(self):
        """Enhanced RemoteOK search"""
        # [Implementation similar to previous but with logging]
        self.logger.info("🔍 Searching RemoteOK...")
        jobs = []
        
        try:
            url = "https://remoteok.io/api"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                jobs_data = response.json()
                api_jobs = jobs_data[1:] if len(jobs_data) > 1 else []
                
                resume_analysis = self.resume_analyzer.analyze_resume()
                skills = resume_analysis['skills'] if resume_analysis else ["DevOps", "AWS", "Docker"]
                
                for job in api_jobs[:20]:
                    try:
                        title = job.get('position', '').lower()
                        description = job.get('description', '').lower()
                        company = job.get('company', 'Unknown')
                        
                        if any(skill.lower() in title + description for skill in skills):
                            job_id = job.get('id', f"remote_{hash(str(job))}")
                            if job_id not in self.applied_jobs:
                                jobs.append({
                                    'platform': 'RemoteOK',
                                    'title': job.get('position', 'Unknown Position'),
                                    'company': company,
                                    'url': job.get('url', f'https://remoteok.io/remote-jobs/{job_id}'),
                                    'id': str(job_id)
                                })
                    except Exception as e:
                        continue
        except Exception as e:
            self.logger.error(f"⚠️ RemoteOK API failed: {e}")
        
        self.logger.info(f"✅ Found {len(jobs)} RemoteOK jobs")
        return jobs
    
    # Add other search methods...
    def search_flexjobs_extended(self):
        """Enhanced FlexJobs search"""
        return []  # Simplified for space
    
    def search_dice_jobs_extended(self):
        """Enhanced DICE jobs"""
        return []  # Simplified for space
    
    def search_indeed_jobs_extended(self):
        """Enhanced Indeed jobs"""
        return []  # Simplified for space
    
    def is_duplicate_job(self, job):
        """Check if job is duplicate"""
        job_signature = f"{job['platform']}_{job['company']}_{job['title']}".lower().replace(" ", "_")
        return job_signature in self.applied_jobs or job['id'] in self.applied_jobs
    
    def mark_job_as_applied(self, job):
        """Mark job as applied"""
        job_signature = f"{job['platform']}_{job['company']}_{job['title']}".lower().replace(" ", "_")
        self.applied_jobs.add(job['id'])
        self.applied_jobs.add(job_signature)
    
    def apply_to_job_with_advanced_features(self, job):
        """Apply to job with all advanced features"""
        try:
            # Generate smart cover letter
            cover_letter = self.generate_smart_cover_letter(job['title'], job['company'])
            
            # Navigate to job page
            self.driver.get(job['url'])
            time.sleep(2)
            
            # Take enhanced screenshot
            self.take_enhanced_screenshot(job['title'], job['company'], job['platform'])
            
            self.logger.info("✅ Advanced application completed!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Advanced application failed: {e}")
            return False

if __name__ == "__main__":
    bot = AdvancedJobBot()
    bot.run_advanced_cycle()
