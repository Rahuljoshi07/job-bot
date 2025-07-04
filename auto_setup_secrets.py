#!/usr/bin/env python3
"""
Automated GitHub Secrets Setup
This script automatically sets up all GitHub Secrets from your credentials template
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def check_github_cli():
    """Check if GitHub CLI is installed"""
    try:
        result = subprocess.run(['gh', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ GitHub CLI found:", result.stdout.strip().split('\n')[0])
            return True
        else:
            return False
    except Exception:
        return False

def check_github_auth():
    """Check if user is authenticated with GitHub CLI"""
    try:
        result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ GitHub CLI authenticated")
            return True
        else:
            print("❌ GitHub CLI not authenticated")
            return False
    except Exception:
        return False

def set_github_secret(name, value):
    """Set a single GitHub secret"""
    try:
        # Escape special characters
        escaped_value = value.replace('"', '\\"').replace('$', '\\$')
        
        result = subprocess.run([
            'gh', 'secret', 'set', name, 
            '--body', value
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ Set secret: {name}")
            return True
        else:
            print(f"❌ Failed to set secret {name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error setting secret {name}: {e}")
        return False

def setup_all_secrets():
    """Set up all GitHub secrets from credentials template"""
    
    # Load credentials
    load_dotenv("credentials_template.env")
    
    secrets = {
        # Personal Information
        "PERSONAL_FULL_NAME": os.getenv("PERSONAL_FULL_NAME"),
        "PERSONAL_EMAIL": os.getenv("PERSONAL_EMAIL"),
        "PERSONAL_PHONE": os.getenv("PERSONAL_PHONE"),
        "PERSONAL_LINKEDIN": os.getenv("PERSONAL_LINKEDIN"),
        "PERSONAL_GITHUB": os.getenv("PERSONAL_GITHUB"),
        "PERSONAL_LOCATION": os.getenv("PERSONAL_LOCATION"),
        
        # Platform Credentials
        "TWITTER_EMAIL": os.getenv("TWITTER_EMAIL"),
        "TWITTER_PASSWORD": os.getenv("TWITTER_PASSWORD"),
        "TURING_EMAIL": os.getenv("TURING_EMAIL"),
        "TURING_PASSWORD": os.getenv("TURING_PASSWORD"),
        "INDEED_EMAIL": os.getenv("INDEED_EMAIL"),
        "INDEED_PASSWORD": os.getenv("INDEED_PASSWORD"),
        "DICE_EMAIL": os.getenv("DICE_EMAIL"),
        "DICE_PASSWORD": os.getenv("DICE_PASSWORD"),
        
        # Optional Platform Credentials
        "WEWORKREMOTELY_EMAIL": os.getenv("WEWORKREMOTELY_EMAIL"),
        "WEWORKREMOTELY_PASSWORD": os.getenv("WEWORKREMOTELY_PASSWORD"),
        "FLEXJOBS_EMAIL": os.getenv("FLEXJOBS_EMAIL"),
        "FLEXJOBS_PASSWORD": os.getenv("FLEXJOBS_PASSWORD"),
        "REMOTEOK_EMAIL": os.getenv("REMOTEOK_EMAIL"),
        "REMOTEOK_PASSWORD": os.getenv("REMOTEOK_PASSWORD")
    }
    
    success_count = 0
    total_count = len(secrets)
    
    print(f"\n🔐 Setting up {total_count} GitHub Secrets...")
    print("-" * 50)
    
    for name, value in secrets.items():
        if value and value not in ["your.email@example.com", "your_password", "your_twitter_password"]:
            if set_github_secret(name, value):
                success_count += 1
        else:
            print(f"⚠️  Skipping {name} (not filled out)")
    
    print("-" * 50)
    print(f"✅ Successfully set {success_count}/{total_count} secrets")
    
    return success_count == total_count

def install_github_cli():
    """Provide instructions to install GitHub CLI"""
    print("\n📥 GitHub CLI Installation:")
    print("-" * 40)
    print("Windows (using winget):")
    print("  winget install --id GitHub.cli")
    print("\nWindows (using Chocolatey):")
    print("  choco install gh")
    print("\nWindows (using Scoop):")
    print("  scoop install gh")
    print("\nManual download:")
    print("  https://cli.github.com/")
    print("\nAfter installation, restart your terminal and run:")
    print("  gh auth login")

def manual_setup_instructions():
    """Provide manual setup instructions"""
    print("\n📋 MANUAL SETUP REQUIRED")
    print("=" * 50)
    print("Go to: https://github.com/Rahuljoshi07/job-bot/settings/secrets/actions")
    print("Add each secret manually using the values from credentials_template.env")
    print("\nOr install GitHub CLI and run this script again.")

def main():
    """Main function"""
    print("🚀 Automated GitHub Secrets Setup")
    print("=" * 50)
    
    # Check if credentials template exists
    if not os.path.exists("credentials_template.env"):
        print("❌ credentials_template.env not found!")
        print("Please fill out the credentials template first.")
        return 1
    
    # Check GitHub CLI
    if not check_github_cli():
        print("❌ GitHub CLI not found")
        install_github_cli()
        manual_setup_instructions()
        return 1
    
    # Check authentication
    if not check_github_auth():
        print("\n🔑 Please authenticate with GitHub CLI:")
        print("Run: gh auth login")
        print("Then run this script again.")
        return 1
    
    # Set up secrets
    if setup_all_secrets():
        print("\n🎉 ALL SECRETS SET UP SUCCESSFULLY!")
        print("Your job bot is now ready to run!")
        return 0
    else:
        print("\n⚠️  Some secrets failed to set up")
        manual_setup_instructions()
        return 1

if __name__ == "__main__":
    sys.exit(main())
