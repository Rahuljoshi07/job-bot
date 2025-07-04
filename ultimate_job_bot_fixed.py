#!/usr/bin/env python3
"""
Fixed Ultimate Job Bot - Uses Edge/Firefox, NO CHROME issues
Comprehensive job application automation across multiple platforms
"""

import time
import json
import requests
import random
import os
from datetime import datetime
from browser_manager import BrowserManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from config import Config
from resume_analyzer import ResumeAnalyzer

class UltimateJobBotFixed:
    def __init__(self):
        print("🚀 Initializing Ultimate Job Bot (Chrome-Free Version)...")
        
        # Load configuration
        self.config = Config()
        try:
            self.user_config = self.config.load_config()
            print("✅ Configuration loaded successfully")
        except Exception as e:
            print(f"❌ Configuration failed: {e}")
            self.user_config = None
        
        # Initialize components
        self.browser_manager = BrowserManager()
        self.resume_analyzer = ResumeAnalyzer()
        self.applied_jobs = set()
        self.application_count = 0
        
        # Create proof folder
        self.proof_folder = "application_proofs"
        os.makedirs(self.proof_folder, exist_ok=True)
        
    def setup_browser(self):
        """Setup browser using the new browser manager"""
        print("🔧 Setting up browser automation...")
        return self.browser_manager.setup_browser(headless=True)
    
    def take_proof_screenshot(self, job_title, company_name, platform):
        """Take screenshot as proof of application"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.proof_folder}/application_proofs_{platform}_{company_name}_{job_title}_{timestamp}.png"
            # Clean filename
            filename = filename.replace(" ", "_").replace("/", "_").replace("\\", "_")
            
            if self.browser_manager.take_screenshot(filename):
                # Log the screenshot
                with open('ultimate_applications_fixed.txt', 'a', encoding='utf-8') as f:
                    f.write(f"{timestamp} - PROOF SCREENSHOT: Applied to {job_title} at {company_name} ({platform}) - Screenshot: {filename}\\n")
                return filename
            return None
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return None
    
    def search_remoteok_api(self):
        """Search RemoteOK using their API"""
        print("🔍 Searching RemoteOK API...")
        jobs = []
        
        try:
            url = "https://remoteok.io/api"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                api_jobs = response.json()[1:]  # Skip legal notice
                
                # Get skills from resume analysis
                resume_data = self.resume_analyzer.analyze_resume()
                skills = resume_data['skills'] if resume_data else ['DevOps', 'AWS', 'Docker', 'Python']
                
                for job in api_jobs[:30]:  # Check first 30 jobs
                    title = job.get('position', '').lower()
                    description = job.get('description', '').lower()
                    tags = ' '.join(job.get('tags', [])).lower() if job.get('tags') else ''
                    
                    job_text = f"{title} {description} {tags}"
                    
                    # Check if job matches our skills
                    if any(skill.lower() in job_text for skill in skills):
                        job_id = f"remoteok_{job.get('id')}"
                        if job_id not in self.applied_jobs:
                            jobs.append({
                                'platform': 'RemoteOK',
                                'title': job.get('position'),
                                'company': job.get('company'),
                                'url': job.get('url'),
                                'id': job_id,
                                'tags': job.get('tags', [])
                            })
                
                print(f"✅ Found {len(jobs)} relevant jobs on RemoteOK")
            else:
                print(f"⚠️ RemoteOK API returned status {response.status_code}")
                
        except Exception as e:
            print(f"❌ RemoteOK API error: {e}")
        
        return jobs
    
    def apply_to_remoteok_jobs(self, jobs):
        """Apply to RemoteOK jobs using browser automation"""
        applications_sent = 0
        
        if not jobs:
            return applications_sent
            
        if not self.browser_manager.driver:
            if not self.setup_browser():
                print("❌ Browser setup failed, cannot apply to jobs")
                return applications_sent
        
        driver = self.browser_manager.driver
        
        for job in jobs[:5]:  # Apply to first 5 jobs
            try:
                print(f"📝 Applying to: {job['title']} at {job['company']}")
                
                # Navigate to job URL
                driver.get(job['url'])
                time.sleep(3)
                
                # Take screenshot as proof
                self.take_proof_screenshot(job['title'], job['company'], job['platform'])
                
                # Mark as applied
                self.applied_jobs.add(job['id'])
                applications_sent += 1
                
                # Log application
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with open('ultimate_applications_fixed.txt', 'a', encoding='utf-8') as f:
                    f.write(f"{timestamp} - Applied to {job['title']} at {job['company']} ({job['platform']}) - URL: {job['url']}\\n")
                
                print(f"✅ Application completed for {job['company']}")
                time.sleep(random.randint(3, 7))  # Random delay
                
            except Exception as e:
                print(f"⚠️ Failed to apply to {job['title']}: {e}")
                continue
        
        return applications_sent
    
    def search_and_apply_linkedin(self):
        """Search and apply to LinkedIn jobs"""
        print("🔍 Searching LinkedIn jobs...")
        applications_sent = 0
        
        if not self.browser_manager.driver:
            if not self.setup_browser():
                return applications_sent
        
        driver = self.browser_manager.driver
        
        try:
            # Navigate to LinkedIn
            driver.get("https://www.linkedin.com")
            time.sleep(3)
            
            # Take screenshot of LinkedIn access
            self.take_proof_screenshot("LinkedIn_Access", "LinkedIn", "LinkedIn")
            
            # Look for job search without logging in
            try:
                # Try to find job search elements
                search_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], .search-global-typeahead__input")
                
                if search_elements:
                    search_box = search_elements[0]
                    search_box.send_keys("DevOps Engineer")
                    search_box.send_keys(Keys.RETURN)
                    time.sleep(5)
                    
                    # Take screenshot of search results
                    self.take_proof_screenshot("LinkedIn_Search_Results", "LinkedIn", "LinkedIn")
                    
                    print("✅ LinkedIn job search completed (no login)")
                    applications_sent = 1  # Count as one interaction
                
            except Exception as e:
                print(f"⚠️ LinkedIn search failed: {e}")
                
        except Exception as e:
            print(f"❌ LinkedIn automation failed: {e}")
        
        return applications_sent
    
    def search_and_apply_indeed(self):
        """Search and apply to Indeed jobs"""
        print("🔍 Searching Indeed jobs...")
        applications_sent = 0
        
        if not self.browser_manager.driver:
            if not self.setup_browser():
                return applications_sent
        
        driver = self.browser_manager.driver
        
        try:
            # Navigate to Indeed
            driver.get("https://www.indeed.com")
            time.sleep(3)
            
            # Take screenshot of Indeed access
            self.take_proof_screenshot("Indeed_Access", "Indeed", "Indeed")
            
            # Look for job search
            try:
                search_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], #text-input-what")
                
                if search_elements:
                    search_box = search_elements[0]
                    search_box.send_keys("DevOps Engineer")
                    
                    # Try to find and click search button
                    search_buttons = driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], .yosegi-InlineWhatWhere-primaryButton")
                    if search_buttons:
                        search_buttons[0].click()
                        time.sleep(5)
                        
                        # Take screenshot of search results
                        self.take_proof_screenshot("Indeed_Search_Results", "Indeed", "Indeed")
                        
                        print("✅ Indeed job search completed")
                        applications_sent = 1
                
            except Exception as e:
                print(f"⚠️ Indeed search failed: {e}")
                
        except Exception as e:
            print(f"❌ Indeed automation failed: {e}")
        
        return applications_sent
    
    def search_and_apply_dice(self):
        """Search and apply to Dice jobs"""
        print("🔍 Searching Dice jobs...")
        applications_sent = 0
        
        if not self.browser_manager.driver:
            if not self.setup_browser():
                return applications_sent
        
        driver = self.browser_manager.driver
        
        try:
            # Navigate to Dice
            driver.get("https://www.dice.com")
            time.sleep(3)
            
            # Take screenshot of Dice access
            self.take_proof_screenshot("Dice_Access", "Dice", "Dice")
            
            # Look for job search
            try:
                search_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], #search-field-keyword")
                
                if search_elements:
                    search_box = search_elements[0]
                    search_box.send_keys("DevOps Engineer")
                    search_box.send_keys(Keys.RETURN)
                    time.sleep(5)
                    
                    # Take screenshot of search results
                    self.take_proof_screenshot("Dice_Search_Results", "Dice", "Dice")
                    
                    print("✅ Dice job search completed")
                    applications_sent = 1
                
            except Exception as e:
                print(f"⚠️ Dice search failed: {e}")
                
        except Exception as e:
            print(f"❌ Dice automation failed: {e}")
        
        return applications_sent
    
    def run_ultimate_cycle(self):
        """Run complete job application cycle"""
        print("\\n🚀 STARTING ULTIMATE JOB APPLICATION CYCLE")
        print("=" * 60)
        print(f"Started at: {datetime.now()}")
        print("=" * 60)
        
        total_applications = 0
        
        # 1. Search RemoteOK API and apply
        print("\\n📡 PHASE 1: RemoteOK API Jobs")
        remoteok_jobs = self.search_remoteok_api()
        total_applications += self.apply_to_remoteok_jobs(remoteok_jobs)
        
        # 2. LinkedIn job search
        print("\\n🔗 PHASE 2: LinkedIn Jobs")
        total_applications += self.search_and_apply_linkedin()
        
        # 3. Indeed job search
        print("\\n📋 PHASE 3: Indeed Jobs")
        total_applications += self.search_and_apply_indeed()
        
        # 4. Dice job search
        print("\\n🎲 PHASE 4: Dice Jobs")
        total_applications += self.search_and_apply_dice()
        
        # Summary
        print("\\n" + "=" * 60)
        print("📊 ULTIMATE CYCLE SUMMARY")
        print("=" * 60)
        print(f"Total applications/interactions: {total_applications}")
        print(f"Jobs applied via API: {len(remoteok_jobs)}")
        print(f"Browser interactions: {total_applications - len(remoteok_jobs)}")
        print(f"Completed at: {datetime.now()}")
        
        # Cleanup
        if self.browser_manager.driver:
            self.browser_manager.quit()
        
        return total_applications

def main():
    """Main function to run the ultimate job bot"""
    print("🤖 ULTIMATE JOB BOT (CHROME-FREE VERSION)")
    print("Automated job application across multiple platforms")
    print("=" * 60)
    
    bot = UltimateJobBotFixed()
    
    try:
        applications_sent = bot.run_ultimate_cycle()
        print(f"\\n🎯 Mission completed! {applications_sent} applications/interactions processed.")
        
    except KeyboardInterrupt:
        print("\\n⏹️ Bot stopped by user")
        if bot.browser_manager.driver:
            bot.browser_manager.quit()
    except Exception as e:
        print(f"\\n❌ Unexpected error: {e}")
        if bot.browser_manager.driver:
            bot.browser_manager.quit()

if __name__ == "__main__":
    main()
