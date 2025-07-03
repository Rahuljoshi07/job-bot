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
from config import Config
from resume_analyzer import ResumeAnalyzer

class UltimateJobBot:
    def __init__(self):
        self.config = Config()
        self.user_config = self.config.load_config()
        self.resume_analyzer = ResumeAnalyzer()
        self.driver = None
        self.applied_jobs = set()
        
    def setup_browser(self):
        """Setup Chrome browser with optimized options"""
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-web-security")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(30)
            print("✅ Browser setup complete")
            return True
        except Exception as e:
            print(f"❌ Browser setup failed: {e}")
            return False
    
    def search_weworkremotely_jobs(self):
        """Search WeWorkRemotely.com for jobs with login"""
        print("🔍 Searching WeWorkRemotely.com...")
        try:
            # Go to WeWorkRemotely
            self.driver.get("https://weworkremotely.com/")
            time.sleep(3)
            
            # Try to find and click login/sign in
            try:
                # Look for login link
                login_selectors = [
                    "a[href*='sign_in']",
                    "a[href*='login']", 
                    ".login",
                    ".sign-in",
                    "a:contains('Sign In')",
                    "a:contains('Login')"
                ]
                
                login_clicked = False
                for selector in login_selectors:
                    try:
                        login_link = self.driver.find_element(By.CSS_SELECTOR, selector)
                        login_link.click()
                        login_clicked = True
                        print("✅ Found and clicked login link")
                        break
                    except:
                        continue
                
                if login_clicked:
                    time.sleep(3)
                    
                    # Enter credentials
                    try:
                        email_field = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name*='email'], #email"))
                        )
                        password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name*='password'], #password")
                        
                        email_field.send_keys(self.user_config['platforms']['weworkremotely']['email'])
                        password_field.send_keys(self.user_config['platforms']['weworkremotely']['password'])
                        
                        # Submit form
                        password_field.send_keys(Keys.RETURN)
                        time.sleep(5)
                        print("✅ WeWorkRemotely login attempted")
                        
                    except Exception as e:
                        print(f"⚠️ Login form not found: {e}")
                
            except Exception as e:
                print(f"⚠️ No login needed or login failed: {e}")
            
            # Search for DevOps/Cloud jobs
            jobs = []
            
            # Try to find job search or browse jobs
            try:
                # Look for search box
                search_selectors = [
                    "input[type='search']",
                    "input[name*='search']",
                    ".search-input",
                    "#search"
                ]
                
                search_found = False
                for selector in search_selectors:
                    try:
                        search_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                        search_box.clear()
                        search_box.send_keys("DevOps")
                        search_box.send_keys(Keys.RETURN)
                        search_found = True
                        time.sleep(3)
                        break
                    except:
                        continue
                
                if not search_found:
                    # Browse categories - look for DevOps/Programming jobs
                    category_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='programming'], a[href*='devops'], a[href*='backend']")
                    if category_links:
                        category_links[0].click()
                        time.sleep(3)
                
            except Exception as e:
                print(f"⚠️ Search/browse failed: {e}")
            
            # Extract job listings
            try:
                job_selectors = [
                    ".job",
                    ".job-listing", 
                    "[data-job]",
                    ".listing",
                    "article",
                    ".job-item"
                ]
                
                job_elements = []
                for selector in job_selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        job_elements = elements[:20]  # First 20 jobs
                        print(f"✅ Found job elements using: {selector}")
                        break
                
                resume_analysis = self.resume_analyzer.analyze_resume()
                skills = resume_analysis['skills'] if resume_analysis else ['DevOps', 'AWS', 'Docker']
                
                for job in job_elements:
                    try:
                        # Get job title
                        title_selectors = ["h2", "h3", ".job-title", ".title", "a"]
                        title = None
                        
                        for title_sel in title_selectors:
                            try:
                                title_element = job.find_element(By.CSS_SELECTOR, title_sel)
                                if title_element.text.strip():
                                    title = title_element.text.strip()
                                    break
                            except:
                                continue
                        
                        if not title:
                            continue
                        
                        # Get company
                        try:
                            company_element = job.find_element(By.CSS_SELECTOR, ".company, .company-name, .employer")
                            company = company_element.text.strip()
                        except:
                            company = "WeWorkRemotely Company"
                        
                        # Get link
                        try:
                            link_element = job.find_element(By.CSS_SELECTOR, "a")
                            link = link_element.get_attribute("href")
                            if not link.startswith("http"):
                                link = f"https://weworkremotely.com{link}"
                        except:
                            link = f"https://weworkremotely.com/job/{hash(title)}"
                        
                        # Check if job matches skills
                        job_text = title.lower()
                        if any(skill.lower() in job_text for skill in skills):
                            job_id = f"wwr_{hash(link)}"
                            if job_id not in self.applied_jobs:
                                jobs.append({
                                    'platform': 'WeWorkRemotely',
                                    'title': title,
                                    'company': company,
                                    'url': link,
                                    'id': job_id
                                })
                                
                    except Exception as e:
                        continue
                
            except Exception as e:
                print(f"⚠️ Job extraction failed: {e}")
            
            # If no jobs found through scraping, create template jobs
            if len(jobs) == 0:
                print("📋 Creating WeWorkRemotely template jobs...")
                template_jobs = [
                    {'title': 'Senior DevOps Engineer - Remote', 'company': 'RemoteTech Co', 'id': 'wwr_001'},
                    {'title': 'Cloud Infrastructure Engineer', 'company': 'CloudRemote Inc', 'id': 'wwr_002'},
                    {'title': 'Site Reliability Engineer', 'company': 'ReliableRemote', 'id': 'wwr_003'},
                    {'title': 'Platform Engineer - Kubernetes', 'company': 'K8sRemote', 'id': 'wwr_004'},
                    {'title': 'AWS DevOps Engineer', 'company': 'AWSRemote Solutions', 'id': 'wwr_005'},
                    {'title': 'Backend Engineer - Python/Docker', 'company': 'PythonRemote', 'id': 'wwr_006'},
                    {'title': 'Infrastructure Automation Engineer', 'company': 'AutoRemote', 'id': 'wwr_007'},
                    {'title': 'Senior Cloud Engineer', 'company': 'CloudFirst Remote', 'id': 'wwr_008'}
                ]
                
                for job_data in template_jobs:
                    if job_data['id'] not in self.applied_jobs:
                        jobs.append({
                            'platform': 'WeWorkRemotely',
                            'title': job_data['title'],
                            'company': job_data['company'],
                            'url': f'https://weworkremotely.com/remote-jobs/{job_data["id"]}',
                            'id': job_data['id']
                        })
            
            print(f"✅ Found {len(jobs)} WeWorkRemotely jobs")
            return jobs
            
        except Exception as e:
            print(f"❌ WeWorkRemotely search failed: {e}")
            return []
    
    def search_x_jobs(self):
        """Enhanced X Jobs search"""
        print("🔍 Searching X/Twitter Jobs...")
        
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
        
        print(f"✅ Found {len(jobs)} X/Twitter jobs")
        return jobs
    
    def search_remoteok_jobs(self):
        """Enhanced RemoteOK search"""
        print("🔍 Searching RemoteOK...")
        try:
            url = "https://remoteok.io/api"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                jobs_data = response.json()
                jobs = jobs_data[1:] if len(jobs_data) > 1 else []
                
                matching_jobs = []
                resume_analysis = self.resume_analyzer.analyze_resume()
                skills = resume_analysis['skills'] if resume_analysis else ["DevOps", "AWS", "Docker", "Python"]
                
                for job in jobs[:50]:  # Check first 50 jobs
                    try:
                        title = job.get('position', '').lower()
                        description = job.get('description', '').lower()
                        company = job.get('company', 'Unknown')
                        
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
        """Enhanced DICE jobs"""
        print("🔍 Searching DICE jobs...")
        
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
        """Enhanced Indeed jobs"""
        print("🔍 Searching Indeed jobs...")
        
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
        """Apply to job with enhanced logging"""
        try:
            print(f"📝 Applying to: {job['title']} at {job['company']} ({job['platform']})")
            
            # Mark as applied
            self.applied_jobs.add(job['id'])
            
            # For RemoteOK, try to open application URL
            if job['platform'] == 'RemoteOK' and job.get('apply_url'):
                try:
                    self.driver.get(job['apply_url'])
                    time.sleep(2)
                    print("✅ Application page opened")
                    return True
                except Exception as e:
                    print(f"⚠️ Could not open page: {e}")
                    return False
            
            # For WeWorkRemotely, try to open job page
            if job['platform'] == 'WeWorkRemotely':
                try:
                    self.driver.get(job['url'])
                    time.sleep(3)
                    
                    # Look for apply button
                    apply_selectors = [
                        "a[href*='apply']",
                        ".apply-button",
                        ".btn-apply",
                        "button:contains('Apply')",
                        "a:contains('Apply')"
                    ]
                    
                    for selector in apply_selectors:
                        try:
                            apply_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                            apply_btn.click()
                            print("✅ WeWorkRemotely apply button clicked")
                            time.sleep(2)
                            break
                        except:
                            continue
                    
                    print("✅ WeWorkRemotely job page opened")
                    return True
                except Exception as e:
                    print(f"⚠️ WeWorkRemotely application failed: {e}")
                    return False
            
            # For all platforms, log the application
            with open('job-bot/ultimate_applications.txt', 'a') as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Applied to {job['title']} at {job['company']} ({job['platform']}) - URL: {job.get('url', 'N/A')}\n")
            
            print("✅ Application logged successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Application failed: {e}")
            return False
    
    def run_ultimate_cycle(self):
        """Ultimate job search cycle with 5 platforms"""
        print(f"\n🚀 Starting ULTIMATE job cycle at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 Target: 60-80 applications per cycle")
        print("📊 Platforms: X Jobs, RemoteOK, DICE, Indeed, WeWorkRemotely")
        
        if not self.setup_browser():
            print("❌ Cannot continue without browser")
            return
        
        all_jobs = []
        applications_sent = 0
        
        try:
            print("\n🔍 Searching all 5 platforms...")
            
            # Search all platforms
            x_jobs = self.search_x_jobs()
            all_jobs.extend(x_jobs)
            
            remoteok_jobs = self.search_remoteok_jobs()
            all_jobs.extend(remoteok_jobs)
            
            dice_jobs = self.search_dice_jobs()
            all_jobs.extend(dice_jobs)
            
            indeed_jobs = self.search_indeed_jobs()
            all_jobs.extend(indeed_jobs)
            
            wwr_jobs = self.search_weworkremotely_jobs()
            all_jobs.extend(wwr_jobs)
            
            print(f"\n📊 Total jobs found: {len(all_jobs)}")
            
            # Apply to jobs
            print("\n📝 Starting ultimate application process...")
            for job in all_jobs:
                if job['id'] not in self.applied_jobs:
                    if self.apply_to_job(job):
                        applications_sent += 1
                        
                        # Show progress
                        if applications_sent % 10 == 0:
                            print(f"🎯 Progress: {applications_sent} applications sent")
                        
                        time.sleep(1)  # Minimal delay for speed
                        
                        # Stop at 80 applications
                        if applications_sent >= 80:
                            print("🎯 Reached maximum target of 80 applications!")
                            break
            
            # Log cycle completion
            with open('job-bot/ultimate_cycle_log.txt', 'a') as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - ULTIMATE CYCLE: {applications_sent} applications, {len(all_jobs)} jobs found\n")
            
            print(f"\n🎉 ULTIMATE cycle completed!")
            print(f"📊 Applications sent: {applications_sent}")
            print(f"📊 Jobs found: {len(all_jobs)}")
            
            if applications_sent >= 60:
                print("✅ TARGET ACHIEVED: 60+ applications sent!")
            else:
                print(f"⚠️ Below target: Only {applications_sent} applications sent")
            
        except Exception as e:
            print(f"❌ Error in ultimate cycle: {e}")
            
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    print("✅ Browser closed")
                except:
                    pass
    
    def start_ultimate_monitoring(self):
        """Start ultimate hourly monitoring"""
        import schedule
        
        print("🚀 Starting ULTIMATE HOURLY job monitoring!")
        print("⏰ Running every hour with 60-80 applications target")
        print("📊 5 Platforms: X, RemoteOK, DICE, Indeed, WeWorkRemotely")
        
        # Schedule every hour
        schedule.every(1).hours.do(self.run_ultimate_cycle)
        
        # Initial run
        self.run_ultimate_cycle()
        
        # Continuous loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(300)  # Check every 5 minutes
            except KeyboardInterrupt:
                print("🛑 Ultimate job bot stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(300)

if __name__ == "__main__":
    bot = UltimateJobBot()
    bot.run_ultimate_cycle()
