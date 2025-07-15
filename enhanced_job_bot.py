#!/usr/bin/env python3
"""
Enhanced Job Bot Integration
Integrates new UI improvements with existing job bot functionality
"""

import os
import sys
import json
import sqlite3
from datetime import datetime

# Import existing modules
from job_bot import JobBot
from web_dashboard import JobBotDashboard
from notifications import NotificationManager

class EnhancedJobBot:
    """Enhanced job bot with UI improvements and notifications"""
    
    def __init__(self, config_file='user_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        
        # Initialize components
        self.job_bot = JobBot()
        self.dashboard = JobBotDashboard()
        self.notifications = NotificationManager()
        
        # Override job bot's apply_to_job method to add notifications
        self.job_bot.apply_to_job = self.enhanced_apply_to_job
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def enhanced_apply_to_job(self, job):
        """Enhanced job application with notifications and database logging"""
        try:
            print(f"📝 Applying to: {job['title']} at {job['company']} ({job['platform']})")
            
            # Mark as applied in original bot
            self.job_bot.applied_jobs.add(job['id'])
            
            # Log to text file (original functionality)
            with open('applications.txt', 'a') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Applied to {job['title']} at {job['company']} ({job['platform']})\n")
            
            # Add to database (new functionality)
            self.dashboard.add_application(
                job_title=job['title'],
                company=job['company'],
                platform=job['platform'],
                url=job.get('url'),
                application_id=job.get('id')
            )
            
            # Send notifications (new functionality)
            self.notifications.notify_application_sent(
                job['title'],
                job['company'],
                job['platform']
            )
            
            print(f"✅ Application submitted successfully!")
            return True
            
        except Exception as e:
            error_msg = f"Failed to apply to {job['title']} at {job['company']}: {e}"
            print(f"❌ {error_msg}")
            
            # Send error notification
            self.notifications.notify_error(error_msg, f"Job application for {job['title']}")
            return False
    
    def enhanced_run_job_search(self, platforms=None):
        """Enhanced job search with improved logging and notifications"""
        if platforms is None:
            platforms = ['remoteok', 'dice']
        
        print(f"\n🤖 Enhanced Job Bot running at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔍 Searching platforms: {', '.join(platforms)}")
        
        all_jobs = []
        
        try:
            # Search platforms
            for platform in platforms:
                if platform.lower() == 'remoteok':
                    jobs = self.job_bot.search_remoteok()
                elif platform.lower() == 'dice':
                    jobs = self.job_bot.search_dice_simulation()
                else:
                    print(f"⚠️ Platform '{platform}' not supported")
                    continue
                
                all_jobs.extend(jobs)
            
            # Apply to found jobs
            applications_sent = 0
            for job in all_jobs:
                if self.enhanced_apply_to_job(job):
                    applications_sent += 1
                    import time
                    time.sleep(2)  # Delay between applications
            
            print(f"🎯 Total applications sent: {applications_sent}")
            print("-" * 50)
            
            # Send search completion notification
            self.notifications.notify_search_completed(
                platforms=platforms,
                jobs_found=len(all_jobs),
                applications_sent=applications_sent
            )
            
            return {
                'jobs_found': len(all_jobs),
                'applications_sent': applications_sent,
                'platforms': platforms
            }
            
        except Exception as e:
            error_msg = f"Error during job search: {e}"
            print(f"❌ {error_msg}")
            self.notifications.notify_error(error_msg, "Job search process")
            return None
    
    def start_enhanced_monitoring(self, interval=30):
        """Start enhanced monitoring with notifications"""
        try:
            import schedule
            
            def run_search():
                result = self.enhanced_run_job_search()
                if result:
                    print(f"✅ Search completed: {result['applications_sent']} applications sent")
                else:
                    print("❌ Search failed")
            
            def send_daily_summary():
                success = self.notifications.generate_daily_summary()
                print(f"📊 Daily summary {'sent' if success else 'failed'}")
            
            def send_weekly_summary():
                success = self.notifications.generate_weekly_summary()
                print(f"📈 Weekly summary {'sent' if success else 'failed'}")
            
            # Schedule job searches
            schedule.every(interval).minutes.do(run_search)
            
            # Schedule daily summary
            if self.notifications.config['summary_reports']['daily']['enabled']:
                daily_time = self.notifications.config['summary_reports']['daily']['time']
                schedule.every().day.at(daily_time).do(send_daily_summary)
            
            # Schedule weekly summary
            if self.notifications.config['summary_reports']['weekly']['enabled']:
                weekly_day = self.notifications.config['summary_reports']['weekly']['day']
                weekly_time = self.notifications.config['summary_reports']['weekly']['time']
                getattr(schedule.every(), weekly_day).at(weekly_time).do(send_weekly_summary)
            
            print(f"🚀 Enhanced monitoring started (interval: {interval} minutes)")
            print("   📧 Email notifications enabled" if self.notifications.config['email']['enabled'] else "   📧 Email notifications disabled")
            print("   🖥️ Desktop notifications enabled" if self.notifications.config['desktop']['enabled'] else "   🖥️ Desktop notifications disabled")
            print("   📊 Summary reports enabled")
            print("   🌐 Web dashboard available at http://localhost:5000")
            print("\nPress Ctrl+C to stop monitoring\n")
            
            # Run immediately
            run_search()
            
            # Continuous loop
            while True:
                schedule.run_pending()
                import time
                time.sleep(60)
                
        except KeyboardInterrupt:
            print("\n🛑 Enhanced monitoring stopped")
            
        except Exception as e:
            error_msg = f"Error in enhanced monitoring: {e}"
            print(f"❌ {error_msg}")
            self.notifications.notify_error(error_msg, "Enhanced monitoring")
    
    def get_statistics(self):
        """Get enhanced statistics"""
        return {
            'dashboard_stats': self.dashboard.get_statistics(),
            'notification_config': self.notifications.config,
            'job_bot_config': self.config
        }
    
    def setup_all_systems(self):
        """Setup all enhanced systems interactively"""
        print("🚀 Enhanced Job Bot Setup")
        print("=" * 50)
        
        # Setup notifications first
        print("\n1. Setting up notification system...")
        self.notifications.setup_interactive()
        
        # Setup job preferences
        print("\n2. Setting up job preferences...")
        self.setup_job_preferences()
        
        # Initialize dashboard
        print("\n3. Initializing dashboard...")
        self.dashboard.load_applications_from_file()
        
        print("\n✅ All systems configured successfully!")
        print("\nYou can now use:")
        print("  - Enhanced CLI: python enhanced_cli.py")
        print("  - Web Dashboard: python web_dashboard.py")
        print("  - Notifications: Configured and ready")
        
    def setup_job_preferences(self):
        """Setup job preferences interactively"""
        print("\n🎯 Job Preferences Setup")
        
        config = {
            'personal': {},
            'job_preferences': {},
            'platforms': {}
        }
        
        # Personal info
        config['personal']['full_name'] = input("Full Name: ")
        config['personal']['email'] = input("Email: ")
        config['personal']['phone'] = input("Phone (optional): ")
        config['personal']['location'] = input("Location: ")
        
        # Job preferences
        print("\nJob Preferences:")
        job_titles = input("Preferred job titles (comma-separated): ")
        config['job_preferences']['job_titles'] = [title.strip() for title in job_titles.split(',')]
        
        skills = input("Your skills (comma-separated): ")
        config['job_preferences']['skills'] = [skill.strip() for skill in skills.split(',')]
        
        config['job_preferences']['experience_level'] = input("Experience level (entry/mid/senior): ")
        config['job_preferences']['remote_preference'] = input("Remote preference (remote/hybrid/onsite): ")
        
        # Save configuration
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ Job preferences saved!")
        except Exception as e:
            print(f"❌ Failed to save preferences: {e}")

def main():
    """Main function for enhanced job bot"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        enhanced_bot = EnhancedJobBot()
        
        if command == 'setup':
            enhanced_bot.setup_all_systems()
        elif command == 'search':
            platforms = sys.argv[2:] if len(sys.argv) > 2 else None
            enhanced_bot.enhanced_run_job_search(platforms)
        elif command == 'monitor':
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            enhanced_bot.start_enhanced_monitoring(interval)
        elif command == 'stats':
            stats = enhanced_bot.get_statistics()
            print(json.dumps(stats, indent=2))
        elif command == 'dashboard':
            from web_dashboard import run_dashboard
            run_dashboard()
        else:
            print("Unknown command")
            print("Usage: python enhanced_job_bot.py <command>")
            print("Commands: setup, search, monitor, stats, dashboard")
    else:
        print("Enhanced Job Bot - UI Improvements")
        print("=" * 40)
        print("Usage: python enhanced_job_bot.py <command>")
        print("\nCommands:")
        print("  setup     - Setup all systems interactively")
        print("  search    - Run job search once")
        print("  monitor   - Start continuous monitoring")
        print("  stats     - Show statistics")
        print("  dashboard - Launch web dashboard")
        print("\nFor better CLI experience, use:")
        print("  python enhanced_cli.py")

if __name__ == '__main__':
    main()