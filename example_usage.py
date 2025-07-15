#!/usr/bin/env python3
"""
Example usage of enhanced fixed_job_bot.py with platform rotation and retry mechanisms
"""
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, '.')

def setup_example_environment():
    """Setup example environment variables"""
    example_env = {
        'PERSONAL_FULL_NAME': 'John Doe',
        'PERSONAL_EMAIL': 'john.doe@example.com',
        'PERSONAL_PHONE': '+1-555-123-4567',
        'PERSONAL_LOCATION': 'Remote',
        'LINKEDIN_EMAIL': 'john.doe@example.com',
        'LINKEDIN_PASSWORD': 'your_linkedin_password',
        'INDEED_EMAIL': 'john.doe@example.com',
        'INDEED_PASSWORD': 'your_indeed_password',
        'DICE_EMAIL': 'john.doe@example.com',
        'DICE_PASSWORD': 'your_dice_password',
        'TWITTER_EMAIL': 'john.doe@example.com',
        'TWITTER_PASSWORD': 'your_twitter_password',
        'TURING_EMAIL': 'john.doe@example.com',
        'TURING_PASSWORD': 'your_turing_password',
        'EMAIL_VERIFICATION_ENABLED': 'true',
        'EMAIL_APP_PASSWORD': 'your_email_app_password',
        'EMAIL_VERIFICATION_TIMEOUT': '300',
        'EMAIL_CHECK_INTERVAL': '30'
    }
    
    for key, value in example_env.items():
        if key not in os.environ:
            os.environ[key] = value

def example_single_platform_cycle():
    """Example 1: Run a single platform cycle with enhanced features"""
    print("🔥 Example 1: Single Platform Cycle with Enhanced Features")
    print("=" * 60)
    
    try:
        setup_example_environment()
        from fixed_job_bot import FixedJobBot
        
        # Create bot instance
        bot = FixedJobBot()
        
        # Run single platform cycle with enhanced parameters
        result = bot.run_platform_cycle(
            platform="LinkedIn",
            max_jobs_per_search=3,  # Limit to 3 jobs per search to avoid rate limiting
            max_retries=3           # Retry up to 3 times if failures occur
        )
        
        # Display results
        print("\n📊 Single Platform Cycle Results:")
        print(f"   Success: {result['success']}")
        print(f"   Platform: {result['platform']}")
        print(f"   Jobs Found: {result['jobs_found']}")
        print(f"   Jobs Applied: {result['jobs_applied']}")
        print(f"   Duration: {result['duration']:.2f} seconds")
        print(f"   Retry Count: {result['retry_count']}")
        
        if not result['success']:
            print(f"   Error: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Example 1 failed: {e}")
        return None

def example_comprehensive_cycle():
    """Example 2: Run comprehensive cycle across multiple platforms"""
    print("\n\n🔥 Example 2: Comprehensive Multi-Platform Cycle")
    print("=" * 60)
    
    try:
        setup_example_environment()
        from fixed_job_bot import FixedJobBot
        
        # Create bot instance
        bot = FixedJobBot()
        
        # Define platforms to cycle through
        platforms = ["LinkedIn", "Indeed", "RemoteOK", "Dice"]
        
        # Run comprehensive cycle
        result = bot.run_comprehensive_cycle(
            platforms=platforms,
            max_jobs_per_platform=20,  # Total jobs per platform
            cycle_delay=60            # Wait 60 seconds between platforms
        )
        
        # Display results
        print("\n📊 Comprehensive Cycle Results:")
        print(f"   Overall Success: {result['success']}")
        print(f"   Total Jobs Found: {result['total_jobs_found']}")
        print(f"   Total Jobs Applied: {result['total_jobs_applied']}")
        print(f"   Success Rate: {result['success_rate']:.1%}")
        print(f"   Duration: {result['duration']:.2f} seconds")
        print(f"   Successful Platforms: {result['successful_platforms']}")
        print(f"   Failed Platforms: {result['failed_platforms']}")
        
        # Show platform-specific results
        print("\n📋 Platform-Specific Results:")
        for platform, platform_result in result['platform_results'].items():
            print(f"   {platform}:")
            print(f"      Success: {platform_result['success']}")
            print(f"      Jobs Found: {platform_result['jobs_found']}")
            print(f"      Jobs Applied: {platform_result['jobs_applied']}")
            if not platform_result['success']:
                print(f"      Error: {platform_result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Example 2 failed: {e}")
        return None

def example_smart_retry():
    """Example 3: Smart retry mechanism for failed platforms"""
    print("\n\n🔥 Example 3: Smart Retry Mechanism")
    print("=" * 60)
    
    try:
        setup_example_environment()
        from fixed_job_bot import FixedJobBot
        
        # Create bot instance
        bot = FixedJobBot()
        
        # Simulate failed platforms (in real use, this would come from comprehensive cycle)
        failed_platforms = ["LinkedIn", "Indeed"]
        
        # Run smart retry cycle
        result = bot.run_smart_retry_cycle(
            failed_platforms=failed_platforms,
            max_attempts=2
        )
        
        # Display results
        print("\n📊 Smart Retry Results:")
        print(f"   Success: {result['success']}")
        print(f"   Platforms Retried Successfully: {result['retried_platforms']}")
        print(f"   Platforms Still Failed: {result['failed_platforms']}")
        
        # Show retry-specific results
        print("\n📋 Retry-Specific Results:")
        for platform, retry_result in result['retry_results'].items():
            print(f"   {platform}:")
            print(f"      Success: {retry_result['success']}")
            if retry_result['success']:
                print(f"      Jobs Found: {retry_result['jobs_found']}")
                print(f"      Jobs Applied: {retry_result['jobs_applied']}")
            else:
                print(f"      Error: {retry_result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Example 3 failed: {e}")
        return None

def example_email_verification():
    """Example 4: Email verification system"""
    print("\n\n🔥 Example 4: Email Verification System")
    print("=" * 60)
    
    try:
        setup_example_environment()
        from fixed_job_bot import FixedJobBot
        
        # Create bot instance
        bot = FixedJobBot()
        
        # Example email verification check
        verification_result = bot._enhanced_email_verification_check(
            platform="LinkedIn",
            job_title="DevOps Engineer",
            company_name="TechCorp",
            application_time=datetime.now()
        )
        
        # Display results
        print("\n📊 Email Verification Results:")
        print(f"   Status: {verification_result['status']}")
        print(f"   Message: {verification_result['message']}")
        
        if verification_result['status'] == 'confirmed':
            print(f"   Details: {verification_result['details']}")
        
        return verification_result
        
    except Exception as e:
        print(f"❌ Example 4 failed: {e}")
        return None

def example_full_workflow():
    """Example 5: Complete workflow combining all features"""
    print("\n\n🔥 Example 5: Complete Enhanced Workflow")
    print("=" * 60)
    
    try:
        setup_example_environment()
        from fixed_job_bot import FixedJobBot
        
        # Create bot instance
        bot = FixedJobBot()
        
        print("🚀 Starting complete enhanced workflow...")
        
        # Step 1: Run comprehensive cycle
        print("\n📋 Step 1: Running comprehensive cycle...")
        comprehensive_result = bot.run_comprehensive_cycle(
            platforms=["LinkedIn", "Indeed", "RemoteOK"],
            max_jobs_per_platform=15,
            cycle_delay=30
        )
        
        print(f"   Comprehensive cycle success: {comprehensive_result['success']}")
        print(f"   Failed platforms: {comprehensive_result['failed_platforms']}")
        
        # Step 2: Run smart retry for failed platforms
        if comprehensive_result['failed_platforms']:
            print("\n📋 Step 2: Running smart retry for failed platforms...")
            retry_result = bot.run_smart_retry_cycle(
                failed_platforms=comprehensive_result['failed_platforms'],
                max_attempts=2
            )
            
            print(f"   Retry success: {retry_result['success']}")
            print(f"   Recovered platforms: {retry_result['retried_platforms']}")
        else:
            print("\n📋 Step 2: No failed platforms to retry")
        
        # Step 3: Display final statistics
        print("\n📊 Final Workflow Statistics:")
        print(f"   Total Jobs Found: {comprehensive_result['total_jobs_found']}")
        print(f"   Total Jobs Applied: {comprehensive_result['total_jobs_applied']}")
        print(f"   Overall Success Rate: {comprehensive_result['success_rate']:.1%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Example 5 failed: {e}")
        return False

def main():
    """Run all examples"""
    print("🚀 Enhanced Fixed Job Bot - Usage Examples")
    print("=" * 80)
    
    examples = [
        ("Single Platform Cycle", example_single_platform_cycle),
        ("Comprehensive Multi-Platform Cycle", example_comprehensive_cycle),
        ("Smart Retry Mechanism", example_smart_retry),
        ("Email Verification System", example_email_verification),
        ("Complete Enhanced Workflow", example_full_workflow)
    ]
    
    print("\n⚠️  NOTE: These examples use mock data and will not perform actual job applications")
    print("   To use with real job applications, configure your credentials properly.")
    
    for example_name, example_func in examples:
        print(f"\n{'='*80}")
        try:
            example_func()
        except Exception as e:
            print(f"❌ {example_name} failed: {e}")
    
    print(f"\n{'='*80}")
    print("✅ All examples completed!")
    print("\nFor production use:")
    print("1. Set up proper credentials in environment variables")
    print("2. Configure email verification settings")
    print("3. Adjust job search parameters as needed")
    print("4. Monitor logs for detailed execution information")

if __name__ == "__main__":
    main()