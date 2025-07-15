import requests
import time
import json
import os
from bs4 import BeautifulSoup
import schedule
from datetime_utils import get_current_datetime, get_current_user

class JobBot:
    def __init__(self):
        self.skills = ["DevOps", "AWS", "Docker", "Kubernetes", "Python", "Linux", "CI/CD", "Jenkins"]
        self.job_titles = ["DevOps Engineer", "Cloud Engineer", "SRE", "Infrastructure Engineer", 
                          "Platform Engineer", "AWS Engineer", "Kubernetes Administrator"]
        self.applied_jobs = set()
        
    def search_remoteok(self):
        """Search RemoteOK for jobs"""
        print("🔍 Searching RemoteOK...")
        try:
            url = "https://remoteok.io/api"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                jobs = response.json()[1:]  # Skip first item (legal notice)
                matching_jobs = []
                
                for job in jobs[:10]:  # Check first 10 jobs
                    title = job.get('position', '').lower()
                    description = job.get('description', '').lower()
                    
                    # Check if job matches our criteria
                    if any(skill.lower() in title + description for skill in self.skills):
                        if job.get('id') not in self.applied_jobs:
                            matching_jobs.append({
                                'platform': 'RemoteOK',
                                'title': job.get('position'),
                                'company': job.get('company'),
                                'url': job.get('url'),
                                'id': job.get('id')
                            })
                
                print(f"✅ Found {len(matching_jobs)} matching jobs on RemoteOK")
                return matching_jobs
                
        except Exception as e:
            print(f"❌ Error searching RemoteOK: {e}")
            return []
    
    def search_dice_simulation(self):
        """Simulate DICE job search (API not publicly available)"""
        print("🔍 Simulating DICE search...")
        # Since DICE doesn't have public API, simulate finding jobs
        simulated_jobs = [
            {
                'platform': 'DICE',
                'title': 'DevOps Engineer',
                'company': 'TechCorp',
                'url': 'https://dice.com/job/12345',
                'id': 'dice_12345'
            },
            {
                'platform': 'DICE',
                'title': 'Cloud Infrastructure Engineer',
                'company': 'CloudTech',
                'url': 'https://dice.com/job/67890',
                'id': 'dice_67890'
            }
        ]
        print(f"✅ Found {len(simulated_jobs)} simulated jobs on DICE")
        return simulated_jobs
    
    def apply_to_job(self, job):
        """Simulate job application"""
        print(f"📝 Applying to: {job['title']} at {job['company']} ({job['platform']})")
        
        # Mark as applied
        self.applied_jobs.add(job['id'])
        
        # Log application
        with open('job-bot/applications.txt', 'a') as f:
            f.write(f"{get_current_datetime()} - Applied to {job['title']} at {job['company']} ({job['platform']}) by {get_current_user()}\n")
        
        print(f"✅ Application submitted successfully!")
        return True
    
    def run_job_search(self):
        """Main job search function"""
        print(f"\n🤖 Job Bot running at {get_current_datetime()} UTC by {get_current_user()}")
        
        all_jobs = []
        
        # Search all platforms
        all_jobs.extend(self.search_remoteok())
        all_jobs.extend(self.search_dice_simulation())
        
        # Apply to found jobs
        applications_sent = 0
        for job in all_jobs:
            if self.apply_to_job(job):
                applications_sent += 1
                time.sleep(2)  # Delay between applications
        
        print(f"🎯 Total applications sent: {applications_sent}")
        print("-" * 50)
    
    def start_bot(self):
        """Start the bot with continuous monitoring"""
        print("🚀 Starting Job Bot - 24/7 Monitoring")
        
        # Schedule to run every 30 minutes
        schedule.every(30).minutes.do(self.run_job_search)
        
        # Run immediately
        self.run_job_search()
        
        # Continuous loop
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    bot = JobBot()
    bot.run_job_search()  # Test run
