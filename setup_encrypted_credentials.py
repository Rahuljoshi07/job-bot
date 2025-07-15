#!/usr/bin/env python3
"""
🔐 Credential Management Utility for Fixed Job Bot
Secure setup and management of encrypted credentials
"""

import os
import json
import getpass
import sys
from pathlib import Path

# Add current directory to path to import fixed_job_bot
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from fixed_job_bot import FixedJobBot
except ImportError as e:
    print(f"❌ Error importing FixedJobBot: {e}")
    print("Please ensure you're running from the correct directory and dependencies are installed")
    sys.exit(1)


def setup_encrypted_credentials():
    """Interactive setup for encrypted credentials"""
    print("🔐 SECURE CREDENTIAL SETUP")
    print("=" * 50)
    
    # Get master password
    master_password = getpass.getpass("Enter master password for encryption: ")
    confirm_password = getpass.getpass("Confirm master password: ")
    
    if master_password != confirm_password:
        print("❌ Passwords don't match!")
        return False
    
    # Set environment variable for this session
    os.environ['CREDENTIALS_PASSWORD'] = master_password
    
    # Collect credentials
    print("\n📋 PERSONAL INFORMATION")
    personal = {
        'full_name': input("Full Name: "),
        'email': input("Email Address: "),
        'phone': input("Phone Number: ")
    }
    
    print("\n🔗 PLATFORM CREDENTIALS")
    platforms = {}
    
    # LinkedIn
    if input("Setup LinkedIn credentials? (y/n): ").lower() == 'y':
        platforms['linkedin'] = {
            'username': input("LinkedIn Email: "),
            'password': getpass.getpass("LinkedIn Password: ")
        }
    
    # Indeed
    if input("Setup Indeed credentials? (y/n): ").lower() == 'y':
        platforms['indeed'] = {
            'username': input("Indeed Email: "),
            'password': getpass.getpass("Indeed Password: ")
        }
    
    # Dice
    if input("Setup Dice credentials? (y/n): ").lower() == 'y':
        platforms['dice'] = {
            'username': input("Dice Email: "),
            'password': getpass.getpass("Dice Password: ")
        }
    
    # Twitter
    if input("Setup Twitter credentials? (y/n): ").lower() == 'y':
        platforms['twitter'] = {
            'username': input("Twitter Email: "),
            'password': getpass.getpass("Twitter Password: ")
        }
    
    # Turing
    if input("Setup Turing credentials? (y/n): ").lower() == 'y':
        platforms['turing'] = {
            'username': input("Turing Email: "),
            'password': getpass.getpass("Turing Password: ")
        }
    
    print("\n📧 EMAIL VERIFICATION SETUP")
    enable_verification = input("Enable email verification? (y/n): ").lower() == 'y'
    
    verification = {
        'enable_email_check': enable_verification
    }
    
    if enable_verification:
        verification.update({
            'email_app_password': getpass.getpass("Email App Password: "),
            'email_imap_server': input("IMAP Server (default: imap.gmail.com): ") or 'imap.gmail.com',
            'email_smtp_server': input("SMTP Server (default: smtp.gmail.com): ") or 'smtp.gmail.com',
            'email_smtp_port': int(input("SMTP Port (default: 587): ") or 587)
        })
    
    print("\n🔄 JOB PREFERENCES")
    preferences = {
        'job_types': input("Job Types (comma-separated): ").split(',') or ['DevOps Engineer', 'SRE'],
        'locations': input("Locations (comma-separated): ").split(',') or ['Remote'],
        'experience_level': input("Experience Level (default: Mid-level): ") or 'Mid-level',
        'apply_strategy': input("Apply Strategy (default: all_matching): ") or 'all_matching'
    }
    
    # Clean up job types and locations
    preferences['job_types'] = [job.strip() for job in preferences['job_types'] if job.strip()]
    preferences['locations'] = [loc.strip() for loc in preferences['locations'] if loc.strip()]
    
    # Build credentials dictionary
    credentials = {
        'personal': personal,
        'platforms': platforms,
        'verification': verification,
        'preferences': preferences
    }
    
    # Save encrypted credentials
    try:
        bot = FixedJobBot()
        if bot._save_encrypted_credentials(credentials, master_password):
            print("\n✅ Encrypted credentials saved successfully!")
            print("\n🔐 IMPORTANT SECURITY NOTES:")
            print("1. Store your master password securely (password manager recommended)")
            print("2. Set CREDENTIALS_PASSWORD environment variable for production")
            print("3. The .env.encrypted file is automatically added to .gitignore")
            print("4. Never share your encrypted credentials file without the password")
            
            # Save a reminder file
            with open('.credentials_reminder.txt', 'w') as f:
                f.write("🔐 CREDENTIAL SETUP COMPLETED\n")
                f.write("=" * 40 + "\n\n")
                f.write("Your encrypted credentials are stored in .env.encrypted\n")
                f.write("To use them, set the environment variable:\n")
                f.write("export CREDENTIALS_PASSWORD='your-master-password'\n\n")
                f.write("For production deployment, consider using a secrets manager.\n")
                f.write("Delete this file after reading!\n")
            
            print("\n📄 Created .credentials_reminder.txt with usage instructions")
            return True
        else:
            print("❌ Failed to save encrypted credentials")
            return False
            
    except Exception as e:
        print(f"❌ Error saving credentials: {e}")
        return False


def test_credentials():
    """Test encrypted credentials"""
    print("🧪 TESTING ENCRYPTED CREDENTIALS")
    print("=" * 50)
    
    try:
        bot = FixedJobBot()
        config = bot.config
        
        if not config:
            print("❌ No configuration loaded")
            return False
        
        print("✅ Configuration loaded successfully")
        
        # Test personal info
        personal = config.get('personal', {})
        if personal.get('full_name') and personal.get('email'):
            print(f"✅ Personal info: {personal['full_name']} ({personal['email']})")
        else:
            print("⚠️ Personal info incomplete")
        
        # Test platforms
        platforms = config.get('platforms', {})
        for platform, creds in platforms.items():
            if creds.get('username') and creds.get('password'):
                print(f"✅ {platform.capitalize()}: {creds['username']}")
            else:
                print(f"⚠️ {platform.capitalize()}: incomplete credentials")
        
        # Test verification
        verification = config.get('verification', {})
        if verification.get('enable_email_check'):
            if verification.get('email_app_password'):
                print("✅ Email verification: enabled with app password")
            else:
                print("⚠️ Email verification: enabled but no app password")
        else:
            print("ℹ️ Email verification: disabled")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing credentials: {e}")
        return False


def main():
    """Main function"""
    print("🔐 FIXED JOB BOT - CREDENTIAL MANAGER")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Setup encrypted credentials")
        print("2. Test credentials")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            setup_encrypted_credentials()
        elif choice == '2':
            test_credentials()
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()