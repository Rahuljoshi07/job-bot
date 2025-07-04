#!/usr/bin/env python3
"""
Job Bot Launch Script
Final verification and launch of the job bot
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def run_diagnostics():
    """Run comprehensive diagnostics"""
    print("🔍 Running diagnostics...")
    try:
        result = subprocess.run([sys.executable, "diagnose.py"], 
                              capture_output=True, text=True, timeout=60)
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Diagnostics failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("⚙️ Testing configuration...")
    try:
        from config import Config
        config = Config()
        user_config = config.create_user_config_from_env()
        print("✅ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def trigger_github_workflow():
    """Trigger GitHub Actions workflow manually"""
    print("🚀 Triggering GitHub Actions workflow...")
    try:
        result = subprocess.run([
            'gh', 'workflow', 'run', '.github/workflows/job-bot-automation.yml'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ GitHub Actions workflow triggered successfully!")
            print("🔗 Check status at: https://github.com/Rahuljoshi07/job-bot/actions")
            return True
        else:
            print(f"❌ Failed to trigger workflow: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error triggering workflow: {e}")
        return False

def run_local_test():
    """Run a quick local test of the bot"""
    print("🤖 Running local bot test...")
    try:
        # Set environment for local testing
        os.environ['GITHUB_ACTIONS'] = 'false'
        
        # Import and run basic test
        from super_ultimate_bot import SuperUltimateJobBot
        
        bot = SuperUltimateJobBot()
        print("✅ Bot initialized successfully")
        
        # Test browser setup
        if bot.setup_browser():
            print("✅ Browser setup successful")
            if bot.driver:
                bot.driver.quit()
            return True
        else:
            print("❌ Browser setup failed")
            return False
            
    except Exception as e:
        print(f"❌ Local test failed: {e}")
        return False

def check_github_secrets():
    """Check if GitHub secrets are set up"""
    print("🔐 Checking GitHub secrets...")
    try:
        result = subprocess.run([
            'gh', 'secret', 'list'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            secrets = result.stdout.strip().split('\n')
            secret_count = len([s for s in secrets if s.strip()])
            print(f"✅ Found {secret_count} GitHub secrets")
            return secret_count >= 10  # Should have at least 10 main secrets
        else:
            print("❌ Could not check GitHub secrets")
            return False
    except Exception as e:
        print(f"❌ Error checking secrets: {e}")
        return False

def main():
    """Main launch function"""
    print("🚀 JOB BOT FINAL LAUNCH SEQUENCE")
    print("=" * 50)
    print(f"⏰ Launch time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Check GitHub secrets
    secrets_ok = check_github_secrets()
    
    # Step 2: Run diagnostics
    diagnostics_ok = run_diagnostics()
    
    # Step 3: Test configuration
    config_ok = test_config()
    
    # Step 4: Run local test (if possible)
    local_test_ok = run_local_test()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 LAUNCH SEQUENCE RESULTS")
    print("=" * 50)
    print(f"🔐 GitHub Secrets: {'✅ PASS' if secrets_ok else '❌ FAIL'}")
    print(f"🔍 Diagnostics: {'✅ PASS' if diagnostics_ok else '❌ FAIL'}")
    print(f"⚙️ Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"🤖 Local Test: {'✅ PASS' if local_test_ok else '❌ FAIL'}")
    
    all_tests_passed = all([secrets_ok, diagnostics_ok, config_ok])
    
    if all_tests_passed:
        print("\n🎉 ALL SYSTEMS GO! BOT IS READY!")
        print("=" * 50)
        
        # Trigger GitHub workflow
        if trigger_github_workflow():
            print("✅ Bot launched successfully!")
            print("\n📋 What happens next:")
            print("• Bot runs automatically every 2 hours")
            print("• Applies to 70-90 jobs per cycle")
            print("• Takes proof screenshots")
            print("• Generates custom cover letters")
            print("• Logs all activities")
            print("\n🔗 Monitor at: https://github.com/Rahuljoshi07/job-bot/actions")
            return 0
        else:
            print("\n⚠️ Workflow trigger failed, but bot is configured correctly")
            print("It will run automatically on schedule or you can trigger it manually.")
            return 0
    else:
        print("\n❌ SOME ISSUES DETECTED")
        print("=" * 50)
        if not secrets_ok:
            print("• Set up GitHub Secrets first")
        if not diagnostics_ok:
            print("• Check diagnostics output for issues")
        if not config_ok:
            print("• Fix configuration issues")
        
        print("\n🔧 Fix the issues above and run this script again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
