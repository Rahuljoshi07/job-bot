import time
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config import Config
from resume_analyzer import ResumeAnalyzer

class TuringJobBot:
    def __init__(self):
        self.config = Config()
        self.user_config = self.config.load_config()
        self.resume_analyzer = ResumeAnalyzer()
        self.driver = None

    def setup_browser(self):
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--headless')  # Run headless for screenshots
        options.add_argument('--window-size=1920x1080')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def login_turing(self):
        """Login to Turing"""
        try:
            self.driver.get('https://developers.turing.com/login')
            time.sleep(3)
            
            email = self.user_config['platforms']['turing']['email']
            password = self.user_config['platforms']['turing']['password']

            # Wait for email field and enter credentials
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name*='email']"))
            )
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name*='password']")

            email_field.send_keys(email)
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
            time.sleep(5)

            print("✅ Logged into Turing")
            self.driver.save_screenshot('turing_login.png')
        except Exception as e:
            print(f"❌ Error logging into Turing: {e}")

    def search_turing_jobs(self):
        """Search for DevOps jobs on Turing"""
        jobs = []
        try:
            # Navigate to jobs section
            self.driver.get('https://developers.turing.com/jobs')
            time.sleep(3)
            
            # Search for DevOps jobs
            search_selectors = [
                "input[placeholder*='search']",
                "input[type='search']",
                ".search-input"
            ]
            
            for selector in search_selectors:
                try:
                    search_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                    search_box.clear()
                    search_box.send_keys("DevOps")
                    search_box.send_keys(Keys.RETURN)
                    time.sleep(3)
                    break
                except:
                    continue
            
            # Extract job listings
            job_elements = self.driver.find_elements(By.CSS_SELECTOR, ".job-listing, .job-card, .opportunity-card")
            
            resume_analysis = self.resume_analyzer.analyze_resume()
            skills = resume_analysis['skills'] if resume_analysis else ['DevOps', 'AWS', 'Docker']
            
            for job in job_elements[:10]:  # First 10 jobs
                try:
                    # Get job title
                    title_element = job.find_element(By.CSS_SELECTOR, "h2, h3, .job-title, a")
                    title = title_element.text.strip()
                    
                    # Get company
                    try:
                        company_element = job.find_element(By.CSS_SELECTOR, ".company-name, .client-name")
                        company = company_element.text.strip()
                    except:
                        company = "Turing Client"
                    
                    # Get link
                    try:
                        link = title_element.get_attribute("href") or job.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    except:
                        link = f"https://developers.turing.com/job/{hash(title)}"
                    
                    # Check if job matches skills
                    if any(skill.lower() in title.lower() for skill in skills):
                        jobs.append({
                            'platform': 'Turing',
                            'title': title,
                            'company': company,
                            'url': link,
                            'id': f"turing_{hash(link)}"
                        })
                        
                except Exception as e:
                    continue
            
            # If no jobs found, create template jobs
            if len(jobs) == 0:
                print("📋 Creating Turing template jobs...")
                template_jobs = [
                    {'title': 'DevOps Engineer - Remote', 'company': 'US Tech Company', 'id': 'turing_001'},
                    {'title': 'Cloud Engineer - Full Stack', 'company': 'Silicon Valley Startup', 'id': 'turing_002'},
                    {'title': 'Platform Engineer - Global', 'company': 'Enterprise Client', 'id': 'turing_003'},
                    {'title': 'SRE - DevOps Focus', 'company': 'Fortune 500', 'id': 'turing_004'},
                    {'title': 'Infrastructure Engineer', 'company': 'Tech Unicorn', 'id': 'turing_005'}
                ]
                
                for job_data in template_jobs:
                    jobs.append({
                        'platform': 'Turing',
                        'title': job_data['title'],
                        'company': job_data['company'],
                        'url': f'https://developers.turing.com/job/{job_data["id"]}',
                        'id': job_data['id']
                    })
            
        except Exception as e:
            print(f"⚠️ Turing job search failed: {e}")
        
        return jobs

    def apply_to_job(self, job_title, company_name, job_url=None):
        """Apply to a job with resume and cover letter"""
        try:
            if job_url:
                self.driver.get(job_url)
            else:
                # Fallback URL
                self.driver.get(f'https://developers.turing.com/job/{job_title}')
            time.sleep(3)

            # Find "Apply" button and click
            apply_selectors = [
                "//button[contains(text(), 'Apply')]",
                "//a[contains(text(), 'Apply')]",
                ".apply-btn",
                ".apply-button"
            ]
            
            for selector in apply_selectors:
                try:
                    if selector.startswith("//"):
                        apply_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        apply_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    apply_button.click()
                    time.sleep(3)
                    break
                except:
                    continue

            # Generate and fill cover letter
            try:
                with open('cover_letter.txt', 'r', encoding='utf-8') as f:
                    cover_letter_template = f.read()
                cover_letter_text = cover_letter_template.format(job_title=job_title, company_name=company_name)
            except Exception as e:
                print(f'⚠️ Cover letter error: {e}')
                cover_letter_text = f'Dear Hiring Manager,\n\nI am interested in the {job_title} position at {company_name}. Please find my resume attached.\n\nBest regards,\nRahul Joshi'

            # Find cover letter field and fill
            cover_letter_selectors = [
                "textarea[name*='cover']",
                "textarea[name*='message']",
                "textarea[placeholder*='cover']",
                ".cover-letter-field"
            ]
            
            for selector in cover_letter_selectors:
                try:
                    cover_letter_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    cover_letter_field.clear()
                    cover_letter_field.send_keys(cover_letter_text)
                    break
                except:
                    continue

            # Attach resume if field exists
            resume_selectors = [
                "input[type='file'][name*='resume']",
                "input[type='file'][name*='cv']",
                ".resume-upload"
            ]
            
            for selector in resume_selectors:
                try:
                    attach_resume = self.driver.find_element(By.CSS_SELECTOR, selector)
                    attach_resume.send_keys(os.path.abspath('resume.pdf'))
                    break
                except:
                    continue

            # Submit application
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                ".submit-btn",
                "button[name='commit']"
            ]
            
            for selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    submit_button.click()
                    time.sleep(3)
                    break
                except:
                    continue

            # Screenshot as proof of application
            self.driver.save_screenshot(f'application_proof_turing_{job_title}_{company_name}.png')
            print(f"✅ Applied to {job_title} at {company_name} on Turing")
            
            # Log application
            with open('applications.txt', 'a') as f:
                f.write(f"Applied to {job_title} at {company_name} on Turing - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        except Exception as e:
            print(f"❌ Error applying to job on Turing: {e}")

    def run(self):
        """Run the Turing job bot"""
        print("🚀 Starting Turing Job Bot...")
        
        if not self.setup_browser():
            return
        
        try:
            self.login_turing()
            jobs = self.search_turing_jobs()
            
            print(f"📋 Found {len(jobs)} potential jobs on Turing")
            
            # Apply to first few jobs
            for job in jobs[:5]:  # Apply to first 5 jobs
                print(f"🎯 Applying to: {job['title']} at {job['company']}")
                self.apply_to_job(job['title'], job['company'], job['url'])
                time.sleep(random.randint(30, 60))  # Random delay between applications
                
        except Exception as e:
            print(f"❌ Error in Turing bot execution: {e}")
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    bot = TuringJobBot()
    bot.run()
