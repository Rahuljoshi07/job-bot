#!/usr/bin/env python3
"""
Notification System for Job Bot
Provides email notifications, desktop notifications, and summary reports
"""

import json
import os
import smtplib
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Check for desktop notification support
try:
    import plyer
    DESKTOP_NOTIFICATIONS = True
except ImportError:
    DESKTOP_NOTIFICATIONS = False

class NotificationManager:
    """Manages all types of notifications for the job bot"""
    
    def __init__(self, config_file='notification_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        self.applications_file = 'applications.txt'
        self.notifications_log = 'notifications_log.txt'
    
    def load_config(self):
        """Load notification configuration"""
        default_config = {
            'email': {
                'enabled': False,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': '',
                'sender_password': '',
                'recipient_email': '',
                'notifications': {
                    'application_sent': True,
                    'daily_summary': True,
                    'weekly_summary': True,
                    'errors': True
                }
            },
            'desktop': {
                'enabled': DESKTOP_NOTIFICATIONS,
                'notifications': {
                    'application_sent': True,
                    'search_completed': True,
                    'errors': True
                }
            },
            'summary_reports': {
                'daily': {
                    'enabled': True,
                    'time': '18:00'
                },
                'weekly': {
                    'enabled': True,
                    'day': 'sunday',
                    'time': '09:00'
                },
                'monthly': {
                    'enabled': False,
                    'day': 1,
                    'time': '09:00'
                }
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    return {**default_config, **loaded_config}
            except json.JSONDecodeError:
                pass
        
        return default_config
    
    def save_config(self):
        """Save notification configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            self.log_notification(f"Error saving config: {e}", 'error')
            return False
    
    def log_notification(self, message, level='info'):
        """Log notification events"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} [{level.upper()}] {message}\n"
        
        try:
            with open(self.notifications_log, 'a') as f:
                f.write(log_entry)
        except Exception:
            pass  # Fail silently to avoid notification loops
    
    def send_email(self, subject, body, html_body=None, attachments=None):
        """Send email notification"""
        if not self.config['email']['enabled']:
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.config['email']['sender_email']
            msg['To'] = self.config['email']['recipient_email']
            msg['Subject'] = subject
            
            # Add plain text body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add HTML body if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['sender_email'], self.config['email']['sender_password'])
            server.send_message(msg)
            server.quit()
            
            self.log_notification(f"Email sent: {subject}")
            return True
            
        except Exception as e:
            self.log_notification(f"Email error: {e}", 'error')
            return False
    
    def send_desktop_notification(self, title, message, timeout=5):
        """Send desktop notification"""
        if not self.config['desktop']['enabled'] or not DESKTOP_NOTIFICATIONS:
            return False
        
        try:
            plyer.notification.notify(
                title=title,
                message=message,
                timeout=timeout
            )
            self.log_notification(f"Desktop notification: {title}")
            return True
        except Exception as e:
            self.log_notification(f"Desktop notification error: {e}", 'error')
            return False
    
    def notify_application_sent(self, job_title, company, platform):
        """Notify when an application is sent"""
        # Desktop notification
        if self.config['desktop']['notifications']['application_sent']:
            self.send_desktop_notification(
                "Job Application Sent",
                f"Applied to {job_title} at {company} ({platform})"
            )
        
        # Email notification
        if self.config['email']['notifications']['application_sent']:
            subject = f"Job Application Sent: {job_title} at {company}"
            body = f"""
Hello,

Your job bot has successfully submitted an application:

Job Title: {job_title}
Company: {company}
Platform: {platform}
Applied At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Good luck with your application!

Best regards,
Job Bot
            """
            
            html_body = f"""
<html>
<body>
    <h2>Job Application Sent</h2>
    <p>Your job bot has successfully submitted an application:</p>
    
    <table style="border-collapse: collapse; width: 100%;">
        <tr>
            <td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">Job Title:</td>
            <td style="border: 1px solid #ddd; padding: 8px;">{job_title}</td>
        </tr>
        <tr>
            <td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">Company:</td>
            <td style="border: 1px solid #ddd; padding: 8px;">{company}</td>
        </tr>
        <tr>
            <td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">Platform:</td>
            <td style="border: 1px solid #ddd; padding: 8px;">{platform}</td>
        </tr>
        <tr>
            <td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">Applied At:</td>
            <td style="border: 1px solid #ddd; padding: 8px;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
        </tr>
    </table>
    
    <p>Good luck with your application!</p>
    <p><em>Best regards,<br>Job Bot</em></p>
</body>
</html>
            """
            
            self.send_email(subject, body, html_body)
    
    def notify_search_completed(self, platforms, jobs_found, applications_sent):
        """Notify when a search is completed"""
        # Desktop notification
        if self.config['desktop']['notifications']['search_completed']:
            self.send_desktop_notification(
                "Job Search Completed",
                f"Found {jobs_found} jobs, sent {applications_sent} applications"
            )
    
    def notify_error(self, error_message, context=None):
        """Notify about errors"""
        # Desktop notification
        if self.config['desktop']['notifications']['errors']:
            self.send_desktop_notification(
                "Job Bot Error",
                f"Error: {error_message}"
            )
        
        # Email notification
        if self.config['email']['notifications']['errors']:
            subject = "Job Bot Error Alert"
            body = f"""
Hello,

Your job bot encountered an error:

Error: {error_message}
Context: {context or 'Not provided'}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please check the application logs for more details.

Best regards,
Job Bot
            """
            
            self.send_email(subject, body)
    
    def generate_daily_summary(self):
        """Generate daily summary report"""
        try:
            today = datetime.now().date()
            today_str = today.strftime('%Y-%m-%d')
            
            # Read applications file
            applications_today = []
            if os.path.exists(self.applications_file):
                with open(self.applications_file, 'r') as f:
                    for line in f:
                        if today_str in line:
                            applications_today.append(line.strip())
            
            # Count by platform
            platform_counts = {}
            for app in applications_today:
                if '(' in app and ')' in app:
                    platform = app.split('(')[-1].split(')')[0]
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            # Generate report
            subject = f"Daily Job Bot Summary - {today_str}"
            body = f"""
Daily Job Bot Summary for {today_str}

Total Applications Sent: {len(applications_today)}

Applications by Platform:
{chr(10).join([f"  {platform}: {count}" for platform, count in platform_counts.items()])}

Recent Applications:
{chr(10).join([f"  {app}" for app in applications_today[-5:]])}

Keep up the great work!

Best regards,
Job Bot
            """
            
            html_body = f"""
<html>
<body>
    <h2>Daily Job Bot Summary - {today_str}</h2>
    
    <h3>Statistics</h3>
    <p><strong>Total Applications Sent:</strong> {len(applications_today)}</p>
    
    <h3>Applications by Platform</h3>
    <ul>
        {''.join([f"<li>{platform}: {count}</li>" for platform, count in platform_counts.items()])}
    </ul>
    
    <h3>Recent Applications</h3>
    <ul>
        {''.join([f"<li>{app}</li>" for app in applications_today[-5:]])}
    </ul>
    
    <p><em>Keep up the great work!</em></p>
    <p><em>Best regards,<br>Job Bot</em></p>
</body>
</html>
            """
            
            return self.send_email(subject, body, html_body)
            
        except Exception as e:
            self.log_notification(f"Daily summary error: {e}", 'error')
            return False
    
    def generate_weekly_summary(self):
        """Generate weekly summary report"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
            
            # Read applications file
            applications_week = []
            if os.path.exists(self.applications_file):
                with open(self.applications_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                app_date_str = line.split(' - ')[0]
                                app_date = datetime.strptime(app_date_str, '%Y-%m-%d %H:%M:%S').date()
                                if start_date <= app_date <= end_date:
                                    applications_week.append(line)
                            except ValueError:
                                continue
            
            # Count by platform and day
            platform_counts = {}
            daily_counts = {}
            
            for app in applications_week:
                # Platform count
                if '(' in app and ')' in app:
                    platform = app.split('(')[-1].split(')')[0]
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1
                
                # Daily count
                try:
                    app_date = datetime.strptime(app.split(' - ')[0], '%Y-%m-%d %H:%M:%S').date()
                    date_str = app_date.strftime('%Y-%m-%d')
                    daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
                except ValueError:
                    continue
            
            # Generate report
            subject = f"Weekly Job Bot Summary - {start_date} to {end_date}"
            body = f"""
Weekly Job Bot Summary ({start_date} to {end_date})

Total Applications Sent: {len(applications_week)}
Average per Day: {len(applications_week) / 7:.1f}

Applications by Platform:
{chr(10).join([f"  {platform}: {count}" for platform, count in platform_counts.items()])}

Daily Breakdown:
{chr(10).join([f"  {date}: {count}" for date, count in sorted(daily_counts.items())])}

Most Active Platform: {max(platform_counts, key=platform_counts.get) if platform_counts else 'None'}
Most Active Day: {max(daily_counts, key=daily_counts.get) if daily_counts else 'None'}

Great job this week!

Best regards,
Job Bot
            """
            
            return self.send_email(subject, body)
            
        except Exception as e:
            self.log_notification(f"Weekly summary error: {e}", 'error')
            return False
    
    def setup_interactive(self):
        """Interactive setup for notification preferences"""
        print("🔔 Notification System Setup")
        print("=" * 40)
        
        # Email setup
        print("\n📧 Email Notifications")
        enable_email = input("Enable email notifications? (y/n): ").lower() == 'y'
        
        if enable_email:
            self.config['email']['enabled'] = True
            self.config['email']['sender_email'] = input("Sender email: ")
            self.config['email']['sender_password'] = input("Sender password (use app password for Gmail): ")
            self.config['email']['recipient_email'] = input("Recipient email: ")
            
            # SMTP settings
            smtp_server = input("SMTP server (default: smtp.gmail.com): ") or 'smtp.gmail.com'
            smtp_port = input("SMTP port (default: 587): ") or '587'
            
            self.config['email']['smtp_server'] = smtp_server
            self.config['email']['smtp_port'] = int(smtp_port)
            
            # Notification preferences
            print("\nEmail notification preferences:")
            self.config['email']['notifications']['application_sent'] = input("Notify on application sent? (y/n): ").lower() == 'y'
            self.config['email']['notifications']['daily_summary'] = input("Send daily summary? (y/n): ").lower() == 'y'
            self.config['email']['notifications']['weekly_summary'] = input("Send weekly summary? (y/n): ").lower() == 'y'
            self.config['email']['notifications']['errors'] = input("Notify on errors? (y/n): ").lower() == 'y'
        
        # Desktop notifications
        print("\n🖥️ Desktop Notifications")
        if DESKTOP_NOTIFICATIONS:
            enable_desktop = input("Enable desktop notifications? (y/n): ").lower() == 'y'
            self.config['desktop']['enabled'] = enable_desktop
            
            if enable_desktop:
                print("\nDesktop notification preferences:")
                self.config['desktop']['notifications']['application_sent'] = input("Notify on application sent? (y/n): ").lower() == 'y'
                self.config['desktop']['notifications']['search_completed'] = input("Notify on search completed? (y/n): ").lower() == 'y'
                self.config['desktop']['notifications']['errors'] = input("Notify on errors? (y/n): ").lower() == 'y'
        else:
            print("Desktop notifications not available (plyer not installed)")
        
        # Summary reports
        print("\n📊 Summary Reports")
        self.config['summary_reports']['daily']['enabled'] = input("Enable daily summaries? (y/n): ").lower() == 'y'
        if self.config['summary_reports']['daily']['enabled']:
            daily_time = input("Daily summary time (HH:MM, default: 18:00): ") or '18:00'
            self.config['summary_reports']['daily']['time'] = daily_time
        
        self.config['summary_reports']['weekly']['enabled'] = input("Enable weekly summaries? (y/n): ").lower() == 'y'
        if self.config['summary_reports']['weekly']['enabled']:
            weekly_day = input("Weekly summary day (default: sunday): ") or 'sunday'
            weekly_time = input("Weekly summary time (HH:MM, default: 09:00): ") or '09:00'
            self.config['summary_reports']['weekly']['day'] = weekly_day
            self.config['summary_reports']['weekly']['time'] = weekly_time
        
        # Save configuration
        if self.save_config():
            print("\n✅ Notification system configured successfully!")
            
            # Test email if enabled
            if self.config['email']['enabled']:
                test_email = input("Send test email? (y/n): ").lower() == 'y'
                if test_email:
                    success = self.send_email(
                        "Job Bot Test Email",
                        "This is a test email from your job bot notification system. If you receive this, email notifications are working correctly!"
                    )
                    if success:
                        print("✅ Test email sent successfully!")
                    else:
                        print("❌ Test email failed. Check your settings.")
        else:
            print("❌ Failed to save configuration")

def main():
    """Main function for testing notification system"""
    notifier = NotificationManager()
    
    if len(os.sys.argv) > 1:
        command = os.sys.argv[1]
        
        if command == 'setup':
            notifier.setup_interactive()
        elif command == 'test':
            notifier.notify_application_sent("Test Job", "Test Company", "Test Platform")
        elif command == 'daily':
            notifier.generate_daily_summary()
        elif command == 'weekly':
            notifier.generate_weekly_summary()
        else:
            print("Unknown command. Use: setup, test, daily, weekly")
    else:
        print("Usage: python notifications.py <command>")
        print("Commands: setup, test, daily, weekly")

if __name__ == '__main__':
    main()