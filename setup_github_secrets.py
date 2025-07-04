#!/usr/bin/env python3
"""
GitHub Secrets Setup Helper
This script helps you set up GitHub Secrets from your credentials template file
"""

import os
import sys
from dotenv import load_dotenv

def load_credentials_from_template():
    """Load credentials from the template file"""
    template_file = "credentials_template.env"
    
    if not os.path.exists(template_file):
        print(f"❌ {template_file} not found!")
        print("Please fill out the credentials_template.env file first.")
        return None
    
    # Load environment variables from template
    load_dotenv(template_file)
    
    # Define all required secrets
    required_secrets = [
        # Personal Information
        "PERSONAL_FULL_NAME",
        "PERSONAL_EMAIL", 
        "PERSONAL_PHONE",
        "PERSONAL_LINKEDIN",
        "PERSONAL_GITHUB",
        "PERSONAL_LOCATION",
        
        # Platform Credentials
        "TWITTER_EMAIL",
        "TWITTER_PASSWORD",
        "TURING_EMAIL", 
        "TURING_PASSWORD",
        "INDEED_EMAIL",
        "INDEED_PASSWORD",
        "DICE_EMAIL",
        "DICE_PASSWORD",
        
        # Optional Platform Credentials
        "WEWORKREMOTELY_EMAIL",
        "WEWORKREMOTELY_PASSWORD",
        "FLEXJOBS_EMAIL",
        "FLEXJOBS_PASSWORD",
        "REMOTEOK_EMAIL",
        "REMOTEOK_PASSWORD"
    ]
    
    secrets = {}
    missing_secrets = []
    default_values = ["your.email@example.com", "your_password", "your_twitter_password", 
                     "your_turing_password", "your_indeed_password", "your.dice@email.com",
                     "your.twitter@email.com", "your.turing@email.com", "your.indeed@email.com",
                     "your.wwr@email.com", "your_wwr_password", "your.flexjobs@email.com",
                     "your_flexjobs_password", "your.remoteok@email.com", "your_remoteok_password"]
    
    for secret in required_secrets:
        value = os.getenv(secret, "")
        if value and value not in default_values:
            secrets[secret] = value
        else:
            missing_secrets.append(secret)
    
    return secrets, missing_secrets

def print_github_secrets_instructions(secrets, missing_secrets):
    """Print instructions for setting up GitHub Secrets"""
    
    print("🔐 GitHub Secrets Setup Instructions")
    print("=" * 50)
    print()
    print("Go to: https://github.com/Rahuljoshi07/job-bot/settings/secrets/actions")
    print()
    print("Click 'New repository secret' and add each of the following:")
    print()
    
    # Print secrets that are ready
    if secrets:
        print("✅ READY TO ADD (filled out in template):")
        print("-" * 40)
        for name, value in secrets.items():
            # Mask the value for security
            masked_value = value[:3] + "*" * (len(value) - 6) + value[-3:] if len(value) > 6 else "*" * len(value)
            print(f"Secret Name: {name}")
            print(f"Secret Value: {masked_value}")
            print()
    
    # Print missing secrets
    if missing_secrets:
        print("⚠️  STILL NEED TO FILL OUT:")
        print("-" * 40)
        for secret in missing_secrets:
            print(f"❌ {secret}")
        print()
        print("Please update credentials_template.env with the missing values.")
    
    print("🔗 Direct link to add secrets:")
    print("https://github.com/Rahuljoshi07/job-bot/settings/secrets/actions")
    print()
    print("🛡️  Security reminder: GitHub Secrets are encrypted and secure!")

def generate_curl_commands(secrets):
    """Generate curl commands for GitHub CLI (if available)"""
    
    if not secrets:
        return
    
    print("\n" + "=" * 50)
    print("🤖 ALTERNATIVE: GitHub CLI Commands")
    print("=" * 50)
    print("If you have GitHub CLI installed, you can use these commands:")
    print()
    
    for name, value in secrets.items():
        # Escape special characters for shell
        escaped_value = value.replace('"', '\\"').replace('$', '\\$')
        print(f'gh secret set {name} --body "{escaped_value}"')
    
    print()
    print("💡 To install GitHub CLI: https://cli.github.com/")

def main():
    """Main function"""
    print("🔒 GitHub Secrets Setup Helper")
    print("=" * 50)
    
    secrets, missing_secrets = load_credentials_from_template()
    
    if secrets is None:
        return 1
    
    if not secrets and missing_secrets:
        print("❌ No secrets ready! Please fill out credentials_template.env first.")
        print(f"Missing: {', '.join(missing_secrets)}")
        return 1
    
    print(f"✅ Found {len(secrets)} ready secrets")
    print(f"⚠️  Missing {len(missing_secrets)} secrets")
    print()
    
    print_github_secrets_instructions(secrets, missing_secrets)
    
    if secrets:
        generate_curl_commands(secrets)
    
    print("\n" + "=" * 50)
    print("🎉 After adding all secrets to GitHub, your bot will work perfectly!")
    print("Run the workflow manually or wait for the next scheduled run.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
