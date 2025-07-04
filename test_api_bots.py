#!/usr/bin/env python3
"""
Test script for API-based job bot functionality
"""

import requests
import time
import json
from datetime import datetime
from config import Config
from resume_analyzer import ResumeAnalyzer

class APIJobBotTester:
    def __init__(self):
        print("🔧 Initializing API Job Bot Tester...")
        
        # Test configuration loading
        try:
            self.config = Config()
            self.user_config = self.config.load_config()
            print("✅ Configuration loaded successfully")
        except Exception as e:
            print(f"❌ Configuration failed: {e}")
            self.user_config = None
        
        # Test resume analyzer
        try:
            self.resume_analyzer = ResumeAnalyzer()
            self.resume_data = self.resume_analyzer.analyze_resume()
            print("✅ Resume analyzer working")
        except Exception as e:
            print(f"❌ Resume analyzer failed: {e}")
            self.resume_data = None
            
        self.applied_jobs = set()
        
    def test_remoteok_api(self):
        """Test RemoteOK API job search"""
        print("\n🔍 Testing RemoteOK API...")
        try:
            url = "https://remoteok.io/api"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                jobs = response.json()[1:]  # Skip first item (legal notice)
                print(f"✅ RemoteOK API responding - {len(jobs)} jobs available")
                
                # Filter for relevant jobs
                relevant_jobs = []
                skills = ['devops', 'aws', 'docker', 'kubernetes', 'python', 'engineer']
                
                for job in jobs[:20]:  # Check first 20 jobs
                    title = job.get('position', '').lower()
                    description = job.get('description', '').lower()
                    tags = ' '.join(job.get('tags', [])).lower() if job.get('tags') else ''
                    
                    job_text = f"{title} {description} {tags}"
                    
                    if any(skill in job_text for skill in skills):
                        relevant_jobs.append({
                            'platform': 'RemoteOK',
                            'title': job.get('position'),
                            'company': job.get('company'),
                            'url': job.get('url'),
                            'id': job.get('id'),
                            'tags': job.get('tags', [])
                        })
                
                print(f"✅ Found {len(relevant_jobs)} relevant jobs:")
                for i, job in enumerate(relevant_jobs[:5], 1):
                    print(f"   {i}. {job['title']} at {job['company']}")
                    
                return relevant_jobs
            else:
                print(f"❌ RemoteOK API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ RemoteOK API test failed: {e}")
            return []
    
    def test_github_jobs_simulation(self):
        """Simulate GitHub Jobs search (since API was discontinued)"""
        print("\n🔍 Testing GitHub Jobs simulation...")
        
        # Simulate finding GitHub-related jobs
        simulated_jobs = [
            {
                'platform': 'GitHub',
                'title': 'DevOps Engineer - Remote',
                'company': 'GitHub-Partner Corp',
                'url': 'https://github.com/jobs/devops-engineer-1',
                'id': 'github_1',
                'tags': ['devops', 'aws', 'docker']
            },
            {
                'platform': 'GitHub',
                'title': 'Site Reliability Engineer',
                'company': 'OpenSource Tech',
                'url': 'https://github.com/jobs/sre-2',
                'id': 'github_2',
                'tags': ['sre', 'kubernetes', 'monitoring']
            }
        ]
        
        print(f"✅ Simulated {len(simulated_jobs)} GitHub-related jobs:")
        for i, job in enumerate(simulated_jobs, 1):
            print(f"   {i}. {job['title']} at {job['company']}")
            
        return simulated_jobs
    
    def test_indeed_simulation(self):
        """Simulate Indeed job search (requires scraping or paid API)"""
        print("\n🔍 Testing Indeed job search simulation...")
        
        # Simulate Indeed jobs (in real implementation, this would scrape or use paid API)
        simulated_jobs = [
            {
                'platform': 'Indeed',
                'title': 'Cloud Engineer - AWS',
                'company': 'CloudFirst Solutions',
                'url': 'https://indeed.com/job/cloud-engineer-123',
                'id': 'indeed_1',
                'tags': ['aws', 'cloud', 'terraform']
            },
            {
                'platform': 'Indeed',
                'title': 'DevOps Specialist',
                'company': 'TechStart Inc',
                'url': 'https://indeed.com/job/devops-specialist-456',
                'id': 'indeed_2',
                'tags': ['devops', 'ci/cd', 'jenkins']
            }
        ]
        
        print(f"✅ Simulated {len(simulated_jobs)} Indeed jobs:")
        for i, job in enumerate(simulated_jobs, 1):
            print(f"   {i}. {job['title']} at {job['company']}")
            
        return simulated_jobs
    
    def simulate_job_application(self, job):
        """Simulate applying to a job"""
        print(f"\n📝 SIMULATING APPLICATION:")
        print(f"   Job: {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Platform: {job['platform']}")
        
        # Mark as applied
        self.applied_jobs.add(job['id'])
        
        # Simulate cover letter generation
        cover_letter = f"""
Dear {job['company']} Hiring Team,

I am writing to express my interest in the {job['title']} position. 
With my background in DevOps, AWS, and cloud infrastructure, I believe 
I would be a great fit for this role.

Skills relevant to this position:
{', '.join(job.get('tags', ['DevOps', 'AWS', 'Python']))}

Best regards,
Test User
        """.strip()
        
        # Log application
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('test_applications.txt', 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} - SIMULATED APPLICATION: {job['title']} at {job['company']} ({job['platform']})\n")
        
        print("   ✅ Application simulated successfully!")
        time.sleep(1)  # Simulate processing time
        return True
    
    def run_comprehensive_test(self):
        """Run comprehensive test of all bot functionality"""
        print("=" * 60)
        print("🤖 COMPREHENSIVE JOB BOT TEST")
        print("=" * 60)
        
        all_jobs = []
        
        # Test API-based job searches
        all_jobs.extend(self.test_remoteok_api())
        all_jobs.extend(self.test_github_jobs_simulation())
        all_jobs.extend(self.test_indeed_simulation())
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total jobs found: {len(all_jobs)}")
        
        # Test applications
        applications_sent = 0
        print(f"\n🎯 TESTING APPLICATIONS:")
        
        for job in all_jobs[:10]:  # Apply to first 10 jobs
            if job['id'] not in self.applied_jobs:
                if self.simulate_job_application(job):
                    applications_sent += 1
        
        print(f"\n✅ TEST COMPLETE!")
        print(f"   Total applications simulated: {applications_sent}")
        print(f"   Success rate: 100% (simulated)")
        
        # Test file logging
        try:
            with open('test_applications.txt', 'r') as f:
                lines = f.readlines()
            print(f"   Application log entries: {len(lines)}")
            print("   ✅ File logging working")
        except:
            print("   ❌ File logging failed")
        
        return {
            'jobs_found': len(all_jobs),
            'applications_sent': applications_sent,
            'configuration_working': self.user_config is not None,
            'resume_analyzer_working': self.resume_data is not None,
            'api_remoteok_working': len([j for j in all_jobs if j['platform'] == 'RemoteOK']) > 0
        }

if __name__ == "__main__":
    tester = APIJobBotTester()
    results = tester.run_comprehensive_test()
    
    print("\n" + "=" * 60)
    print("🔍 DETAILED TEST RESULTS:")
    print("=" * 60)
    for key, value in results.items():
        status = "✅" if value else "❌"
        print(f"{status} {key.replace('_', ' ').title()}: {value}")
