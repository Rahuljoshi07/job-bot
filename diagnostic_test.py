#!/usr/bin/env python3
"""
Diagnostic script to test all job bot components
"""

import sys
import traceback
from datetime import datetime

def test_component(name, test_func):
    """Test a component and return results"""
    print(f"\n{'='*50}")
    print(f"🔍 TESTING: {name}")
    print(f"{'='*50}")
    
    try:
        result = test_func()
        print(f"✅ {name}: WORKING")
        return True, result
    except Exception as e:
        print(f"❌ {name}: FAILED")
        print(f"Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False, str(e)

def test_basic_imports():
    """Test basic Python imports"""
    import requests
    import json
    import time
    import os
    return "Basic imports successful"

def test_config_system():
    """Test configuration system"""
    from config import Config
    config = Config()
    user_config = config.load_config()
    return f"Config loaded with {len(user_config)} sections"

def test_resume_analyzer():
    """Test resume analyzer"""
    from resume_analyzer import ResumeAnalyzer
    analyzer = ResumeAnalyzer()
    result = analyzer.analyze_resume()
    return f"Resume analyzed, found {len(result.get('skills', []))} skills" if result else "Resume analysis failed"

def test_basic_job_bot():
    """Test basic job bot functionality"""
    from job_bot import JobBot
    bot = JobBot()
    jobs = bot.search_remoteok()
    return f"Basic bot found {len(jobs)} jobs"

def test_selenium_setup():
    """Test Selenium browser setup using new browser manager"""
    from browser_manager import BrowserManager
    
    manager = BrowserManager()
    if manager.setup_browser(headless=True):
        manager.driver.get("https://www.google.com")
        title = manager.driver.title
        manager.quit()
        return f"Browser automation working with {manager.browser_type}, accessed Google: {title}"
    else:
        raise Exception("Browser setup failed")

def test_advanced_bot_import():
    """Test advanced bot imports"""
    from ultimate_job_bot import UltimateJobBot
    bot = UltimateJobBot()
    return "Ultimate job bot imported successfully"

def test_mega_bot_import():
    """Test mega bot imports"""
    from mega_job_bot import MegaJobBot
    bot = MegaJobBot()
    return "Mega job bot imported successfully"

def test_api_connectivity():
    """Test API connectivity"""
    import requests
    
    # Test RemoteOK API
    response = requests.get("https://remoteok.io/api", timeout=10)
    if response.status_code == 200:
        jobs = response.json()
        return f"RemoteOK API working, {len(jobs)} jobs available"
    else:
        return f"RemoteOK API failed with status {response.status_code}"

def test_file_operations():
    """Test file read/write operations"""
    test_file = "diagnostic_test_file.txt"
    test_content = f"Test written at {datetime.now()}"
    
    # Write test
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    # Read test
    with open(test_file, 'r') as f:
        content = f.read()
    
    # Cleanup
    import os
    os.remove(test_file)
    
    return f"File operations working, wrote and read {len(content)} characters"

def test_json_operations():
    """Test JSON operations"""
    import json
    
    test_data = {
        "test": True,
        "timestamp": str(datetime.now()),
        "numbers": [1, 2, 3, 4, 5]
    }
    
    # Test JSON serialization
    json_string = json.dumps(test_data)
    
    # Test JSON deserialization
    parsed_data = json.loads(json_string)
    
    return f"JSON operations working, serialized {len(json_string)} characters"

def run_comprehensive_diagnostic():
    """Run comprehensive diagnostic test"""
    print("🤖 JOB BOT COMPREHENSIVE DIAGNOSTIC")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")
    print("=" * 60)
    
    # Define all tests
    tests = [
        ("Basic Python Imports", test_basic_imports),
        ("File Operations", test_file_operations),
        ("JSON Operations", test_json_operations),
        ("API Connectivity", test_api_connectivity),
        ("Configuration System", test_config_system),
        ("Resume Analyzer", test_resume_analyzer),
        ("Basic Job Bot", test_basic_job_bot),
        ("Advanced Bot Import", test_advanced_bot_import),
        ("Mega Bot Import", test_mega_bot_import),
        ("Selenium Setup", test_selenium_setup),
    ]
    
    results = {}
    working_count = 0
    total_count = len(tests)
    
    # Run all tests
    for test_name, test_func in tests:
        success, result = test_component(test_name, test_func)
        results[test_name] = {
            'success': success,
            'result': result
        }
        if success:
            working_count += 1
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 DIAGNOSTIC SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests: {total_count}")
    print(f"Working: {working_count}")
    print(f"Failed: {total_count - working_count}")
    print(f"Success rate: {(working_count/total_count)*100:.1f}%")
    
    print(f"\n{'='*60}")
    print("🔍 DETAILED RESULTS")
    print(f"{'='*60}")
    
    for test_name, result in results.items():
        status = "✅ WORKING" if result['success'] else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result['success']:
            print(f"   └─ {result['result']}")
        else:
            print(f"   └─ Error: {result['result']}")
    
    # Recommendations
    print(f"\n{'='*60}")
    print("💡 RECOMMENDATIONS")
    print(f"{'='*60}")
    
    if not results.get("Selenium Setup", {}).get('success', False):
        print("❌ Selenium not working:")
        print("   - Chrome browser may not be installed")
        print("   - ChromeDriver compatibility issue")
        print("   - Try installing Chrome browser first")
        print("   - Some advanced bots will not work")
    
    if not results.get("Configuration System", {}).get('success', False):
        print("❌ Configuration system issues:")
        print("   - .env file may be missing or invalid")
        print("   - Environment variables not set correctly")
        print("   - Check .env.example for reference")
    
    if results.get("Basic Job Bot", {}).get('success', False):
        print("✅ Basic functionality working:")
        print("   - API-based job search is functional")
        print("   - Can run basic automation without browser")
    
    if results.get("API Connectivity", {}).get('success', False):
        print("✅ API connectivity working:")
        print("   - RemoteOK API accessible")
        print("   - Can fetch job listings")
    
    print(f"\n{'='*60}")
    print("🚀 NEXT STEPS")
    print(f"{'='*60}")
    
    if working_count >= total_count * 0.7:  # 70% working
        print("✅ Most components working!")
        print("   - You can run API-based job searches")
        print("   - Basic automation is functional")
        if not results.get("Selenium Setup", {}).get('success', False):
            print("   - Install Chrome browser for full functionality")
    else:
        print("⚠️ Several components need attention:")
        print("   - Check Python dependencies")
        print("   - Verify environment configuration")
        print("   - Install missing browsers/drivers")
    
    return results

if __name__ == "__main__":
    results = run_comprehensive_diagnostic()
