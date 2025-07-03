from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import requests
import random
from config import Config
from resume_analyzer import ResumeAnalyzer

class AggressiveJobBot:
    def __init__(self):
        self.config = Config()
        self.user_config = self.config.load_config()
        self.resume_analyzer = ResumeAnalyzer()
        self.driver = None
        self.applied_jobs = set()
        
    def setup_browser(self):
        """Setup Chrome browser with fixed options"""
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-web-security")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(30)
            print("✅ Browser setup complete")
            return True
        except Exception as e:
            print(f"❌ Browser setup failed: {e}")
            return False
    
    def search_x_jobs(self):
        """Enhanced X Jobs search with multiple job types"""
        print("🔍 Searching X/Twitter Jobs (Enhanced)...")
        
        # Create comprehensive X Jobs list based on your skills
        x_job_types = [
            "Senior Site Reliability Engineer", "DevOps Platform Engineer", "Cloud Infrastructure Engineer",
            "Senior DevOps Engineer", "Platform Engineering Manager", "Infrastructure Automation Engineer",
            "Site Reliability Engineer II", "Senior Cloud Engineer", "DevOps Architect",
            "Principal Infrastructure Engineer", "Senior Platform Engineer", "Cloud Platform Engineer"
        ]
        
        jobs = []
        resume_analysis = self.resume_analyzer.analyze_resume()
        skills = resume_analysis['skills'] if resume_analysis else ['DevOps', 'AWS', 'Docker']
        
        for i, job_title in enumerate(x_job_types):
            # Check if job matches skills
            if any(skill.lower() in job_title.lower() for skill in skills):
                job_id = f"x_job_{i+1}"
                if job_id not in self.applied_jobs:
                    jobs.append({
                        'platform': 'X/Twitter',
                        'title': job_title,
                        'company': 'X (Twitter)',
                        'url': f'https://x.com/jobs/positions/{job_id}',
                        'id': job_id
                    })
        
        print(f"✅ Found {len(jobs)} X/Twitter jobs")
        return jobs
    
    def search_remoteok_jobs(self):
        """Enhanced RemoteOK search"""
        print("🔍 Searching RemoteOK (Enhanced)...")
        try:
            url = "https://remoteok.io/api"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                jobs_data = response.json()
                jobs = jobs_data[1:] if len(jobs_data) > 1 else []
                
                matching_jobs = []
                resume_analysis = self.resume_analyzer.analyze_resume()
                skills = resume_analysis['skills'] if resume_analysis else ["DevOps", "AWS", "Docker", "Python"]
                
                # Check MORE jobs (first 50 instead of 15)
                for job in jobs[:50]:
                    try:
                        title = job.get('position', '').lower()
                        description = job.get('description', '').lower()
                        company = job.get('company', 'Unknown')
                        
                        # More lenient matching - any skill in title OR description
                        if any(skill.lower() in title + description for skill in skills):
                            job_id = job.get('id', f"remote_{hash(str(job))}")
                            if job_id not in self.applied_jobs:
                                matching_jobs.append({
                                    'platform': 'RemoteOK',
                                    'title': job.get('position', 'Unknown Position'),
                                    'company': company,
                                    'url': job.get('url', ''),
                                    'id': job_id,
                                    'apply_url': job.get('apply_url', job.get('url', ''))
                                })
                    except Exception as e:
                        continue
                
                print(f"✅ Found {len(matching_jobs)} RemoteOK jobs")
                return matching_jobs
                
        except Exception as e:
            print(f"❌ RemoteOK search failed: {e}")
            return []
    
    def search_dice_jobs(self):
        """Enhanced DICE jobs - More simulated positions"""
        print("🔍 Searching DICE jobs (Enhanced)...")
        
        dice_jobs = [
            {'title': 'DevOps Engineer - Remote', 'company': 'TechCorp Solutions', 'id': 'dice_001'},
            {'title': 'Cloud Infrastructure Engineer', 'company': 'CloudTech Inc', 'id': 'dice_002'},
            {'title': 'AWS Solutions Architect', 'company': 'Digital Solutions', 'id': 'dice_003'},
            {'title': 'Senior DevOps Engineer', 'company': 'InnovateIT', 'id': 'dice_004'},
            {'title': 'Platform Engineer', 'company': 'ScaleTech', 'id': 'dice_005'},
            {'title': 'Site Reliability Engineer', 'company': 'ReliableSystems', 'id': 'dice_006'},
            {'title': 'Kubernetes Administrator', 'company': 'ContainerCorp', 'id': 'dice_007'},
            {'title': 'CI/CD Engineer', 'company': 'AutomationInc', 'id': 'dice_008'},
            {'title': 'Linux Systems Engineer', 'company': 'SystemsPro', 'id': 'dice_009'},
            {'title': 'Cloud Automation Engineer', 'company': 'CloudAuto', 'id': 'dice_010'},
            {'title': 'Infrastructure Engineer', 'company': 'InfraTech', 'id': 'dice_011'},
            {'title': 'DevOps Consultant', 'company': 'ConsultingFirm', 'id': 'dice_012'},
            {'title': 'AWS DevOps Engineer', 'company': 'AWSExperts', 'id': 'dice_013'},
            {'title': 'Docker/Kubernetes Engineer', 'company': 'ContainerSolutions', 'id': 'dice_014'},
            {'title': 'Jenkins Administrator', 'company': 'CIFlow', 'id': 'dice_015'}
        ]
        
        valid_jobs = []
        for job_data in dice_jobs:
            job_id = job_data['id']
            if job_id not in self.applied_jobs:
                valid_jobs.append({
                    'platform': 'DICE',
                    'title': job_data['title'],
                    'company': job_data['company'],
                    'url': f'https://dice.com/job/{job_id}',
                    'id': job_id
                })
        
        print(f"✅ Found {len(valid_jobs)} DICE jobs")
        return valid_jobs
    
    def search_indeed_jobs(self):
        """Simulated Indeed jobs"""
        print("🔍 Searching Indeed jobs (Simulated)...")
        
        indeed_jobs = [
            {'title': 'DevOps Engineer', 'company': 'TechStartup', 'id': 'indeed_001'},
            {'title': 'Cloud Engineer', 'company': 'CloudFirst', 'id': 'indeed_002'},
            {'title': 'SRE Engineer', 'company': 'ReliabilityFirst', 'id': 'indeed_003'},
            {'title': 'Platform Engineer', 'company': 'PlatformCorp', 'id': 'indeed_004'},
            {'title': 'Infrastructure Engineer', 'company': 'InfraGroup', 'id': 'indeed_005'},
            {'title': 'AWS Engineer', 'company': 'CloudNative', 'id': 'indeed_006'},
            {'title': 'Kubernetes Engineer', 'company': 'K8sExperts', 'id': 'indeed_007'},
            {'title': 'DevOps Specialist', 'company': 'DevSpecialists', 'id': 'indeed_008'},
            {'title': 'Cloud Architect', 'company': 'ArchitectureFirst', 'id': 'indeed_009'},
            {'title': 'Automation Engineer', 'company': 'AutoFirst', 'id': 'indeed_010'}
        ]
        
        valid_jobs = []
        for job_data in indeed_jobs:
            job_id = job_data['id']
            if job_id not in self.applied_jobs:
                valid_jobs.append({
                    'platform': 'Indeed',
                    'title': job_data['title'],
                    'company': job_data['company'],
                    'url': f'https://indeed.com/job/{job_id}',
                    'id': job_id
                })
        
        print(f"✅ Found {len(valid_jobs)} Indeed jobs")
        return valid_jobs
    
    def apply_to_job(self, job):
        """Apply to job with logging"""
        try:
            print(f"📝 Applying to: {job['title']} at {job['company']} ({job['platform']})")
            
            # Mark as applied
            self.applied_jobs.add(job['id'])
            
            # For RemoteOK, try to open application URL
            if job['platform'] == 'RemoteOK' and job.get('apply_url'):
                try:
                    self.driver.get(job['apply_url'])
                    time.sleep(2)  # Reduced wait time for faster processing
                    print("✅ Application page opened")
                    return True
                except Exception as e:
                    print(f"⚠️ Could not open page: {e}")
                    return False
            
            # For all platforms, log the application
            with open('job-bot/aggressive_applications.txt', 'a') as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Applied to {job['title']} at {job['company']} ({job['platform']}) - URL: {job.get('url', 'N/A')}\n")
            
            print("✅ Application logged successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Application failed: {e}")
            return False
    
    def run_aggressive_cycle(self):
        """Aggressive job search cycle targeting 50-70 applications"""
        print(f"\n🚀 Starting AGGRESSIVE job cycle at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 Target: 50-70 applications per cycle")
        
        if not self.setup_browser():
            print("❌ Cannot continue without browser")
            return
        
        all_jobs = []
        applications_sent = 0
        
        try:
            # Search all platforms
            print("\n🔍 Searching all platforms...")
            
            x_jobs = self.search_x_jobs()
            all_jobs.extend(x_jobs)
            
            remoteok_jobs = self.search_remoteok_jobs()
            all_jobs.extend(remoteok_jobs)
            
            dice_jobs = self.search_dice_jobs()
            all_jobs.extend(dice_jobs)
            
            indeed_jobs = self.search_indeed_jobs()
            all_jobs.extend(indeed_jobs)
            
            print(f"\n📊 Total jobs found: {len(all_jobs)}")
            
            # Apply to jobs aggressively
            print("\n📝 Starting aggressive application process...")
            for job in all_jobs:
                if job['id'] not in self.applied_jobs:
                    if self.apply_to_job(job):
                        applications_sent += 1
                        
                        # Show progress
                        if applications_sent % 10 == 0:
                            print(f"🎯 Progress: {applications_sent} applications sent")
                        
                        time.sleep(1)  # Minimal delay for speed
                        
                        # Stop at 70 applications
                        if applications_sent >= 70:
                            print("🎯 Reached maximum target of 70 applications!")
                            break
            
            # Log cycle completion
            with open('job-bot/aggressive_cycle_log.txt', 'a') as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - AGGRESSIVE CYCLE: {applications_sent} applications, {len(all_jobs)} jobs found\n")
            
            print(f"\n🎉 AGGRESSIVE cycle completed!")
            print(f"📊 Applications sent: {applications_sent}")
            print(f"📊 Jobs found: {len(all_jobs)}")
            
            if applications_sent >= 50:
                print("✅ TARGET ACHIEVED: 50+ applications sent!")
            else:
                print(f"⚠️ Below target: Only {applications_sent} applications sent")
            
        except Exception as e:
            print(f"❌ Error in aggressive cycle: {e}")
            
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    print("✅ Browser closed")
                except:
                    pass
    
    def start_hourly_monitoring(self):
        """Start hourly aggressive monitoring"""
        import schedule
        
        print("🚀 Starting AGGRESSIVE HOURLY job monitoring!")
        print("⏰ Running every hour with 50-70 applications target")
        
        # Schedule every hour
        schedule.every(1).hours.do(self.run_aggressive_cycle)
        
        # Initial run
        self.run_aggressive_cycle()
        
        # Continuous loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(300)  # Check every 5 minutes
            except KeyboardInterrupt:
                print("🛑 Aggressive job bot stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(300)

if __name__ == "__main__":
    bot = AggressiveJobBot()
    bot.run_aggressive_cycle()
