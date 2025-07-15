#!/usr/bin/env python3
"""
Enhanced Command Line Interface for Job Bot
Provides intuitive command structure, colored output, and interactive mode
"""

import argparse
import sys
import os
import time
import json
from datetime import datetime
import subprocess

# Check for colorama availability
try:
    from colorama import init, Fore, Back, Style
    init()  # Initialize colorama
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Fallback color definitions
    class MockColor:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ''
    
    Fore = Back = Style = MockColor()

# Check for click availability for better CLI
try:
    import click
    CLICK_AVAILABLE = True
except ImportError:
    CLICK_AVAILABLE = False

# Check for tqdm for progress bars
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

class ColoredOutput:
    """Handle colored output with fallback"""
    
    @staticmethod
    def success(message):
        return f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}"
    
    @staticmethod
    def error(message):
        return f"{Fore.RED}❌ {message}{Style.RESET_ALL}"
    
    @staticmethod
    def warning(message):
        return f"{Fore.YELLOW}⚠️ {message}{Style.RESET_ALL}"
    
    @staticmethod
    def info(message):
        return f"{Fore.CYAN}ℹ️ {message}{Style.RESET_ALL}"
    
    @staticmethod
    def header(message):
        return f"{Fore.MAGENTA}{Style.BRIGHT}🤖 {message}{Style.RESET_ALL}"
    
    @staticmethod
    def progress(message):
        return f"{Fore.BLUE}🔄 {message}{Style.RESET_ALL}"

class ProgressBar:
    """Progress bar with fallback"""
    
    def __init__(self, total, description="Processing"):
        self.total = total
        self.description = description
        self.current = 0
        
        if TQDM_AVAILABLE:
            self.pbar = tqdm(total=total, desc=description, unit="item")
        else:
            self.pbar = None
            print(f"{ColoredOutput.progress(description)} (0/{total})")
    
    def update(self, n=1):
        self.current += n
        if self.pbar:
            self.pbar.update(n)
        else:
            print(f"{ColoredOutput.progress(self.description)} ({self.current}/{self.total})")
    
    def close(self):
        if self.pbar:
            self.pbar.close()
        else:
            print(f"{ColoredOutput.success(f'{self.description} completed')} ({self.current}/{self.total})")

class JobBotCLI:
    """Enhanced CLI for Job Bot"""
    
    def __init__(self):
        self.config_file = 'user_config.json'
        self.applications_file = 'applications.txt'
        self.logo = """
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                      ║
║                            🤖 JOB BOT ENHANCED CLI                                  ║
║                                                                                      ║
║                     Automated Job Application Assistant                             ║
║                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
        """
    
    def print_logo(self):
        """Print the application logo"""
        print(f"{Fore.CYAN}{self.logo}{Style.RESET_ALL}")
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(ColoredOutput.error("Configuration file is corrupted"))
                return None
        return None
    
    def save_config(self, config):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(ColoredOutput.success("Configuration saved"))
            return True
        except Exception as e:
            print(ColoredOutput.error(f"Failed to save configuration: {e}"))
            return False
    
    def interactive_setup(self):
        """Interactive configuration setup"""
        print(ColoredOutput.header("Interactive Setup"))
        print("Let's configure your job bot step by step...\n")
        
        config = {
            'personal': {},
            'platforms': {},
            'job_preferences': {}
        }
        
        # Personal information
        print(ColoredOutput.info("Personal Information"))
        config['personal']['full_name'] = input("Full Name: ")
        config['personal']['email'] = input("Email: ")
        config['personal']['phone'] = input("Phone: ")
        config['personal']['location'] = input("Location: ")
        config['personal']['linkedin'] = input("LinkedIn Profile (optional): ")
        config['personal']['github'] = input("GitHub Profile (optional): ")
        
        # Job preferences
        print(f"\n{ColoredOutput.info('Job Preferences')}")
        config['job_preferences']['job_titles'] = input("Preferred Job Titles (comma-separated): ").split(',')
        config['job_preferences']['skills'] = input("Your Skills (comma-separated): ").split(',')
        config['job_preferences']['experience_level'] = input("Experience Level (entry/mid/senior): ")
        config['job_preferences']['remote_preference'] = input("Remote Preference (remote/hybrid/onsite): ")
        config['job_preferences']['salary_min'] = input("Minimum Salary (optional): ")
        
        # Platform credentials
        print(f"\n{ColoredOutput.info('Platform Credentials')}")
        print("Configure job platforms (leave empty to skip):")
        
        platforms = ['linkedin', 'indeed', 'dice', 'glassdoor']
        for platform in platforms:
            print(f"\n{platform.title()}:")
            email = input(f"  Email: ")
            if email:
                password = input(f"  Password: ")
                config['platforms'][platform] = {
                    'email': email,
                    'password': password
                }
        
        # Save configuration
        if self.save_config(config):
            print(f"\n{ColoredOutput.success('Setup completed successfully!')}")
            return config
        else:
            print(f"\n{ColoredOutput.error('Setup failed')}")
            return None
    
    def status_command(self):
        """Show current status and statistics"""
        print(ColoredOutput.header("Job Bot Status"))
        
        config = self.load_config()
        if not config:
            print(ColoredOutput.warning("No configuration found. Run 'setup' first."))
            return
        
        # Show configuration status
        print(f"\n{ColoredOutput.info('Configuration Status:')}")
        print(f"  Name: {config.get('personal', {}).get('full_name', 'Not set')}")
        print(f"  Email: {config.get('personal', {}).get('email', 'Not set')}")
        print(f"  Platforms: {len(config.get('platforms', {}))}")
        
        # Show application statistics
        if os.path.exists(self.applications_file):
            with open(self.applications_file, 'r') as f:
                applications = f.readlines()
            
            print(f"\n{ColoredOutput.info('Application Statistics:')}")
            print(f"  Total Applications: {len(applications)}")
            
            # Count by platform
            platform_counts = {}
            for app in applications:
                if '(' in app and ')' in app:
                    platform = app.split('(')[-1].split(')')[0]
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            for platform, count in platform_counts.items():
                print(f"  {platform}: {count}")
        
        # Show recent applications
        print(f"\n{ColoredOutput.info('Recent Applications:')}")
        if os.path.exists(self.applications_file):
            with open(self.applications_file, 'r') as f:
                recent = f.readlines()[-5:]  # Last 5 applications
            
            for app in recent:
                app = app.strip()
                if app:
                    print(f"  {app}")
        else:
            print("  No applications found")
    
    def search_command(self, platforms=None, dry_run=False):
        """Search for jobs on specified platforms"""
        if not platforms:
            platforms = ['remoteok', 'dice']
        
        print(ColoredOutput.header(f"Searching for jobs on: {', '.join(platforms)}"))
        
        if dry_run:
            print(ColoredOutput.warning("DRY RUN MODE - No applications will be submitted"))
        
        # Import and use the existing job bot
        try:
            from job_bot import JobBot
            bot = JobBot()
            
            # Create progress bar
            progress = ProgressBar(len(platforms), "Searching platforms")
            
            total_jobs = []
            for platform in platforms:
                if platform.lower() == 'remoteok':
                    jobs = bot.search_remoteok()
                elif platform.lower() == 'dice':
                    jobs = bot.search_dice_simulation()
                else:
                    print(ColoredOutput.warning(f"Platform '{platform}' not supported"))
                    jobs = []
                
                total_jobs.extend(jobs)
                progress.update()
            
            progress.close()
            
            print(f"\n{ColoredOutput.success(f'Found {len(total_jobs)} matching jobs')}")
            
            # Show found jobs
            for job in total_jobs:
                print(f"  📋 {job['title']} at {job['company']} ({job['platform']})")
            
            # Apply to jobs if not dry run
            if not dry_run and total_jobs:
                confirm = input(f"\n{ColoredOutput.info('Apply to these jobs? (y/n): ')}")
                if confirm.lower() == 'y':
                    apply_progress = ProgressBar(len(total_jobs), "Applying to jobs")
                    
                    for job in total_jobs:
                        bot.apply_to_job(job)
                        apply_progress.update()
                        time.sleep(2)  # Delay between applications
                    
                    apply_progress.close()
                    print(ColoredOutput.success(f"Applied to {len(total_jobs)} jobs"))
                else:
                    print(ColoredOutput.info("Application cancelled"))
            
        except ImportError:
            print(ColoredOutput.error("Job bot module not found"))
    
    def monitor_command(self, interval=30):
        """Start continuous monitoring"""
        print(ColoredOutput.header(f"Starting continuous monitoring (every {interval} minutes)"))
        
        try:
            import schedule
            
            def run_search():
                print(f"\n{ColoredOutput.info('Running scheduled search...')}")
                self.search_command()
            
            schedule.every(interval).minutes.do(run_search)
            
            # Run immediately
            run_search()
            
            print(f"{ColoredOutput.success('Monitoring started')} - Press Ctrl+C to stop")
            
            while True:
                schedule.run_pending()
                time.sleep(60)
                
        except KeyboardInterrupt:
            print(f"\n{ColoredOutput.info('Monitoring stopped')}")
        except ImportError:
            print(ColoredOutput.error("Schedule module not found"))
    
    def dashboard_command(self):
        """Launch web dashboard"""
        print(ColoredOutput.header("Launching Web Dashboard"))
        
        try:
            from web_dashboard import run_dashboard
            run_dashboard()
        except ImportError:
            print(ColoredOutput.error("Web dashboard module not found"))
    
    def interactive_mode(self):
        """Interactive mode for easier operation"""
        print(ColoredOutput.header("Interactive Mode"))
        print("Type 'help' for available commands or 'exit' to quit\n")
        
        while True:
            try:
                command = input(f"{Fore.CYAN}job-bot> {Style.RESET_ALL}").strip()
                
                if command == 'exit':
                    print(ColoredOutput.info("Goodbye!"))
                    break
                elif command == 'help':
                    self.show_help()
                elif command == 'status':
                    self.status_command()
                elif command == 'setup':
                    self.interactive_setup()
                elif command.startswith('search'):
                    parts = command.split()
                    platforms = parts[1:] if len(parts) > 1 else None
                    self.search_command(platforms)
                elif command == 'dashboard':
                    self.dashboard_command()
                elif command.startswith('monitor'):
                    parts = command.split()
                    interval = int(parts[1]) if len(parts) > 1 else 30
                    self.monitor_command(interval)
                elif command == '':
                    continue
                else:
                    print(ColoredOutput.error(f"Unknown command: {command}"))
                    print("Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print(f"\n{ColoredOutput.info('Use exit to quit')}")
            except EOFError:
                print(f"\n{ColoredOutput.info('Goodbye!')}")
                break
    
    def show_help(self):
        """Show help information"""
        help_text = f"""
{ColoredOutput.header('Available Commands:')}

{ColoredOutput.info('Setup & Configuration:')}
  setup                 - Interactive setup wizard
  status               - Show current status and statistics

{ColoredOutput.info('Job Search:')}
  search [platforms]   - Search for jobs (platforms: remoteok, dice)
  search --dry-run     - Search without applying
  monitor [interval]   - Start continuous monitoring (default: 30 min)

{ColoredOutput.info('Dashboard:')}
  dashboard            - Launch web dashboard

{ColoredOutput.info('Interactive Mode:')}
  interactive          - Enter interactive mode
  help                 - Show this help
  exit                 - Exit the application

{ColoredOutput.info('Examples:')}
  python enhanced_cli.py setup
  python enhanced_cli.py search remoteok dice
  python enhanced_cli.py search --dry-run
  python enhanced_cli.py monitor 60
  python enhanced_cli.py dashboard
  python enhanced_cli.py interactive
        """
        print(help_text)

def main():
    """Main CLI entry point"""
    cli = JobBotCLI()
    
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Enhanced Job Bot CLI - Automated Job Application Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Interactive setup wizard')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show current status')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for jobs')
    search_parser.add_argument('platforms', nargs='*', help='Platforms to search')
    search_parser.add_argument('--dry-run', action='store_true', help='Search without applying')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Start continuous monitoring')
    monitor_parser.add_argument('--interval', type=int, default=30, help='Monitoring interval in minutes')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Launch web dashboard')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Enter interactive mode')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show logo
    cli.print_logo()
    
    # Handle commands
    if args.command == 'setup':
        cli.interactive_setup()
    elif args.command == 'status':
        cli.status_command()
    elif args.command == 'search':
        cli.search_command(args.platforms, args.dry_run)
    elif args.command == 'monitor':
        cli.monitor_command(args.interval)
    elif args.command == 'dashboard':
        cli.dashboard_command()
    elif args.command == 'interactive':
        cli.interactive_mode()
    else:
        # No command provided, show help
        cli.show_help()

if __name__ == '__main__':
    main()