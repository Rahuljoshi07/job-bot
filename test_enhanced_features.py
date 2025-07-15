#!/usr/bin/env python3
"""
Test script for enhanced job bot functionality
"""

import os
import sys
import json
import sqlite3
from datetime import datetime

def test_basic_imports():
    """Test basic imports"""
    print("Testing basic imports...")
    
    try:
        import requests
        print("✅ requests imported")
    except ImportError as e:
        print(f"❌ requests import failed: {e}")
    
    try:
        from web_dashboard import JobBotDashboard
        print("✅ JobBotDashboard imported")
    except ImportError as e:
        print(f"❌ JobBotDashboard import failed: {e}")
    
    try:
        from enhanced_cli import JobBotCLI
        print("✅ JobBotCLI imported")
    except ImportError as e:
        print(f"❌ JobBotCLI import failed: {e}")
    
    try:
        from notifications import NotificationManager
        print("✅ NotificationManager imported")
    except ImportError as e:
        print(f"❌ NotificationManager import failed: {e}")

def test_database_creation():
    """Test database creation"""
    print("\nTesting database creation...")
    
    try:
        from web_dashboard import JobBotDashboard
        dashboard = JobBotDashboard(db_path='test_job_bot.db')
        
        # Check if database was created
        if os.path.exists('test_job_bot.db'):
            print("✅ Database created successfully")
            
            # Check tables
            conn = sqlite3.connect('test_job_bot.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            
            table_names = [table[0] for table in tables]
            if 'applications' in table_names:
                print("✅ Applications table created")
            if 'statistics' in table_names:
                print("✅ Statistics table created")
            
            # Clean up
            os.remove('test_job_bot.db')
        else:
            print("❌ Database creation failed")
    except Exception as e:
        print(f"❌ Database test failed: {e}")

def test_notifications_config():
    """Test notification configuration"""
    print("\nTesting notification configuration...")
    
    try:
        from notifications import NotificationManager
        notifier = NotificationManager(config_file='test_notification_config.json')
        
        # Check if config is loaded
        if notifier.config:
            print("✅ Notification config loaded")
            
            # Check default structure
            if 'email' in notifier.config:
                print("✅ Email config section exists")
            if 'desktop' in notifier.config:
                print("✅ Desktop config section exists")
            if 'summary_reports' in notifier.config:
                print("✅ Summary reports config section exists")
        
        # Clean up
        if os.path.exists('test_notification_config.json'):
            os.remove('test_notification_config.json')
            
    except Exception as e:
        print(f"❌ Notification config test failed: {e}")

def test_cli_help():
    """Test CLI help functionality"""
    print("\nTesting CLI help...")
    
    try:
        from enhanced_cli import JobBotCLI
        cli = JobBotCLI()
        
        # Test help method exists
        if hasattr(cli, 'show_help'):
            print("✅ CLI help method exists")
        
        # Test logo method exists
        if hasattr(cli, 'print_logo'):
            print("✅ CLI logo method exists")
            
    except Exception as e:
        print(f"❌ CLI test failed: {e}")

def test_enhanced_job_bot():
    """Test enhanced job bot integration"""
    print("\nTesting enhanced job bot...")
    
    try:
        from enhanced_job_bot import EnhancedJobBot
        
        # Create enhanced bot
        bot = EnhancedJobBot(config_file='test_config.json')
        
        if bot.dashboard:
            print("✅ Dashboard component initialized")
        if bot.notifications:
            print("✅ Notifications component initialized")
        if bot.job_bot:
            print("✅ Job bot component initialized")
            
        # Clean up
        if os.path.exists('test_config.json'):
            os.remove('test_config.json')
            
    except Exception as e:
        print(f"❌ Enhanced job bot test failed: {e}")

def test_sample_data():
    """Test with sample application data"""
    print("\nTesting with sample data...")
    
    try:
        from web_dashboard import JobBotDashboard
        
        # Create sample applications file
        sample_data = """2024-01-01 10:00:00 - Applied to DevOps Engineer at TechCorp (RemoteOK)
2024-01-01 10:05:00 - Applied to Cloud Engineer at CloudCorp (DICE)
2024-01-01 10:10:00 - Applied to Platform Engineer at PlatformCorp (LinkedIn)
"""
        with open('test_applications.txt', 'w') as f:
            f.write(sample_data)
        
        # Test dashboard with sample data
        dashboard = JobBotDashboard(db_path='test_with_data.db', applications_file='test_applications.txt')
        
        # Get statistics
        stats = dashboard.get_statistics()
        
        if stats['total_applications'] > 0:
            print(f"✅ Sample data loaded: {stats['total_applications']} applications")
        
        if stats['platform_stats']:
            print(f"✅ Platform statistics: {stats['platform_stats']}")
        
        # Clean up
        os.remove('test_applications.txt')
        os.remove('test_with_data.db')
        
    except Exception as e:
        print(f"❌ Sample data test failed: {e}")

def test_all():
    """Run all tests"""
    print("🧪 Running Enhanced Job Bot Tests")
    print("=" * 50)
    
    test_basic_imports()
    test_database_creation()
    test_notifications_config()
    test_cli_help()
    test_enhanced_job_bot()
    test_sample_data()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")
    print("\nTo use the enhanced job bot:")
    print("1. Run setup: python enhanced_job_bot.py setup")
    print("2. Use CLI: python enhanced_cli.py interactive")
    print("3. Web dashboard: python web_dashboard.py")

if __name__ == '__main__':
    test_all()