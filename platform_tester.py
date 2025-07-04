#!/usr/bin/env python3
"""
Comprehensive Platform Testing Script
Tests all job platforms to identify what's working and what's not
"""

import time
import requests
import json
from datetime import datetime
from browser_manager import BrowserManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from config import Config
from resume_analyzer import ResumeAnalyzer

class PlatformTester:
    def __init__(self):
        self.config = Config()
        try:
            self.user_config = self.config.load_config()
            print("✅ Configuration loaded")
        except Exception as e:
            print(f"❌ Configuration failed: {e}")
            self.user_config = None
        
        self.browser_manager = BrowserManager()
        self.test_results = {}
        
    def test_api_platform(self, platform_name, test_func):
        """Test an API-based platform"""
        print(f"\n{'='*60}")
        print(f"🔍 TESTING: {platform_name} (API)")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            self.test_results[platform_name] = {
                'type': 'API',
                'status': 'WORKING',
                'details': result,
                'error': None
            }
            print(f"✅ {platform_name}: WORKING - {result}")
            return True
        except Exception as e:
            self.test_results[platform_name] = {
                'type': 'API',
                'status': 'FAILED',
                'details': None,
                'error': str(e)
            }
            print(f"❌ {platform_name}: FAILED - {e}")
            return False
    
    def test_browser_platform(self, platform_name, test_func):
        """Test a browser-based platform"""
        print(f"\n{'='*60}")
        print(f"🔍 TESTING: {platform_name} (Browser)")
        print(f"{'='*60}")
        
        if not self.browser_manager.driver:
            if not self.browser_manager.setup_browser(headless=True):
                self.test_results[platform_name] = {
                    'type': 'Browser',
                    'status': 'FAILED',
                    'details': None,
                    'error': 'Browser setup failed'
                }
                print(f"❌ {platform_name}: FAILED - Browser setup failed")
                return False
        
        try:
            result = test_func()
            self.test_results[platform_name] = {
                'type': 'Browser',
                'status': 'WORKING',
                'details': result,
                'error': None
            }
            print(f"✅ {platform_name}: WORKING - {result}")
            return True
        except Exception as e:
            self.test_results[platform_name] = {
                'type': 'Browser',
                'status': 'FAILED',
                'details': None,
                'error': str(e)
            }
            print(f"❌ {platform_name}: FAILED - {e}")
            return False
    
    # API Platform Tests
    def test_remoteok_api(self):
        """Test RemoteOK API"""
        url = "https://remoteok.io/api"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            jobs = response.json()[1:]  # Skip legal notice
            relevant_jobs = []
            
            for job in jobs[:20]:
                title = job.get('position', '').lower()
                if any(skill in title for skill in ['devops', 'cloud', 'engineer', 'developer']):
                    relevant_jobs.append(job.get('position'))
            
            return f"API working, {len(jobs)} total jobs, {len(relevant_jobs)} relevant jobs"
        else:
            raise Exception(f"API returned status {response.status_code}")
    
    def test_stackoverflow_api(self):
        """Test StackOverflow Jobs API"""
        # Note: StackOverflow discontinued their jobs API, but we can test the endpoint
        try:
            url = "https://api.stackexchange.com/2.3/questions"
            params = {
                'order': 'desc',
                'sort': 'activity',
                'tagged': 'devops',
                'site': 'stackoverflow'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return f"StackOverflow API working, {len(data.get('items', []))} items found"
            else:
                raise Exception(f"API returned status {response.status_code}")
        except Exception as e:
            raise Exception(f"StackOverflow API test failed: {e}")
    
    def test_github_api(self):
        """Test GitHub API for job-related repos"""
        url = "https://api.github.com/search/repositories"
        params = {
            'q': 'devops jobs',
            'sort': 'updated',
            'per_page': 10
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return f"GitHub API working, {data.get('total_count', 0)} repos found"
        else:
            raise Exception(f"GitHub API returned status {response.status_code}")
    
    # Browser Platform Tests
    def test_linkedin_browser(self):
        """Test LinkedIn access"""
        driver = self.browser_manager.driver
        
        try:
            driver.get("https://www.linkedin.com")
            time.sleep(3)
            
            # Check if we can access LinkedIn
            title = driver.title
            if "linkedin" in title.lower():
                # Try to find login elements
                login_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='login'], .nav__button-secondary")
                return f"LinkedIn accessible, title: {title}, login elements: {len(login_elements)}"
            else:
                raise Exception(f"Unexpected page title: {title}")
                
        except Exception as e:
            raise Exception(f"LinkedIn browser test failed: {e}")
    
    def test_indeed_browser(self):
        """Test Indeed access"""
        driver = self.browser_manager.driver
        
        try:
            driver.get("https://www.indeed.com")
            time.sleep(3)
            
            title = driver.title
            if "indeed" in title.lower():
                # Look for job search elements
                search_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], .yosegi-InlineWhatWhere-primaryInput")
                return f"Indeed accessible, title: {title}, search elements: {len(search_elements)}"
            else:
                raise Exception(f"Unexpected page title: {title}")
                
        except Exception as e:
            raise Exception(f"Indeed browser test failed: {e}")
    
    def test_glassdoor_browser(self):
        """Test Glassdoor access"""
        driver = self.browser_manager.driver
        
        try:
            driver.get("https://www.glassdoor.com")
            time.sleep(3)
            
            title = driver.title
            if "glassdoor" in title.lower():
                # Look for job search elements
                search_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], .SearchBar")
                return f"Glassdoor accessible, title: {title}, search elements: {len(search_elements)}"
            else:
                raise Exception(f"Unexpected page title: {title}")
                
        except Exception as e:
            raise Exception(f"Glassdoor browser test failed: {e}")
    
    def test_dice_browser(self):
        """Test Dice access"""
        driver = self.browser_manager.driver
        
        try:
            driver.get("https://www.dice.com")
            time.sleep(3)
            
            title = driver.title
            if "dice" in title.lower():
                # Look for job search elements
                search_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], .search-field")
                return f"Dice accessible, title: {title}, search elements: {len(search_elements)}"
            else:
                raise Exception(f"Unexpected page title: {title}")
                
        except Exception as e:
            raise Exception(f"Dice browser test failed: {e}")
    
    def test_flexjobs_browser(self):
        """Test FlexJobs access"""
        driver = self.browser_manager.driver
        
        try:
            driver.get("https://www.flexjobs.com")
            time.sleep(3)
            
            title = driver.title
            if "flexjobs" in title.lower() or "flex" in title.lower():
                # Look for job search elements
                search_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], .search-input")
                return f"FlexJobs accessible, title: {title}, search elements: {len(search_elements)}"
            else:
                raise Exception(f"Unexpected page title: {title}")
                
        except Exception as e:
            raise Exception(f"FlexJobs browser test failed: {e}")
    
    def test_weworkremotely_browser(self):
        """Test WeWorkRemotely access"""
        driver = self.browser_manager.driver
        
        try:
            driver.get("https://weworkremotely.com")
            time.sleep(3)
            
            title = driver.title
            if "remote" in title.lower():
                # Look for job listings
                job_elements = driver.find_elements(By.CSS_SELECTOR, ".job, .listing, article")
                return f"WeWorkRemotely accessible, title: {title}, job elements: {len(job_elements)}"
            else:
                raise Exception(f"Unexpected page title: {title}")
                
        except Exception as e:
            raise Exception(f"WeWorkRemotely browser test failed: {e}")
    
    def test_twitter_browser(self):
        """Test Twitter/X access"""
        driver = self.browser_manager.driver
        
        try:
            driver.get("https://x.com")
            time.sleep(3)
            
            title = driver.title
            # Look for Twitter/X elements
            login_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='login'], [data-testid*='login']")
            return f"Twitter/X accessible, title: {title}, login elements: {len(login_elements)}"
                
        except Exception as e:
            raise Exception(f"Twitter/X browser test failed: {e}")
    
    def run_all_tests(self):
        """Run all platform tests"""
        print("🤖 COMPREHENSIVE PLATFORM TESTING")
        print("=" * 80)
        print(f"Started at: {datetime.now()}")
        print("=" * 80)
        
        # Test API Platforms
        print("\n📡 TESTING API-BASED PLATFORMS")
        print("-" * 50)
        
        api_tests = [
            ("RemoteOK", self.test_remoteok_api),
            ("StackOverflow", self.test_stackoverflow_api),
            ("GitHub", self.test_github_api),
        ]
        
        for platform, test_func in api_tests:
            self.test_api_platform(platform, test_func)
        
        # Test Browser Platforms
        print("\n🌐 TESTING BROWSER-BASED PLATFORMS")
        print("-" * 50)
        
        browser_tests = [
            ("LinkedIn", self.test_linkedin_browser),
            ("Indeed", self.test_indeed_browser),
            ("Glassdoor", self.test_glassdoor_browser),
            ("Dice", self.test_dice_browser),
            ("FlexJobs", self.test_flexjobs_browser),
            ("WeWorkRemotely", self.test_weworkremotely_browser),
            ("Twitter/X", self.test_twitter_browser),
        ]
        
        for platform, test_func in browser_tests:
            self.test_browser_platform(platform, test_func)
        
        # Generate summary
        self.generate_summary()
        
        # Cleanup
        if self.browser_manager.driver:
            self.browser_manager.quit()
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE PLATFORM TEST RESULTS")
        print("=" * 80)
        
        total_platforms = len(self.test_results)
        working_platforms = len([r for r in self.test_results.values() if r['status'] == 'WORKING'])
        failed_platforms = total_platforms - working_platforms
        
        print(f"Total Platforms Tested: {total_platforms}")
        print(f"Working Platforms: {working_platforms}")
        print(f"Failed Platforms: {failed_platforms}")
        print(f"Success Rate: {(working_platforms/total_platforms)*100:.1f}%")
        
        print("\n" + "=" * 80)
        print("🔍 DETAILED RESULTS BY PLATFORM")
        print("=" * 80)
        
        # Group by type
        api_platforms = {k: v for k, v in self.test_results.items() if v['type'] == 'API'}
        browser_platforms = {k: v for k, v in self.test_results.items() if v['type'] == 'Browser'}
        
        print("\n📡 API-BASED PLATFORMS:")
        for platform, result in api_platforms.items():
            status_icon = "✅" if result['status'] == 'WORKING' else "❌"
            print(f"{status_icon} {platform}: {result['status']}")
            if result['status'] == 'WORKING':
                print(f"   └─ {result['details']}")
            else:
                print(f"   └─ Error: {result['error']}")
        
        print("\n🌐 BROWSER-BASED PLATFORMS:")
        for platform, result in browser_platforms.items():
            status_icon = "✅" if result['status'] == 'WORKING' else "❌"
            print(f"{status_icon} {platform}: {result['status']}")
            if result['status'] == 'WORKING':
                print(f"   └─ {result['details']}")
            else:
                print(f"   └─ Error: {result['error']}")
        
        print("\n" + "=" * 80)
        print("💡 RECOMMENDATIONS")
        print("=" * 80)
        
        working_api = [k for k, v in api_platforms.items() if v['status'] == 'WORKING']
        working_browser = [k for k, v in browser_platforms.items() if v['status'] == 'WORKING']
        
        if working_api:
            print("✅ WORKING API PLATFORMS:")
            for platform in working_api:
                print(f"   • {platform} - Ready for immediate use")
        
        if working_browser:
            print("✅ WORKING BROWSER PLATFORMS:")
            for platform in working_browser:
                print(f"   • {platform} - Browser automation available")
        
        failed_api = [k for k, v in api_platforms.items() if v['status'] == 'FAILED']
        failed_browser = [k for k, v in browser_platforms.items() if v['status'] == 'FAILED']
        
        if failed_api:
            print("❌ FAILED API PLATFORMS:")
            for platform in failed_api:
                print(f"   • {platform} - Check API endpoints/keys")
        
        if failed_browser:
            print("❌ FAILED BROWSER PLATFORMS:")
            for platform in failed_browser:
                print(f"   • {platform} - Check browser compatibility")
        
        print("\n" + "=" * 80)
        print("🚀 NEXT STEPS")
        print("=" * 80)
        
        if working_platforms >= total_platforms * 0.5:
            print("✅ GOOD NEWS: Majority of platforms are working!")
            print("   • You can start job searching immediately")
            print("   • Focus on working platforms first")
        else:
            print("⚠️ ATTENTION NEEDED: Several platforms require fixes")
            print("   • Check network connectivity")
            print("   • Verify browser installation")
            print("   • Update credentials if needed")
        
        return self.test_results

if __name__ == "__main__":
    tester = PlatformTester()
    results = tester.run_all_tests()
