#!/usr/bin/env python3
"""
Example usage of the enhanced job bot with security and reliability features.
"""

import os
import sys
from datetime import datetime

# Add the current directory to sys.path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from security.credential_manager import CredentialManager
from application_tracking.tracker import ApplicationTracker, JobApplication, ApplicationStatus
from enhanced_job_bot import EnhancedJobBot
from logging_framework.logger import get_logger, log_security_event


def setup_credentials():
    """Set up sample credentials for demonstration."""
    print("🔐 Setting up secure credentials...")
    
    credential_manager = CredentialManager()
    
    # Sample credentials (in production, these would be loaded securely)
    sample_credentials = {
        ('linkedin', 'email'): 'user@example.com',
        ('linkedin', 'password'): 'secure_password_123',
        ('indeed', 'email'): 'user@example.com',
        ('indeed', 'password'): 'another_secure_password',
        ('remoteok', 'api_key'): 'api_key_12345',
    }
    
    for (platform, cred_type), value in sample_credentials.items():
        success = credential_manager.store_credential(platform, cred_type, value)
        if success:
            print(f"✅ Stored {cred_type} for {platform}")
        else:
            print(f"❌ Failed to store {cred_type} for {platform}")
    
    print("🔐 Credentials setup completed!")
    
    # Log security event
    log_security_event("credentials_setup", {
        "platforms": list(set(platform for platform, _ in sample_credentials.keys())),
        "credential_count": len(sample_credentials)
    })


def demonstrate_application_tracking():
    """Demonstrate the application tracking system."""
    print("\n📊 Demonstrating application tracking...")
    
    tracker = ApplicationTracker()
    
    # Create sample applications
    sample_applications = [
        JobApplication(
            platform="linkedin",
            job_id="job123",
            title="Senior DevOps Engineer",
            company="Tech Corp",
            url="https://linkedin.com/jobs/job123",
            status=ApplicationStatus.APPLIED
        ),
        JobApplication(
            platform="indeed",
            job_id="job456",
            title="Cloud Infrastructure Engineer",
            company="Cloud Solutions Inc",
            url="https://indeed.com/jobs/job456",
            status=ApplicationStatus.APPLIED
        ),
        JobApplication(
            platform="remoteok",
            job_id="job789",
            title="Platform Engineer",
            company="Remote Tech",
            url="https://remoteok.io/job789",
            status=ApplicationStatus.FAILED
        ),
    ]
    
    # Add applications to tracker
    for application in sample_applications:
        success = tracker.add_application(application)
        if success:
            print(f"✅ Tracked application: {application.title} at {application.company}")
        else:
            print(f"❌ Failed to track application: {application.title}")
    
    # Test duplicate detection
    duplicate_app = JobApplication(
        platform="linkedin",
        job_id="job124",  # Different job ID
        title="Senior DevOps Engineer",  # Same title
        company="Tech Corp",  # Same company
        url="https://linkedin.com/jobs/job123",  # Same URL
        status=ApplicationStatus.APPLIED
    )
    
    duplicate_success = tracker.add_application(duplicate_app)
    if not duplicate_success:
        print("✅ Duplicate application detected and prevented!")
    
    # Get statistics
    stats = tracker.get_statistics()
    print(f"\n📈 Application Statistics:")
    print(f"   Total applications: {stats['total_applications']}")
    print(f"   By platform: {stats['by_platform']}")
    print(f"   By status: {stats['by_status']}")
    
    # Get recent applications
    recent_apps = tracker.get_applications(limit=5)
    print(f"\n📋 Recent Applications:")
    for app in recent_apps:
        print(f"   - {app.title} at {app.company} ({app.platform}) - {app.status.value}")


def demonstrate_error_handling():
    """Demonstrate error handling and retry logic."""
    print("\n🔄 Demonstrating error handling and retry logic...")
    
    from error_handling.retry_logic import RetryManager, RetryConfig
    from error_handling.exceptions import PlatformError
    
    # Create retry configuration
    config = RetryConfig(
        max_attempts=3,
        base_delay=0.1,  # Short delay for demo
        backoff_factor=2.0
    )
    
    retry_manager = RetryManager(config)
    
    # Simulate a function that fails twice then succeeds
    attempt_count = 0
    
    def unreliable_operation():
        nonlocal attempt_count
        attempt_count += 1
        
        if attempt_count < 3:
            raise PlatformError(f"Simulated failure (attempt {attempt_count})")
        
        return f"Success after {attempt_count} attempts!"
    
    try:
        result = retry_manager.execute_with_retry(
            unreliable_operation,
            operation_name="demo_operation",
            platform="demo_platform"
        )
        print(f"✅ {result}")
    except Exception as e:
        print(f"❌ Operation failed: {e}")


def demonstrate_logging():
    """Demonstrate the logging framework."""
    print("\n📝 Demonstrating logging framework...")
    
    from logging_framework.logger import get_platform_logger, log_application_attempt
    
    # Get platform-specific logger
    logger = get_platform_logger("demo_platform")
    
    # Log some demo events
    logger.info("Starting demo platform operations")
    logger.warning("This is a warning message")
    
    # Log application attempts
    log_application_attempt(
        "demo_platform",
        "Demo Engineer",
        "Demo Company",
        True,
        {"job_id": "demo123", "salary": "$100,000"}
    )
    
    log_application_attempt(
        "demo_platform",
        "Another Demo Engineer",
        "Another Company",
        False,
        {"job_id": "demo456", "error": "Form submission failed"}
    )
    
    print("✅ Logging examples completed - check logs/ directory for output")


def demonstrate_enhanced_bot():
    """Demonstrate the enhanced job bot."""
    print("\n🤖 Demonstrating enhanced job bot...")
    
    # Create bot configuration
    config = {
        'job_preferences': {
            'titles': [
                "DevOps Engineer",
                "Cloud Engineer",
                "Platform Engineer"
            ],
            'skills': [
                "AWS",
                "Docker",
                "Kubernetes",
                "Python"
            ],
            'remote_only': True,
            'salary_min': 80000
        },
        'platforms': ['remoteok']  # Only use RemoteOK for demo
    }
    
    # Create enhanced bot
    bot = EnhancedJobBot(config)
    
    try:
        # Get bot statistics
        stats = bot.get_statistics()
        print(f"📊 Bot Statistics:")
        print(f"   Runtime: {stats['runtime_formatted']}")
        print(f"   Total searches: {stats['total_searches']}")
        print(f"   Total applications: {stats['total_applications']}")
        print(f"   Successful applications: {stats['successful_applications']}")
        
        print("✅ Enhanced bot demonstration completed")
        
    finally:
        # Clean up
        bot.cleanup()


def main():
    """Main demonstration function."""
    print("🚀 Enhanced Job Bot Security and Reliability Demo")
    print("=" * 50)
    
    try:
        # Demonstrate each feature
        setup_credentials()
        demonstrate_application_tracking()
        demonstrate_error_handling()
        demonstrate_logging()
        demonstrate_enhanced_bot()
        
        print("\n🎉 All demonstrations completed successfully!")
        print("\nKey enhancements implemented:")
        print("✅ Secure credential storage with encryption")
        print("✅ Sensitive data masking in logs")
        print("✅ Application tracking with duplicate prevention")
        print("✅ Platform-specific error handling")
        print("✅ Retry logic with exponential backoff")
        print("✅ Consistent logging framework")
        print("✅ Modular platform architecture")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()