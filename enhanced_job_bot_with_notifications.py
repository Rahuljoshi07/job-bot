#!/usr/bin/env python3
"""
Enhanced Job Bot with Visible Browser, LinkedIn/Indeed Automation, and Notifications
Features:
- Visible browser automation
- Real LinkedIn job applications
- Real Indeed job applications
- Notification system for messages and updates
- Screenshot proof system
"""

import time
import json
import requests
import random
import os
import winsound
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from browser_manager import BrowserManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from config import Config
from resume_analyzer import ResumeAnalyzer

class EnhancedJobBotWithNotifications:
    def __init__(self):
        print("🚀 Initializing Enhanced Job Bot with Notifications...")
        
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
        
        # Notification settings
        self.notification_log = "notifications_log.txt"
        # Email setup
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_email = os.getenv('SMTP_EMAIL')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.smtp_recipients = [self.user_config['personal']['email']]
        self.smtp_server_connection = None
        
    def setup_visible_browser(self):
        """Setup browser with visible window for monitoring"""
        print("🔧 Setting up VISIBLE browser for monitoring...")
        return self.browser_manager.setup_browser(headless=False)  # Non-headless = visible
    
    def play_notification_sound(self):
        """Play notification sound"""
        try:
            # Play Windows default notification sound
            winsound.MessageBeep(winsound.MB_ICONINFORMATION)
        except:
            print("🔔 NOTIFICATION: Check the application!")
    
    def send_notification(self, title, message, sound=True):
        """Send notification with sound and logging"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Log notification
        with open(self.notification_log, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} - {title}: {message}\\n")
        
        # Display notification
        print(f"\\n🔔 NOTIFICATION: {title}")
        print(f"📨 {message}")
        print(f"⏰ Time: {timestamp}")
        
        # Play sound
        if sound:
            self.play_notification_sound()
        
        # Send email
        self.send_email(title, message)
    
    def send_email(self, subject, message):
        """Send email through Gmail SMTP server"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_email
            msg['To'] = ", ".join(self.smtp_recipients)
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            
            if not self.smtp_server_connection:
                self.smtp_server_connection = smtplib.SMTP(self.smtp_server, self.smtp_port)
                self.smtp_server_connection.starttls()
                self.smtp_server_connection.login(self.smtp_email, self.smtp_password)
            
            self.smtp_server_connection.send_message(msg)
            print("📧 Email sent successfully")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
    
    def take_proof_screenshot(self, job_title, company_name, platform, action="Applied"):
        """Take screenshot as proof of application with notification"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.proof_folder}/enhanced_{platform}_{company_name}_{job_title}_{timestamp}.png"
            # Clean filename
            filename = filename.replace(" ", "_").replace("/", "_").replace("\\", "_")
            
            if self.browser_manager.take_screenshot(filename):
                # Send notification about screenshot
                self.send_notification(
                    f"Screenshot Captured",
                    f"{action} to {job_title} at {company_name} - Proof saved: {filename}",
                    sound=False
                )
                return filename
            return None
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return None
    
    def check_linkedin_notifications(self, driver):
        """Check for LinkedIn notifications and messages"""
        try:
            print("🔍 Checking LinkedIn notifications...")
            
            # Look for notification indicators
            notification_selectors = [
                ".notification-badge",
                "[data-test-id*='notification']",
                ".notifications-icon--new-notifications",
                ".global-nav__notification-badge"
            ]
            
            notifications_found = False
            for selector in notification_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        notifications_found = True
                        self.send_notification(
                            "LinkedIn Notification",
                            f"You have {len(elements)} new notifications on LinkedIn!"
                        )
                        break
                except:
                    continue
            
            # Check for messages
            message_selectors = [
                ".msg-overlay-bubble-header__badge",
                "[data-test-id*='messaging']",
                ".messaging-icon--new-messages"
            ]
            
            for selector in message_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        self.send_notification(
                            "LinkedIn Message",
                            f"You have new messages on LinkedIn!"
                        )
                        break
                except:
                    continue
                    
            return notifications_found
            
        except Exception as e:
            print(f"⚠️ Error checking LinkedIn notifications: {e}")
            return False
    
    def check_indeed_notifications(self, driver):
        """Check for Indeed notifications and messages"""
        try:
            print("🔍 Checking Indeed notifications...")
            
            # Look for notification indicators
            notification_selectors = [
                ".np-indicator",
                "[data-testid*='notification']",
                ".notification-count",
                ".alert-count"
            ]
            
            for selector in notification_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        self.send_notification(
                            "Indeed Notification",
                            f"You have new notifications on Indeed!"
                        )
                        break
                except:
                    continue
                    
            return True
            
        except Exception as e:
            print(f"⚠️ Error checking Indeed notifications: {e}")
            return False
    
    def apply_to_linkedin_jobs(self):
        """Apply to LinkedIn jobs with real automation"""
        print("🔗 Starting LinkedIn job application automation...")
        applications_sent = 0
        
        if not self.browser_manager.driver:
            if not self.setup_visible_browser():
                self.send_notification("Error", "Browser setup failed for LinkedIn")
                return applications_sent
        
        driver = self.browser_manager.driver
        
        try:
            # Navigate to LinkedIn login
            driver.get("https://www.linkedin.com/login")
            time.sleep(3)
            
            # Login with real credentials
            linkedin_email = self.user_config['platforms']['linkedin']['email']
            linkedin_password = self.user_config['platforms']['linkedin']['password']
            
            print(f"📧 Logging into LinkedIn with: {linkedin_email}")
            
            # Fill login form
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.clear()
            email_field.send_keys(linkedin_email)
            
            password_field = driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(linkedin_password)
            
            # Take screenshot before login
            self.take_proof_screenshot("LinkedIn_Login_Attempt", "LinkedIn", "LinkedIn", "Logging_in")
            
            # Submit login
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            current_url = driver.current_url
            if "challenge" in current_url or "checkpoint" in current_url:
                self.send_notification(
                    "LinkedIn Security Check",
                    "LinkedIn requires additional verification. Please complete manually and press Enter to continue."
                )
                input("Complete LinkedIn verification and press Enter to continue...")
            
            # Check for notifications first
            self.check_linkedin_notifications(driver)
            
            # Navigate to jobs
            driver.get("https://www.linkedin.com/jobs/")
            time.sleep(3)
            
            # Search for DevOps jobs
            try:
                search_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-box__text-input"))
                )
                search_box.clear()
                search_box.send_keys("DevOps Engineer")
                search_box.send_keys(Keys.RETURN)
                time.sleep(5)
                
                # Take screenshot of search results
                self.take_proof_screenshot("LinkedIn_Job_Search", "LinkedIn", "LinkedIn", "Searched")
                
                # Get job listings
                job_cards = driver.find_elements(By.CSS_SELECTOR, ".job-card-container, .jobs-search-results__list-item")
                
                self.send_notification(
                    "LinkedIn Jobs Found",
                    f"Found {len(job_cards)} job listings on LinkedIn!"
                )
                
                # Apply to first few jobs
                for i, job_card in enumerate(job_cards[:3]):  # Apply to first 3 jobs
                    try:
                        # Scroll to job card
                        driver.execute_script("arguments[0].scrollIntoView();", job_card)
                        time.sleep(2)
                        
                        # Get job details
                        try:
                            title_element = job_card.find_element(By.CSS_SELECTOR, "h3 a, .job-card-list__title a")
                            title = title_element.text.strip()
                        except:
                            title = f"LinkedIn_Job_{i+1}"
                        
                        try:
                            company_element = job_card.find_element(By.CSS_SELECTOR, ".job-card-container__company-name, h4")
                            company = company_element.text.strip()
                        except:
                            company = f"LinkedIn_Company_{i+1}"
                        
                        # Click on job
                        title_element.click()
                        time.sleep(3)
                        
                        # Take screenshot of job details
                        self.take_proof_screenshot(title, company, "LinkedIn", "Viewing")
                        
                        # Look for Easy Apply button
                        try:
                            apply_buttons = driver.find_elements(By.CSS_SELECTOR, ".jobs-apply-button, [aria-label*='Easy Apply']")
                            if apply_buttons:
                                apply_button = apply_buttons[0]
                                apply_button.click()
                                time.sleep(3)
                                
                                # Take screenshot of application
                                self.take_proof_screenshot(title, company, "LinkedIn", "Applied")
                                
                                applications_sent += 1
                                
                                # Send notification
                                self.send_notification(
                                    "LinkedIn Application Sent",
                                    f"Successfully applied to {title} at {company}!"
                                )
                                
                                # Close any application modals
                                try:
                                    close_buttons = driver.find_elements(By.CSS_SELECTOR, "[aria-label='Dismiss'], .artdeco-modal__dismiss")
                                    if close_buttons:
                                        close_buttons[0].click()
                                        time.sleep(2)
                                except:
                                    pass
                            else:
                                print(f"⚠️ No Easy Apply available for {title}")
                                
                        except Exception as e:
                            print(f"⚠️ Could not apply to {title}: {e}")
                            
                    except Exception as e:
                        print(f"❌ Error processing job card {i+1}: {e}")
                        continue
                
            except Exception as e:
                print(f"❌ LinkedIn job search failed: {e}")
            
        except Exception as e:
            print(f"❌ LinkedIn automation failed: {e}")
            self.send_notification("LinkedIn Error", f"LinkedIn automation failed: {e}")
        
        return applications_sent
    
    def apply_to_indeed_jobs(self):
        """Apply to Indeed jobs with real automation"""
        print("📋 Starting Indeed job application automation...")
        applications_sent = 0
        
        if not self.browser_manager.driver:
            if not self.setup_visible_browser():
                self.send_notification("Error", "Browser setup failed for Indeed")
                return applications_sent
        
        driver = self.browser_manager.driver
        
        try:
            # Navigate to Indeed login
            driver.get("https://secure.indeed.com/account/login")
            time.sleep(3)
            
            # Login with real credentials
            indeed_email = self.user_config['platforms']['indeed']['email']
            indeed_password = self.user_config['platforms']['indeed']['password']
            
            print(f"📧 Logging into Indeed with: {indeed_email}")
            
            # Fill login form
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "login-email-input"))
            )
            email_field.clear()
            email_field.send_keys(indeed_email)
            
            password_field = driver.find_element(By.ID, "login-password-input")
            password_field.clear()
            password_field.send_keys(indeed_password)
            
            # Take screenshot before login
            self.take_proof_screenshot("Indeed_Login_Attempt", "Indeed", "Indeed", "Logging_in")
            
            # Submit login
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            time.sleep(5)
            
            # Check for notifications
            self.check_indeed_notifications(driver)
            
            # Navigate to job search
            driver.get("https://www.indeed.com/jobs?q=DevOps+Engineer&l=Remote")
            time.sleep(3)
            
            # Take screenshot of search results
            self.take_proof_screenshot("Indeed_Job_Search", "Indeed", "Indeed", "Searched")
            
            # Get job listings
            job_cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid='job-result'], .jobsearch-SerpJobCard")
            
            self.send_notification(
                "Indeed Jobs Found", 
                f"Found {len(job_cards)} job listings on Indeed!"
            )
            
            # Apply to first few jobs
            for i, job_card in enumerate(job_cards[:3]):  # Apply to first 3 jobs
                try:
                    # Scroll to job card
                    driver.execute_script("arguments[0].scrollIntoView();", job_card)
                    time.sleep(2)
                    
                    # Get job details
                    try:
                        title_element = job_card.find_element(By.CSS_SELECTOR, "h2 a, .jobTitle a")
                        title = title_element.text.strip()
                    except:
                        title = f"Indeed_Job_{i+1}"
                    
                    try:
                        company_element = job_card.find_element(By.CSS_SELECTOR, ".companyName, [data-testid='company-name']")
                        company = company_element.text.strip()
                    except:
                        company = f"Indeed_Company_{i+1}"
                    
                    # Click on job
                    title_element.click()
                    time.sleep(3)
                    
                    # Take screenshot of job details
                    self.take_proof_screenshot(title, company, "Indeed", "Viewing")
                    
                    # Look for Apply button
                    try:
                        apply_buttons = driver.find_elements(By.CSS_SELECTOR, "[data-testid='apply-button'], .jobsearch-IndeedApplyButton")
                        if apply_buttons:
                            apply_button = apply_buttons[0]
                            apply_button.click()
                            time.sleep(3)
                            
                            # Take screenshot of application
                            self.take_proof_screenshot(title, company, "Indeed", "Applied")
                            
                            applications_sent += 1
                            
                            # Send notification
                            self.send_notification(
                                "Indeed Application Sent",
                                f"Successfully applied to {title} at {company}!"
                            )
                        else:
                            print(f"⚠️ No direct apply available for {title}")
                            
                    except Exception as e:
                        print(f"⚠️ Could not apply to {title}: {e}")
                        
                except Exception as e:
                    print(f"❌ Error processing job card {i+1}: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ Indeed automation failed: {e}")
            self.send_notification("Indeed Error", f"Indeed automation failed: {e}")
        
        return applications_sent
    
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
                if jobs:
                    self.send_notification(
                        "RemoteOK Jobs Found",
                        f"Found {len(jobs)} matching DevOps/Cloud jobs!",
                        sound=False
                    )
            else:
                print(f"⚠️ RemoteOK API returned status {response.status_code}")
                
        except Exception as e:
            print(f"❌ RemoteOK API error: {e}")
        
        return jobs
    
    def run_enhanced_job_cycle(self):
        """Run complete enhanced job application cycle"""
        print("\\n🚀 STARTING ENHANCED JOB APPLICATION CYCLE WITH NOTIFICATIONS")
        print("=" * 80)
        print(f"Started at: {datetime.now()}")
        print("Browser will be VISIBLE for monitoring")
        print("=" * 80)
        
        # Send start notification
        self.send_notification(
            "Job Bot Started",
            "Enhanced job application cycle has begun!"
        )
        
        total_applications = 0
        
        # 1. Search RemoteOK API
        print("\\n📡 PHASE 1: RemoteOK API Jobs")
        remoteok_jobs = self.search_remoteok_api()
        
        # 2. LinkedIn job applications with visible browser
        print("\\n🔗 PHASE 2: LinkedIn Job Applications (REAL)")
        linkedin_apps = self.apply_to_linkedin_jobs()
        total_applications += linkedin_apps
        
        # Wait between platforms
        time.sleep(3)
        
        # 3. Indeed job applications with visible browser
        print("\\n📋 PHASE 3: Indeed Job Applications (REAL)")
        indeed_apps = self.apply_to_indeed_jobs()
        total_applications += indeed_apps
        
        # Summary
        print("\\n" + "=" * 80)
        print("📊 ENHANCED CYCLE SUMMARY")
        print("=" * 80)
        print(f"LinkedIn applications: {linkedin_apps}")
        print(f"Indeed applications: {indeed_apps}")
        print(f"RemoteOK jobs found: {len(remoteok_jobs)}")
        print(f"Total applications sent: {total_applications}")
        print(f"Completed at: {datetime.now()}")
        
        # Final notification
        self.send_notification(
            "Job Bot Completed",
            f"Cycle complete! {total_applications} applications sent across LinkedIn and Indeed!"
        )
        
        # Keep browser open for manual review
        if self.browser_manager.driver:
            input("\\n👀 Review the results in the browser, then press Enter to close...")
            self.browser_manager.quit()
        
        return total_applications

def main():
    """Main function"""
    print("🤖 ENHANCED JOB BOT WITH VISIBLE BROWSER & NOTIFICATIONS")
    print("Features:")
    print("✅ Visible browser automation")
    print("✅ Real LinkedIn job applications")  
    print("✅ Real Indeed job applications")
    print("✅ Notification system for messages")
    print("✅ Screenshot proof system")
    print("=" * 80)
    
    bot = EnhancedJobBotWithNotifications()
    
    try:
        applications_sent = bot.run_enhanced_job_cycle()
        print(f"\\n🎯 Enhanced mission completed! {applications_sent} real applications processed.")
        
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
