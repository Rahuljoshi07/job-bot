#!/usr/bin/env python3
"""
Enhanced Platform Tester with Automatic Captcha Solving
Never gets stuck on CloudFlare or captchas
"""

import time
import requests
import json
from datetime import datetime
from browser_manager import BrowserManager
from captcha_solver import AdvancedCaptchaSolver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from config import Config
from resume_analyzer import ResumeAnalyzer

class EnhancedPlatformTester:
    def __init__(self):
        self.config = Config()
        try:
            self.user_config = self.config.load_config()
            print("✅ Configuration loaded")
        except Exception as e:
            print(f"❌ Configuration failed: {e}")
            self.user_config = None
        
        self.browser_manager = BrowserManager()
        self.captcha_solver = None
        self.test_results = {}
        
    def setup_browser_with_captcha_solver(self):
        """Setup browser with captcha solving capabilities"""
        print("🔧 Setting up browser with captcha solving...")
        
        if self.browser_manager.setup_browser(headless=False):  # Non-headless for captcha solving
            self.captcha_solver = AdvancedCaptchaSolver(self.browser_manager.driver)
            print("✅ Browser and captcha solver ready")
            return True
        else:
            print("❌ Browser setup failed")
            return False
    
    def smart_navigate_and_bypass(self, url, max_attempts=3):
        """Smart navigation with automatic security bypass"""
        print(f"🌐 Smart navigating to {url}...")
        
        if not self.browser_manager.driver:
            if not self.setup_browser_with_captcha_solver():
                return False
        
        driver = self.browser_manager.driver
        
        for attempt in range(max_attempts):
            try:
                print(f"🔄 Navigation attempt {attempt + 1}/{max_attempts}")
                
                # Navigate to URL
                driver.get(url)
                time.sleep(3)
                
                # Automatically bypass any security measures
                if self.captcha_solver.comprehensive_security_bypass(driver):
                    print(f"✅ Successfully accessed {url}")
                    return True
                else:
                    print(f"⚠️ Security bypass failed for {url}, retrying...")
                    time.sleep(5)
                    
            except Exception as e:
                print(f"❌ Navigation error attempt {attempt + 1}: {e}")
                time.sleep(3)
        
        print(f"❌ Failed to access {url} after {max_attempts} attempts")
        return False
    
    def test_glassdoor_with_bypass(self):
        """Test Glassdoor with automatic CloudFlare bypass"""
        print("🔍 Testing Glassdoor with bypass...")
        
        url = "https://www.glassdoor.com"
        
        if self.smart_navigate_and_bypass(url):
            driver = self.browser_manager.driver
            
            try:
                # Wait for page to fully load
                time.sleep(5)
                
                title = driver.title
                print(f"📄 Page title: {title}")
                
                # Look for job search elements
                search_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], .SearchBar, #searchbox")
                
                # Take screenshot as proof
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_name = f"glassdoor_access_proof_{timestamp}.png"
                self.browser_manager.take_screenshot(screenshot_name)
                
                return f"Glassdoor accessible, title: {title}, search elements: {len(search_elements)}, proof: {screenshot_name}"
            
            except Exception as e:
                print(f"❌ Error testing Glassdoor: {e}")
                return f"Error: {e}"
        else:
            return "Failed to bypass security measures"
    
    def test_weworkremotely_with_bypass(self):
        """Test WeWorkRemotely with automatic CloudFlare bypass"""
        print("🔍 Testing WeWorkRemotely with bypass...")
        
        url = "https://weworkremotely.com"
        
        if self.smart_navigate_and_bypass(url):
            driver = self.browser_manager.driver
            
            try:
                # Wait for page to fully load
                time.sleep(5)
                
                title = driver.title
                print(f"📄 Page title: {title}")
                
                # Look for job listings
                job_elements = driver.find_elements(By.CSS_SELECTOR, ".job, .listing, article, .job-listing")
                
                # Take screenshot as proof
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_name = f"weworkremotely_access_proof_{timestamp}.png"
                self.browser_manager.take_screenshot(screenshot_name)
                
                return f"WeWorkRemotely accessible, title: {title}, job elements: {len(job_elements)}, proof: {screenshot_name}"
            
            except Exception as e:
                print(f"❌ Error testing WeWorkRemotely: {e}")
                return f"Error: {e}"
        else:
            return "Failed to bypass security measures"
    
    def test_platform_with_bypass(self, platform_name, url, search_selectors):
        """Generic platform test with security bypass"""
        print(f"🔍 Testing {platform_name} with bypass...")
        
        if self.smart_navigate_and_bypass(url):
            driver = self.browser_manager.driver
            
            try:
                # Wait for page to fully load
                time.sleep(5)
                
                title = driver.title
                print(f"📄 Page title: {title}")
                
                # Look for search elements
                search_elements = []
                for selector in search_selectors:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    search_elements.extend(elements)
                
                # Take screenshot as proof
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_name = f"{platform_name.lower()}_access_proof_{timestamp}.png"
                self.browser_manager.take_screenshot(screenshot_name)
                
                return f"{platform_name} accessible, title: {title}, search elements: {len(search_elements)}, proof: {screenshot_name}"
            
            except Exception as e:
                print(f"❌ Error testing {platform_name}: {e}")
                return f"Error: {e}"
        else:
            return "Failed to bypass security measures"
    
    def test_api_platform(self, platform_name, test_func):
        """Test an API-based platform"""
        print(f"\\n{'='*60}")
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
    
    def test_browser_platform_enhanced(self, platform_name, test_func):
        """Test a browser-based platform with enhanced bypass"""
        print(f"\\n{'='*60}")
        print(f"🔍 TESTING: {platform_name} (Browser + Captcha Solver)")
        print(f"{'='*60}")
        
        if not self.browser_manager.driver:
            if not self.setup_browser_with_captcha_solver():
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
    
    # API Platform Tests (same as before)
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
    
    def run_comprehensive_enhanced_test(self):
        """Run comprehensive test with enhanced bypass capabilities"""
        print("🤖 ENHANCED COMPREHENSIVE PLATFORM TESTING")
        print("=" * 80)
        print(f"Started at: {datetime.now()}")
        print("With automatic captcha solving and CloudFlare bypass")
        print("=" * 80)
        
        # Test API Platforms
        print("\\n📡 TESTING API-BASED PLATFORMS")
        print("-" * 50)
        
        api_tests = [
            ("RemoteOK", self.test_remoteok_api),
            ("StackOverflow", self.test_stackoverflow_api),
            ("GitHub", self.test_github_api),
        ]
        
        for platform, test_func in api_tests:
            self.test_api_platform(platform, test_func)
        
        # Test Browser Platforms with Enhanced Bypass
        print("\\n🌐 TESTING BROWSER-BASED PLATFORMS (Enhanced)")
        print("-" * 50)
        
        enhanced_browser_tests = [
            ("Glassdoor (Enhanced)", self.test_glassdoor_with_bypass),
            ("WeWorkRemotely (Enhanced)", self.test_weworkremotely_with_bypass),
        ]
        
        for platform, test_func in enhanced_browser_tests:
            self.test_browser_platform_enhanced(platform, test_func)
        
        # Test other platforms with bypass
        other_platforms = [
            ("LinkedIn (Enhanced)", "https://www.linkedin.com", ["input[type='text']", ".search-global-typeahead__input"]),
            ("Indeed (Enhanced)", "https://www.indeed.com", ["input[type='text']", "#text-input-what"]),
            ("Dice (Enhanced)", "https://www.dice.com", ["input[type='text']", "#search-field-keyword"]),
            ("FlexJobs (Enhanced)", "https://www.flexjobs.com", ["input[type='text']", ".search-input"]),
        ]
        
        for platform_name, url, selectors in other_platforms:
            result = self.test_platform_with_bypass(platform_name, url, selectors)
            self.test_results[platform_name] = {
                'type': 'Browser',
                'status': 'WORKING' if 'accessible' in result else 'FAILED',
                'details': result,
                'error': None if 'accessible' in result else result
            }
            print(f"{'✅' if 'accessible' in result else '❌'} {platform_name}: {result}")
        
        # Generate enhanced summary
        self.generate_enhanced_summary()
        
        # Cleanup
        if self.browser_manager.driver:
            self.browser_manager.quit()
    
    def generate_enhanced_summary(self):
        """Generate enhanced test summary"""
        print("\\n" + "=" * 80)
        print("📊 ENHANCED PLATFORM TEST RESULTS")
        print("=" * 80)
        
        total_platforms = len(self.test_results)
        working_platforms = len([r for r in self.test_results.values() if r['status'] == 'WORKING'])
        failed_platforms = total_platforms - working_platforms
        
        print(f"Total Platforms Tested: {total_platforms}")
        print(f"Working Platforms: {working_platforms}")
        print(f"Failed Platforms: {failed_platforms}")
        print(f"Success Rate: {(working_platforms/total_platforms)*100:.1f}%")
        
        print("\\n" + "=" * 80)
        print("🔍 DETAILED RESULTS WITH CAPTCHA BYPASS")
        print("=" * 80)
        
        # Group by type
        api_platforms = {k: v for k, v in self.test_results.items() if v['type'] == 'API'}
        browser_platforms = {k: v for k, v in self.test_results.items() if v['type'] == 'Browser'}
        
        print("\\n📡 API-BASED PLATFORMS:")
        for platform, result in api_platforms.items():
            status_icon = "✅" if result['status'] == 'WORKING' else "❌"
            print(f"{status_icon} {platform}: {result['status']}")
            if result['status'] == 'WORKING':
                print(f"   └─ {result['details']}")
            else:
                print(f"   └─ Error: {result['error']}")
        
        print("\\n🌐 BROWSER-BASED PLATFORMS (With Security Bypass):")
        for platform, result in browser_platforms.items():
            status_icon = "✅" if result['status'] == 'WORKING' else "❌"
            print(f"{status_icon} {platform}: {result['status']}")
            if result['status'] == 'WORKING':
                print(f"   └─ {result['details']}")
            else:
                print(f"   └─ Error: {result['error']}")
        
        print("\\n" + "=" * 80)
        print("🎯 ENHANCED CAPABILITIES")
        print("=" * 80)
        
        print("✅ SECURITY BYPASS FEATURES:")
        print("   • Automatic CloudFlare detection and bypass")
        print("   • reCAPTCHA checkbox solving")
        print("   • hCaptcha handling")
        print("   • Anti-detection browser configuration")
        print("   • Human behavior simulation")
        print("   • Screenshot proof capture")
        
        working_count = len([r for r in self.test_results.values() if r['status'] == 'WORKING'])
        if working_count >= total_platforms * 0.7:
            print("\\n🏆 EXCELLENT SUCCESS RATE!")
            print("   • Most platforms accessible with enhanced bypass")
            print("   • CloudFlare and captcha protection overcome")
            print("   • Ready for full automation")
        
        return self.test_results

if __name__ == "__main__":
    tester = EnhancedPlatformTester()
    results = tester.run_comprehensive_enhanced_test()
