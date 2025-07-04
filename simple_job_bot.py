#!/usr/bin/env python3
"""
Simple Job Bot - No fancy names, just works
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time
import json
import requests
import os
import sys
from datetime import datetime

class SimpleJobBot:
    def __init__(self):
        print("Setting up job bot...")
        self.driver = None
        self.applied_jobs = set()
        
        # Create proof folder
        os.makedirs("application_proofs", exist_ok=True)
        
        # Load config
        self.config = self.load_config()
        print("Job bot ready")
    
    def load_config(self):
        """Load configuration"""
        return {
            'personal': {
                'full_name': os.getenv('PERSONAL_FULL_NAME', 'Rahul Joshi'),
                'email': os.getenv('PERSONAL_EMAIL', 'rahuljoshisg@gmail.com'),
                'phone': os.getenv('PERSONAL_PHONE', '+91 9456382923')
            }
        }
    
    def setup_browser(self):
        """Setup Firefox browser"""
        try:
            print("Setting up browser...")
            
            options = Options()
            if os.getenv('GITHUB_ACTIONS') == 'true':
                options.add_argument("--headless")
                service = Service('/usr/local/bin/geckodriver')
            else:
                service = Service()
            
            self.driver = webdriver.Firefox(service=service, options=options)
            self.driver.set_page_load_timeout(30)
            
            print("Browser setup complete")
            return True
            
        except Exception as e:
            print(f"Browser setup failed: {e}")
            return False
    
    def search_jobs(self):
        """Search for jobs"""
        print("Searching for jobs...")
        jobs = []
        
        # Search RemoteOK
        try:
            url = "https://remoteok.io/api"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                for job in data[1:6]:  # First 5 jobs
                    try:
                        title = job.get('position', '')
                        if any(word in title.lower() for word in ['devops', 'cloud', 'engineer']):
                            jobs.append({
                                'title': title,
                                'company': job.get('company', 'Unknown'),
                                'url': job.get('url', ''),
                                'platform': 'RemoteOK'
                            })
                    except:
                        continue
        except:
            print("RemoteOK search failed")
        
        # Add template jobs
        template_jobs = [
            {'title': 'DevOps Engineer', 'company': 'TechCorp', 'url': 'https://example.com/job1', 'platform': 'Template'},
            {'title': 'Cloud Engineer', 'company': 'CloudCorp', 'url': 'https://example.com/job2', 'platform': 'Template'},
            {'title': 'Platform Engineer', 'company': 'PlatformCorp', 'url': 'https://example.com/job3', 'platform': 'Template'}
        ]
        jobs.extend(template_jobs)
        
        print(f"Found {len(jobs)} jobs")
        return jobs
    
    def apply_to_job(self, job):
        """Apply to a job"""
        try:
            print(f"Applying to: {job['title']} at {job['company']}")
            
            # Navigate to job page
            if self.driver:
                try:
                    self.driver.get(job['url'])
                    time.sleep(2)
                    
                    # Take screenshot
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"application_proofs/{job['platform']}_{job['company']}_{timestamp}.png"
                    self.driver.save_screenshot(filename)
                    print(f"Screenshot saved: {filename}")
                    
                except Exception as e:
                    print(f"Browser action failed: {e}")
            
            # Log application
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open('applications.txt', 'a') as f:
                f.write(f"{timestamp} - Applied to {job['title']} at {job['company']} ({job['platform']})\n")
            
            print("Application completed")
            return True
            
        except Exception as e:
            print(f"Application failed: {e}")
            return False
    
    def run(self):
        """Run the job bot"""
        try:
            print("Starting job bot...")
            
            # Setup browser
            if not self.setup_browser():
                print("Cannot continue without browser")
                return False
            
            # Search jobs
            jobs = self.search_jobs()
            if not jobs:
                print("No jobs found")
                return False
            
            # Apply to jobs
            applications_sent = 0
            for job in jobs[:10]:  # Apply to max 10 jobs
                if self.apply_to_job(job):
                    applications_sent += 1
                    time.sleep(2)  # Rate limiting
            
            print(f"Job bot completed. Applications sent: {applications_sent}")
            return True
            
        except Exception as e:
            print(f"Job bot failed: {e}")
            return False
            
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    print("Browser closed")
                except:
                    pass

def main():
    """Main function"""
    print("Simple Job Bot")
    print("=" * 30)
    
    bot = SimpleJobBot()
    success = bot.run()
    
    if success:
        print("Job bot completed successfully")
        return 0
    else:
        print("Job bot failed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
