from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import requests
from config import Config
from resume_analyzer import ResumeAnalyzer

class JobBotWithLogin:
    def __init__(self):
        self.config = Config()
        self.user_config = self.config.load_config()
        self.resume_analyzer = ResumeAnalyzer()
        self.driver = None
        self.applied_jobs = set()
        
    def setup_browser(self):
        """Setup Chrome browser with options"""
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # Remove headless for debugging - you can add it back later
        # options.add_argument("--headless")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        print("✅ Browser setup complete")
        
    def login_linkedin(self):
        """Login to LinkedIn"""
        try:
            print("🔐 Logging into LinkedIn...")
            self.driver.get("https://www.linkedin.com/login")
            
            # Enter credentials
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            
            email_field.send_keys(self.user_config['platforms']['linkedin']['email'])
            password_field.send_keys(self.user_config['platforms']['linkedin']['password'])
            
            # Click login
            login_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_btn.click()
            
            time.sleep(5)  # Wait for login
            print("✅ LinkedIn login successful")
            return True
            
        except Exception as e:
            print(f"❌ LinkedIn login failed: {e}")
            return False
    
    def search_linkedin_jobs(self):
        """Search for jobs on LinkedIn"""
        try:
            print("🔍 Searching LinkedIn jobs...")
            
            # Go to jobs page
            self.driver.get("https://www.linkedin.com/jobs/")
            time.sleep(3)
            
            # Search for DevOps jobs
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label*='Search by title']"))
            )
            search_box.clear()
            search_box.send_keys("DevOps Engineer")
            
            # Click search
            search_btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Search']")
            search_btn.click()
            time.sleep(5)
            
            # Get job listings
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".job-search-card")
            jobs = []
            
            for card in job_cards[:5]:  # First 5 jobs
                try:
                    title = card.find_element(By.CSS_SELECTOR, ".base-search-card__title").text
                    company = card.find_element(By.CSS_SELECTOR, ".base-search-card__subtitle").text
                    link = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    
                    jobs.append({
                        'platform': 'LinkedIn',
                        'title': title,
                        'company': company,
                        'url': link,
                        'id': f"linkedin_{hash(link)}"
                    })
                except:
                    continue
            
            print(f"✅ Found {len(jobs)} LinkedIn jobs")
            return jobs
            
        except Exception as e:
            print(f"❌ LinkedIn search failed: {e}")
            return []
    
    def apply_linkedin_job(self, job):
        """Apply to a LinkedIn job"""
        try:
            print(f"📝 Applying to LinkedIn job: {job['title']}")
            
            self.driver.get(job['url'])
            time.sleep(3)
            
            # Look for Easy Apply button
            try:
                easy_apply_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Easy Apply')]"))
                )
                easy_apply_btn.click()
                time.sleep(2)
                
                # Handle application form (simplified)
                # This would need more sophisticated handling for different form types
                submit_btns = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Submit application')]")
                if submit_btns:
                    submit_btns[0].click()
                    print("✅ LinkedIn application submitted!")
                    return True
                else:
                    print("⚠️ Could not find submit button - manual intervention needed")
                    return False
                    
            except:
                print("⚠️ Easy Apply not available for this job")
                return False
                
        except Exception as e:
            print(f"❌ LinkedIn application failed: {e}")
            return False
    
    def search_remoteok_jobs(self):
        """Search RemoteOK for jobs (no login required)"""
        print("🔍 Searching RemoteOK...")
        try:
            url = "https://remoteok.io/api"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                jobs = response.json()[1:]  # Skip first item
                matching_jobs = []
                
                # Get skills from resume
                resume_analysis = self.resume_analyzer.analyze_resume()
                skills = resume_analysis['skills'] if resume_analysis else ["DevOps", "AWS", "Docker"]
                
                for job in jobs[:10]:
                    title = job.get('position', '').lower()
                    description = job.get('description', '').lower()
                    
                    if any(skill.lower() in title + description for skill in skills):
                        if job.get('id') not in self.applied_jobs:
                            matching_jobs.append({
                                'platform': 'RemoteOK',
                                'title': job.get('position'),
                                'company': job.get('company'),
                                'url': job.get('url'),
                                'id': job.get('id'),
                                'apply_url': job.get('apply_url')
                            })
                
                print(f"✅ Found {len(matching_jobs)} RemoteOK jobs")
                return matching_jobs
                
        except Exception as e:
            print(f"❌ RemoteOK search failed: {e}")
            return []
    
    def apply_remoteok_job(self, job):
        """Apply to RemoteOK job by opening application URL"""
        try:
            print(f"📝 Opening RemoteOK application: {job['title']}")
            
            if job.get('apply_url'):
                self.driver.get(job['apply_url'])
                time.sleep(5)
                print("✅ RemoteOK application page opened - manual completion needed")
                return True
            else:
                print("⚠️ No application URL available")
                return False
                
        except Exception as e:
            print(f"❌ RemoteOK application failed: {e}")
            return False
    
    def run_job_cycle(self):
        """Main job search and application cycle"""
        print(f"\n🤖 Starting job application cycle...")
        
        self.setup_browser()
        
        all_jobs = []
        applications_sent = 0
        
        # Search LinkedIn
        if self.login_linkedin():
            linkedin_jobs = self.search_linkedin_jobs()
            for job in linkedin_jobs:
                if job['id'] not in self.applied_jobs:
                    if self.apply_linkedin_job(job):
                        applications_sent += 1
                        self.applied_jobs.add(job['id'])
                        time.sleep(10)  # Rate limiting
        
        # Search RemoteOK
        remoteok_jobs = self.search_remoteok_jobs()
        for job in remoteok_jobs:
            if job['id'] not in self.applied_jobs:
                if self.apply_remoteok_job(job):
                    applications_sent += 1
                    self.applied_jobs.add(job['id'])
                    time.sleep(5)
        
        # Log applications
        with open('job-bot/applications_with_login.txt', 'a') as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Completed cycle: {applications_sent} applications sent\n")
        
        print(f"🎯 Job cycle completed! Applications sent: {applications_sent}")
        
        if self.driver:
            self.driver.quit()
    
    def start_continuous_monitoring(self):
        """Start continuous job monitoring"""
        import schedule
        
        print("🚀 Starting 24/7 job monitoring with login...")
        
        # Schedule every 2 hours (to avoid being rate limited)
        schedule.every(2).hours.do(self.run_job_cycle)
        
        # Initial run
        self.run_job_cycle()
        
        # Continuous loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(300)  # Check every 5 minutes
            except KeyboardInterrupt:
                print("🛑 Job bot stopped by user")
                break

if __name__ == "__main__":
    bot = JobBotWithLogin()
    bot.run_job_cycle()
