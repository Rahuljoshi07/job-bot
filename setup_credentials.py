#!/usr/bin/env python3
"""
Secure Credential Setup and Management
Helps you safely configure your job platform credentials
"""

import os
import getpass
from datetime import datetime

class CredentialManager:
    def __init__(self):
        self.env_file = ".env"
        self.platforms = {
            'personal': [
                ('PERSONAL_FULL_NAME', 'Your full name'),
                ('PERSONAL_EMAIL', 'Your email address'),
                ('PERSONAL_PHONE', 'Your phone number'),
                ('PERSONAL_LINKEDIN', 'Your LinkedIn profile URL'),
                ('PERSONAL_GITHUB', 'Your GitHub profile URL'),
                ('PERSONAL_LOCATION', 'Your location (City, Country)')
            ],
            'job_platforms': [
                ('TWITTER_EMAIL', 'Twitter/X email'),
                ('TWITTER_PASSWORD', 'Twitter/X password'),
                ('TURING_EMAIL', 'Turing email'),
                ('TURING_PASSWORD', 'Turing password'),
                ('INDEED_EMAIL', 'Indeed email'),
                ('INDEED_PASSWORD', 'Indeed password'),
                ('DICE_EMAIL', 'Dice email'),
                ('DICE_PASSWORD', 'Dice password'),
                ('LINKEDIN_EMAIL', 'LinkedIn email'),
                ('LINKEDIN_PASSWORD', 'LinkedIn password'),
                ('FLEXJOBS_EMAIL', 'FlexJobs email'),
                ('FLEXJOBS_PASSWORD', 'FlexJobs password'),
                ('WEWORKREMOTELY_EMAIL', 'WeWorkRemotely email'),
                ('WEWORKREMOTELY_PASSWORD', 'WeWorkRemotely password'),
                ('GLASSDOOR_EMAIL', 'Glassdoor email'),
                ('GLASSDOOR_PASSWORD', 'Glassdoor password')
            ],
            'preferences': [
                ('PREFERENCES_SALARY_MIN', 'Minimum salary requirement'),
                ('PREFERENCES_REMOTE_ONLY', 'Remote only (true/false)'),
                ('PREFERENCES_EXPERIENCE_LEVEL', 'Experience level (entry/mid/senior)')
            ]
        }
    
    def display_current_config(self):
        """Display current configuration (masked passwords)"""
        print("🔍 CURRENT CONFIGURATION")
        print("=" * 60)
        
        if not os.path.exists(self.env_file):
            print("❌ No .env file found")
            return
        
        with open(self.env_file, 'r') as f:
            lines = f.readlines()
        
        print("📋 Personal Information:")
        print("-" * 30)
        for line in lines:
            if line.startswith('PERSONAL_'):
                key, value = line.strip().split('=', 1)
                print(f"   {key}: {value}")
        
        print("\n🔐 Platform Credentials:")
        print("-" * 30)
        for line in lines:
            if any(platform in line for platform in ['TWITTER_', 'TURING_', 'INDEED_', 'DICE_', 'LINKEDIN_', 'FLEXJOBS_', 'WEWORKREMOTELY_', 'GLASSDOOR_']):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    if 'PASSWORD' in key:
                        print(f"   {key}: {'*' * len(value) if value else 'NOT SET'}")
                    else:
                        print(f"   {key}: {value}")
        
        print("\n⚙️ Preferences:")
        print("-" * 30)
        for line in lines:
            if line.startswith('PREFERENCES_'):
                key, value = line.strip().split('=', 1)
                print(f"   {key}: {value}")
    
    def setup_credentials_interactive(self):
        """Interactive credential setup"""
        print("🔧 INTERACTIVE CREDENTIAL SETUP")
        print("=" * 60)
        print("📝 Enter your real credentials (passwords will be hidden)")
        print("⏭️  Press Enter to skip any field")
        print()
        
        credentials = {}
        
        # Personal Information
        print("👤 PERSONAL INFORMATION")
        print("-" * 30)
        for key, description in self.platforms['personal']:
            value = input(f"{description} ({key}): ").strip()
            if value:
                credentials[key] = value
        
        # Job Platform Credentials
        print("\n🔐 JOB PLATFORM CREDENTIALS")
        print("-" * 30)
        for key, description in self.platforms['job_platforms']:
            if 'PASSWORD' in key:
                value = getpass.getpass(f"{description} ({key}): ")
            else:
                value = input(f"{description} ({key}): ").strip()
            if value:
                credentials[key] = value
        
        # Preferences
        print("\n⚙️ PREFERENCES")
        print("-" * 30)
        for key, description in self.platforms['preferences']:
            value = input(f"{description} ({key}): ").strip()
            if value:
                credentials[key] = value
        
        return credentials
    
    def backup_current_env(self):
        """Backup current .env file"""
        if os.path.exists(self.env_file):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f".env.backup_{timestamp}"
            
            with open(self.env_file, 'r') as src:
                content = src.read()
            
            with open(backup_file, 'w') as dst:
                dst.write(content)
            
            print(f"📋 Current .env backed up to: {backup_file}")
            return backup_file
        return None
    
    def update_env_file(self, credentials):
        """Update .env file with new credentials"""
        
        # Create new .env content
        env_content = [
            "# Job Bot Configuration - Real Credentials",
            f"# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "# NEVER commit this file to version control!",
            "",
            "# Personal Information"
        ]
        
        # Add personal information
        for key, description in self.platforms['personal']:
            value = credentials.get(key, '')
            env_content.append(f"{key}={value}")
        
        env_content.extend([
            "",
            "# Job Platform Credentials"
        ])
        
        # Add platform credentials
        for key, description in self.platforms['job_platforms']:
            value = credentials.get(key, '')
            env_content.append(f"{key}={value}")
        
        env_content.extend([
            "",
            "# Job Preferences"
        ])
        
        # Add preferences
        for key, description in self.platforms['preferences']:
            value = credentials.get(key, '')
            env_content.append(f"{key}={value}")
        
        # Write to file
        with open(self.env_file, 'w') as f:
            f.write('\n'.join(env_content))
        
        print(f"✅ Credentials saved to {self.env_file}")
    
    def validate_config(self):
        """Validate current configuration"""
        print("\n🔍 VALIDATING CONFIGURATION")
        print("=" * 60)
        
        try:
            from config import Config
            config_manager = Config()
            user_config = config_manager.load_config()
            
            print("✅ Configuration validation successful!")
            
            # Count configured platforms
            platforms = user_config.get('platforms', {})
            configured_count = len([p for p in platforms.values() if p.get('email') and p.get('password')])
            
            print(f"📊 Configured platforms: {configured_count}")
            print(f"📧 Personal email: {user_config.get('personal', {}).get('email', 'NOT SET')}")
            print(f"👤 Full name: {user_config.get('personal', {}).get('full_name', 'NOT SET')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            return False
    
    def show_platform_requirements(self):
        """Show what each platform requires"""
        print("📋 PLATFORM REQUIREMENTS")
        print("=" * 60)
        
        requirements = {
            "LinkedIn": "Professional profile with active login",
            "Indeed": "Basic account, no premium required", 
            "Dice": "Tech job platform account",
            "Twitter/X": "Active account for job networking",
            "Turing": "Developer platform account",
            "FlexJobs": "Flexible work platform account",
            "WeWorkRemotely": "Remote work platform account",
            "Glassdoor": "Company review platform account"
        }
        
        for platform, requirement in requirements.items():
            print(f"🔹 {platform}: {requirement}")
        
        print("\n💡 TIPS:")
        print("   • Use the same email across platforms when possible")
        print("   • Use strong, unique passwords")
        print("   • Enable 2FA where available (may require manual login)")
        print("   • Some platforms may require phone verification")
    
    def run_setup_wizard(self):
        """Run the complete setup wizard"""
        print("🚀 JOB BOT CREDENTIAL SETUP WIZARD")
        print("=" * 60)
        
        # Show current config
        print("\n1️⃣ Current Configuration:")
        self.display_current_config()
        
        # Show platform requirements
        print("\n2️⃣ Platform Requirements:")
        self.show_platform_requirements()
        
        # Ask if user wants to update
        print("\n3️⃣ Update Configuration:")
        update = input("Do you want to update your credentials? (y/n): ").lower().strip()
        
        if update == 'y':
            # Backup current
            self.backup_current_env()
            
            # Get new credentials
            credentials = self.setup_credentials_interactive()
            
            # Update file
            self.update_env_file(credentials)
            
            # Validate
            self.validate_config()
            
            print("\n✅ Setup complete!")
            print("🔐 Your credentials are now configured")
            print("🚀 Ready to run job bot automation!")
        else:
            print("⏭️ Setup skipped")

def main():
    """Main function"""
    manager = CredentialManager()
    
    print("Choose an option:")
    print("1. View current configuration")
    print("2. Run setup wizard") 
    print("3. Validate configuration")
    print("4. Show platform requirements")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        manager.display_current_config()
    elif choice == '2':
        manager.run_setup_wizard()
    elif choice == '3':
        manager.validate_config()
    elif choice == '4':
        manager.show_platform_requirements()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
