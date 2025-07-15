import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    def __init__(self):
        self.resume_path = "resume.pdf"
        
    def load_config(self):
        """Load configuration from environment variables"""
        # Check if running in GitHub Actions (environment variables are set differently)
        if os.getenv('GITHUB_ACTIONS') == 'true':
            print("🔧 Loading configuration from GitHub Secrets...")
        else:
            print("🔧 Loading configuration from environment variables...")
        
        config = {
            'personal': {
                'full_name': os.getenv('PERSONAL_FULL_NAME'),
                'email': os.getenv('PERSONAL_EMAIL'),
                'phone': os.getenv('PERSONAL_PHONE'),
                'linkedin': os.getenv('PERSONAL_LINKEDIN', ''),
                'github': os.getenv('PERSONAL_GITHUB', ''),
                'location': os.getenv('PERSONAL_LOCATION')
            },
            'platforms': {
                'twitter': {
                    'email': os.getenv('TWITTER_EMAIL'),
                    'password': os.getenv('TWITTER_PASSWORD')
                },
                'turing': {
                    'email': os.getenv('TURING_EMAIL'),
                    'password': os.getenv('TURING_PASSWORD')
                },
                'indeed': {
                    'email': os.getenv('INDEED_EMAIL'),
                    'password': os.getenv('INDEED_PASSWORD')
                },
                'dice': {
                    'email': os.getenv('DICE_EMAIL'),
                    'password': os.getenv('DICE_PASSWORD')
                },
                'flexjobs': {
                    'email': os.getenv('FLEXJOBS_EMAIL'),
                    'password': os.getenv('FLEXJOBS_PASSWORD')
                },
                'weworkremotely': {
                    'email': os.getenv('WEWORKREMOTELY_EMAIL'),
                    'password': os.getenv('WEWORKREMOTELY_PASSWORD')
                }
            },
            'preferences': {
                'job_titles': [
                    "DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer (SRE)",
                    "Infrastructure Engineer", "Platform Engineer", "AWS Engineer",
                    "Kubernetes Administrator", "CI/CD Engineer", "Linux Systems Engineer",
                    "Cloud Automation Engineer", "Junior DevOps Associate", "Remote DevOps Intern"
                ],
                'skills': ["DevOps", "AWS", "Docker", "Kubernetes", "Python", "Linux", "CI/CD", "Jenkins", "Terraform"],
                'salary_min': os.getenv('PREFERENCES_SALARY_MIN', ''),
                'remote_only': os.getenv('PREFERENCES_REMOTE_ONLY', 'true').lower() == 'true',
                'experience_level': os.getenv('PREFERENCES_EXPERIENCE_LEVEL', 'entry')
            },
            'email_verification': {
                'enabled': os.getenv('EMAIL_VERIFICATION_ENABLED', 'true').lower() == 'true',
                'imap_server': os.getenv('EMAIL_IMAP_SERVER', 'imap.gmail.com'),
                'imap_port': int(os.getenv('EMAIL_IMAP_PORT', '993')),
                'smtp_server': os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
                'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', '587')),
                'email': os.getenv('PERSONAL_EMAIL'),
                'app_password': os.getenv('EMAIL_APP_PASSWORD'),
                'timeout': int(os.getenv('EMAIL_VERIFICATION_TIMEOUT', '300')),
                'check_interval': int(os.getenv('EMAIL_CHECK_INTERVAL', '30'))
            }
        }
        
        # Validate that required environment variables are set
        required_vars = [
            'PERSONAL_FULL_NAME', 'PERSONAL_EMAIL', 'PERSONAL_PHONE', 'PERSONAL_LOCATION',
            'TWITTER_EMAIL', 'TWITTER_PASSWORD',
            'TURING_EMAIL', 'TURING_PASSWORD',
            'INDEED_EMAIL', 'INDEED_PASSWORD',
            'DICE_EMAIL', 'DICE_PASSWORD'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            print("\n🔧 Please ensure all required environment variables are set.")
            print("For local development, create a .env file based on .env.example")
            print("For GitHub Actions, set the secrets in your repository settings.")
            
            # In GitHub Actions, continue with partial config rather than failing
            if os.getenv('GITHUB_ACTIONS') == 'true':
                print("⚠️  Running in GitHub Actions with missing vars - using defaults")
                # Set default values for missing vars
                for var in missing_vars:
                    if 'EMAIL' in var:
                        os.environ[var] = 'default@example.com'
                    elif 'PASSWORD' in var:
                        os.environ[var] = 'default_password'
                    elif 'PERSONAL_FULL_NAME' in var:
                        os.environ[var] = 'Rahul Joshi'
                    elif 'PERSONAL_PHONE' in var:
                        os.environ[var] = '+1234567890'
                    elif 'PERSONAL_LOCATION' in var:
                        os.environ[var] = 'Remote'
                    elif 'LINKEDIN' in var:
                        os.environ[var] = 'https://linkedin.com/in/rahul'
                    elif 'GITHUB' in var:
                        os.environ[var] = 'https://github.com/rahuljoshi'
                print("✅ Default values set for missing variables")
                
                # Reload configuration after setting defaults
                config = {
                    'personal': {
                        'full_name': os.getenv('PERSONAL_FULL_NAME'),
                        'email': os.getenv('PERSONAL_EMAIL'),
                        'phone': os.getenv('PERSONAL_PHONE'),
                        'linkedin': os.getenv('PERSONAL_LINKEDIN', ''),
                        'github': os.getenv('PERSONAL_GITHUB', ''),
                        'location': os.getenv('PERSONAL_LOCATION')
                    },
                    'platforms': {
                        'twitter': {
                            'email': os.getenv('TWITTER_EMAIL'),
                            'password': os.getenv('TWITTER_PASSWORD')
                        },
                        'turing': {
                            'email': os.getenv('TURING_EMAIL'),
                            'password': os.getenv('TURING_PASSWORD')
                        },
                        'indeed': {
                            'email': os.getenv('INDEED_EMAIL'),
                            'password': os.getenv('INDEED_PASSWORD')
                        },
                        'dice': {
                            'email': os.getenv('DICE_EMAIL'),
                            'password': os.getenv('DICE_PASSWORD')
                        },
                        'flexjobs': {
                            'email': os.getenv('FLEXJOBS_EMAIL'),
                            'password': os.getenv('FLEXJOBS_PASSWORD')
                        },
                        'weworkremotely': {
                            'email': os.getenv('WEWORKREMOTELY_EMAIL'),
                            'password': os.getenv('WEWORKREMOTELY_PASSWORD')
                        }
                    },
                    'preferences': {
                        'job_titles': [
                            "DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer (SRE)",
                            "Infrastructure Engineer", "Platform Engineer", "AWS Engineer",
                            "Kubernetes Administrator", "CI/CD Engineer", "Linux Systems Engineer",
                            "Cloud Automation Engineer", "Junior DevOps Associate", "Remote DevOps Intern"
                        ],
                        'skills': ["DevOps", "AWS", "Docker", "Kubernetes", "Python", "Linux", "CI/CD", "Jenkins", "Terraform"],
                        'salary_min': os.getenv('PREFERENCES_SALARY_MIN', ''),
                        'remote_only': os.getenv('PREFERENCES_REMOTE_ONLY', 'true').lower() == 'true',
                        'experience_level': os.getenv('PREFERENCES_EXPERIENCE_LEVEL', 'entry')
                    },
                    'email_verification': {
                        'enabled': os.getenv('EMAIL_VERIFICATION_ENABLED', 'true').lower() == 'true',
                        'imap_server': os.getenv('EMAIL_IMAP_SERVER', 'imap.gmail.com'),
                        'imap_port': int(os.getenv('EMAIL_IMAP_PORT', '993')),
                        'smtp_server': os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
                        'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', '587')),
                        'email': os.getenv('PERSONAL_EMAIL'),
                        'app_password': os.getenv('EMAIL_APP_PASSWORD'),
                        'timeout': int(os.getenv('EMAIL_VERIFICATION_TIMEOUT', '300')),
                        'check_interval': int(os.getenv('EMAIL_CHECK_INTERVAL', '30'))
                    }
                }
            else:
                raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        print("✅ Configuration loaded successfully!")
        return config
    
    def create_user_config_from_env(self):
        """Create user_config.json from environment variables (for compatibility with existing bots)"""
        config = self.load_config()
        
        # Create user_config.json for backward compatibility
        with open('user_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ user_config.json created from environment variables for bot compatibility")
        return config
    
    def update_resume_path(self, new_path):
        """Update resume file path"""
        if os.path.exists(new_path):
            # Copy resume to bot directory
            import shutil
            shutil.copy2(new_path, self.resume_path)
            print(f"✅ Resume copied to {self.resume_path}")
            return True
        else:
            print(f"❌ Resume file not found: {new_path}")
            return False
