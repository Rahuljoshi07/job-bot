#!/usr/bin/env python3
"""
🚀 ENHANCED ULTIMATE JOB BOT STARTER
Launcher script for the enhanced AI-powered job application system
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'selenium', 'requests', 'beautifulsoup4', 'webdriver_manager',
        'schedule', 'PyPDF2', 'python-docx'
    ]
    
    optional_packages = [
        'nltk', 'spacy', 'textblob', 'scikit-learn', 'pandas', 'numpy'
    ]
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_required.append(package)
    
    for package in optional_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_optional.append(package)
    
    if missing_required:
        print(f"❌ Missing required packages: {', '.join(missing_required)}")
        print("Please install with: pip install -r requirements.txt")
        return False
    
    if missing_optional:
        print(f"⚠️ Missing optional AI packages: {', '.join(missing_optional)}")
        print("Some AI features will be disabled. Install with: pip install -r requirements.txt")
    
    print("✅ Dependencies check completed")
    return True

def setup_environment():
    """Setup environment and configuration"""
    print("⚙️ Setting up environment...")
    
    # Create necessary directories
    directories = ['application_proofs', 'logs', 'data']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Check for configuration
    config_file = "user_config.json"
    if not os.path.exists(config_file):
        print("⚠️ Configuration file not found. Using environment variables or defaults.")
    else:
        print(f"✅ Found configuration file: {config_file}")
    
    # Check for resume
    resume_files = ["resume.pdf", "resume.docx", "resume.txt"]
    resume_found = False
    for resume_file in resume_files:
        if os.path.exists(resume_file):
            print(f"✅ Found resume: {resume_file}")
            resume_found = True
            break
    
    if not resume_found:
        print("⚠️ No resume found. Resume parsing features will be limited.")
    
    print("✅ Environment setup completed")

def show_startup_banner():
    """Display startup banner"""
    banner = """
╔════════════════════════════════════════════════════════════════╗
║                🚀 ENHANCED ULTIMATE JOB BOT                   ║
║                   AI-POWERED AUTOMATION                       ║
╚════════════════════════════════════════════════════════════════╝

🎯 Features:
├── 🔍 Multi-Platform Job Discovery (RemoteOK, LinkedIn, Dice, etc.)
├── 🤖 AI-Powered Job Relevance Scoring
├── 📄 Resume Parsing & Skill Gap Analysis
├── 💌 Smart Cover Letter Generation
├── 📸 Application Proof Screenshots
├── 📊 Analytics Dashboard & Reporting
├── 🔔 Email Notifications
├── 🛡️ Advanced Security & Anti-Detection
├── ⏰ Smart Scheduling & Rate Limiting
└── 📈 Continuous Learning & Optimization

"""
    print(banner)

def get_user_choice():
    """Get user's choice for bot operation mode"""
    print("🎛️ Choose operation mode:")
    print("1. Single Run (Apply to jobs once)")
    print("2. Continuous Mode (24/7 automated operation)")
    print("3. Test Mode (Dry run without applying)")
    print("4. Configuration Setup")
    print("5. View Analytics Dashboard")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return int(choice)
            else:
                print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)

def run_configuration_setup():
    """Run interactive configuration setup"""
    print("\n🔧 CONFIGURATION SETUP")
    print("=" * 40)
    
    config = {}
    
    # Personal information
    print("\n📋 Personal Information:")
    config['personal'] = {
        'full_name': input("Full Name: ").strip() or "Job Seeker",
        'email': input("Email: ").strip() or "jobseeker@example.com",
        'phone': input("Phone: ").strip() or "+1234567890",
        'location': input("Location (or 'Remote'): ").strip() or "Remote",
        'linkedin': input("LinkedIn URL (optional): ").strip(),
        'github': input("GitHub URL (optional): ").strip()
    }
    
    # Job preferences
    print("\n🎯 Job Preferences:")
    job_titles = input("Preferred job titles (comma-separated): ").strip()
    if job_titles:
        config['preferences'] = {
            'job_titles': [title.strip() for title in job_titles.split(',')],
            'skills': [],
            'blacklisted_companies': [],
            'preferred_companies': [],
            'salary_min': int(input("Minimum salary (or 0 for any): ").strip() or "0"),
            'remote_only': input("Remote jobs only? (y/n): ").strip().lower() == 'y',
            'experience_level': input("Experience level (entry/mid/senior): ").strip() or "entry"
        }
    
    # Save configuration
    with open('user_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuration saved to user_config.json")

def view_analytics():
    """View analytics dashboard"""
    print("\n📊 ANALYTICS DASHBOARD")
    print("=" * 40)
    
    # Check for database file
    if os.path.exists('job_bot.db'):
        try:
            import sqlite3
            conn = sqlite3.connect('job_bot.db')
            cursor = conn.cursor()
            
            # Get basic stats
            cursor.execute("SELECT COUNT(*) FROM applications")
            total_applications = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT platform) FROM applications")
            platforms_used = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(relevance_score) FROM applications WHERE relevance_score > 0")
            avg_score = cursor.fetchone()[0] or 0
            
            print(f"📈 Total Applications: {total_applications}")
            print(f"🌐 Platforms Used: {platforms_used}")
            print(f"🎯 Average Relevance Score: {avg_score:.1f}%")
            
            # Recent applications
            cursor.execute("""
                SELECT title, company, platform, applied_date, relevance_score 
                FROM applications 
                ORDER BY applied_date DESC 
                LIMIT 10
            """)
            recent_apps = cursor.fetchall()
            
            if recent_apps:
                print("\n📋 Recent Applications:")
                for app in recent_apps:
                    title, company, platform, date, score = app
                    print(f"  • {title} at {company} ({platform}) - {score:.1f}% - {date}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error reading analytics: {e}")
    else:
        print("📊 No analytics data available yet. Run the bot first!")
    
    input("\nPress Enter to continue...")

def run_bot(mode):
    """Run the enhanced ultimate job bot"""
    print(f"\n🚀 Starting Enhanced Ultimate Job Bot in mode {mode}...")
    
    try:
        if mode == 1:  # Single run
            subprocess.run([sys.executable, "enhanced_ultimate_job_bot.py"], check=True)
        elif mode == 2:  # Continuous
            subprocess.run([sys.executable, "enhanced_ultimate_job_bot.py", "--continuous"], check=True)
        elif mode == 3:  # Test mode
            print("🧪 Test mode - would run bot in dry-run mode")
            # Add test mode logic here
        
        print("✅ Bot execution completed!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Bot execution failed with code {e.returncode}")
        print("Check the logs for more details.")
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    """Main function"""
    try:
        # Show banner
        show_startup_banner()
        
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        # Setup environment
        setup_environment()
        
        # Main loop
        while True:
            choice = get_user_choice()
            
            if choice == 1 or choice == 2 or choice == 3:
                run_bot(choice)
                break
            elif choice == 4:
                run_configuration_setup()
            elif choice == 5:
                view_analytics()
            
            print()  # Add spacing
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
