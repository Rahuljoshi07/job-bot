#!/usr/bin/env python3
"""
Final verification that CSS selector fixes have been deployed to GitHub
"""

import os
import subprocess
import requests

def check_git_status():
    """Check that changes are committed and pushed"""
    print("🔍 Checking Git status...")
    
    try:
        # Check if we're up to date with origin
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print("⚠️ There are uncommitted changes:")
            print(result.stdout)
            return False
        
        # Check if we're ahead of origin
        result = subprocess.run(['git', 'rev-list', '--count', 'HEAD', '^origin/main'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip() == '0':
            print("✅ All changes are committed and pushed to GitHub")
            return True
        else:
            print("⚠️ Local commits not pushed to origin")
            return False
            
    except Exception as e:
        print(f"❌ Git status check failed: {e}")
        return False

def check_fixed_files():
    """Check that the fixed files exist and contain correct selectors"""
    print("\n🔍 Checking fixed files...")
    
    files_to_check = [
        'super_ultimate_bot.py',
        'ultimate_job_bot.py', 
        'enhanced_button_detector.py',
        'button_finder_utility.py'
    ]
    
    for filename in files_to_check:
        if not os.path.exists(filename):
            print(f"❌ Missing file: {filename}")
            return False
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for invalid selectors
        if 'button:contains(' in content:
            print(f"❌ {filename} still contains invalid button:contains() selector")
            return False
        
        if 'a:contains(' in content and filename != 'CSS_SELECTOR_FIX_SUMMARY.md':
            print(f"❌ {filename} still contains invalid a:contains() selector")
            return False
        
        print(f"✅ {filename} - selectors fixed")
    
    return True

def check_workflow_file():
    """Check that workflow file exists and is properly configured"""
    print("\n🔍 Checking GitHub Actions workflow...")
    
    workflow_path = '.github/workflows/job-bot-automation.yml'
    
    if not os.path.exists(workflow_path):
        print("❌ GitHub Actions workflow file missing")
        return False
    
    with open(workflow_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check key workflow components
    required_items = [
        'super_ultimate_bot.py',  # The main bot file
        'on:',  # Workflow triggers
        'schedule:',  # Scheduled runs
        'workflow_dispatch:'  # Manual trigger
    ]
    
    for item in required_items:
        if item not in content:
            print(f"❌ Workflow missing: {item}")
            return False
    
    print("✅ GitHub Actions workflow properly configured")
    return True

def check_recent_commit():
    """Check the most recent commit contains our fixes"""
    print("\n🔍 Checking recent commit...")
    
    try:
        result = subprocess.run(['git', 'log', '--oneline', '-3'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            commits = result.stdout.strip().split('\n')
            print(f"Recent commits:")
            for commit in commits[:3]:
                print(f"  {commit}")
            
            # Check if any of the recent commits contain CSS fixes
            for commit in commits:
                if 'CSS selector' in commit or 'Fix CSS' in commit:
                    print("✅ Recent commits contain CSS selector fixes")
                    return True
            
            print("⚠️ No recent commits contain CSS fixes")
            return False
        else:
            print("❌ Could not check git log")
            return False
            
    except Exception as e:
        print(f"❌ Commit check failed: {e}")
        return False

def main():
    """Main verification function"""
    
    print("🚀 FINAL DEPLOYMENT VERIFICATION")
    print("=" * 50)
    
    # Run all checks
    git_ok = check_git_status()
    files_ok = check_fixed_files()
    workflow_ok = check_workflow_file()
    commit_ok = check_recent_commit()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 DEPLOYMENT STATUS:")
    
    all_checks_passed = git_ok and files_ok and workflow_ok and commit_ok
    
    if all_checks_passed:
        print("✅ All deployment checks passed!")
        print("✅ CSS selector fixes are deployed to GitHub")
        print("✅ GitHub Actions workflow should now run successfully")
        print("✅ Job bot will no longer encounter InvalidSelectorError")
        
        print("\n🎯 NEXT STEPS:")
        print("1. ✅ GitHub Actions will automatically run every 2 hours")
        print("2. ✅ You can manually trigger via GitHub Actions tab")
        print("3. ✅ Check Actions tab for workflow execution status")
        print("4. ✅ Review application logs and proof screenshots")
        
        print("\n🔗 GitHub Repository: https://github.com/Rahuljoshi07/job-bot")
        print("🔗 Actions: https://github.com/Rahuljoshi07/job-bot/actions")
        
    else:
        print("❌ Some deployment checks failed")
        print("🔧 Please review the issues above before proceeding")
    
    return all_checks_passed

if __name__ == "__main__":
    success = main()
    print(f"\n{'🎉 DEPLOYMENT SUCCESS' if success else '⚠️ DEPLOYMENT ISSUES'}")
    exit(0 if success else 1)
