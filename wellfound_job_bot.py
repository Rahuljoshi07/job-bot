import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config import Config
from resume_analyzer import ResumeAnalyzer

class WellfoundJobBot:
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

    def login_wellfound(self):
        """Login to Wellfound (AngelList)"""
        try:
            self.driver.get('https://wellfound.com/login')
            email = self.user_config['platforms']['wellfound']['email']
            password = self.user_config['platforms']['wellfound']['password']

            email_field = self.driver.find_element(By.NAME, 'user[email]')
            password_field = self.driver.find_element(By.NAME, 'user[password]')

            email_field.send_keys(email)
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
            time.sleep(3)

            print("Logged into Wellfound")
            self.driver.save_screenshot('wellfound_login.png')
        except Exception as e:
            print(f"Error logging into Wellfound: {e}")

    def apply_to_job(self, job_title, company_name):
        """Apply to a job with resume and cover letter"""
        try:
            # Assume we have the job URL already
            job_url = f'https://wellfound.com/job/{job_title}'
            self.driver.get(job_url)
            time.sleep(2)

            # Find "Apply" button and click
            apply_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Apply')]" )
            apply_button.click()
            time.sleep(2)

            # Find the cover letter field and fill in
            cover_letter_template = open('cover_letter.txt').read()
            cover_letter_text = cover_letter_template.format(job_title=job_title, company_name=company_name)

            cover_letter_field = self.driver.find_element(By.NAME, 'cover_letter')
            cover_letter_field.send_keys(cover_letter_text)

            # Attach resume if necessary
            attach_resume = self.driver.find_element(By.NAME, 'resume_upload')
            attach_resume.send_keys(os.path.abspath('resume.pdf'))

            # Submit application
            submit_button = self.driver.find_element(By.NAME, 'commit')
            submit_button.click()
            time.sleep(2)

            # Screenshot as proof of application
            self.driver.save_screenshot(f'application_proof_{job_title}.png')
            print(f"Applied to {job_title} at {company_name} on Wellfound")

        except Exception as e:
            print(f"Error applying to job on Wellfound: {e}")

    def run(self):
        self.setup_browser()
        self.login_wellfound()

        # Example job application
        self.apply_to_job('devops-engineer', 'Example Corp')

        self.driver.quit()

if __name__ == "__main__":
    bot = WellfoundJobBot()
    bot.run()
