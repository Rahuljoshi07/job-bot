#!/usr/bin/env python3
"""
Monitor GitHub Actions workflow progress
"""

import subprocess
import time
import json
import sys

def get_latest_run():
    """Get the latest workflow run"""
    try:
        result = subprocess.run([
            'gh', 'run', 'list', 
            '--workflow=job-bot-automation.yml', 
            '--limit=1', 
            '--json'
        ], capture_output=True, text=True, check=True)
        
        runs = json.loads(result.stdout)
        if runs:
            return runs[0]
        return None
    except Exception as e:
        print(f"Error getting runs: {e}")
        return None

def get_run_details(run_id):
    """Get detailed information about a run"""
    try:
        result = subprocess.run([
            'gh', 'run', 'view', str(run_id), '--json'
        ], capture_output=True, text=True, check=True)
        
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error getting run details: {e}")
        return None

def print_status(run_data):
    """Print formatted status"""
    if not run_data:
        print("❌ No run data available")
        return
    
    status = run_data.get('status', 'unknown')
    conclusion = run_data.get('conclusion', '')
    
    # Status emoji mapping
    status_emojis = {
        'in_progress': '🔄',
        'completed': '✅',
        'cancelled': '🚫',
        'failed': '❌',
        'queued': '⏳'
    }
    
    conclusion_emojis = {
        'success': '✅',
        'failure': '❌',
        'cancelled': '🚫',
        'skipped': '⏭️'
    }
    
    emoji = status_emojis.get(status, '❓')
    if conclusion:
        emoji = conclusion_emojis.get(conclusion, emoji)
    
    print(f"{emoji} Status: {status.upper()}")
    if conclusion:
        print(f"🎯 Conclusion: {conclusion.upper()}")
    
    print(f"🔗 URL: {run_data.get('url', 'N/A')}")
    print(f"⏱️ Started: {run_data.get('createdAt', 'N/A')}")
    
    if 'jobs' in run_data:
        print("\n📋 Jobs:")
        for job in run_data['jobs']:
            job_status = job.get('status', 'unknown')
            job_conclusion = job.get('conclusion', '')
            job_emoji = status_emojis.get(job_status, '❓')
            if job_conclusion:
                job_emoji = conclusion_emojis.get(job_conclusion, job_emoji)
            print(f"  {job_emoji} {job.get('name', 'Unknown Job')}")

def monitor_workflow():
    """Monitor workflow progress"""
    print("🔍 Monitoring GitHub Actions workflow...")
    print("=" * 50)
    
    last_status = None
    
    while True:
        # Get latest run
        run = get_latest_run()
        if not run:
            print("❌ No workflow runs found")
            break
        
        run_id = run['databaseId']
        current_status = run.get('status')
        
        # Get detailed information
        details = get_run_details(run_id)
        
        # Only print if status changed
        if current_status != last_status:
            print(f"\n📊 Workflow Update - {time.strftime('%H:%M:%S')}")
            print("-" * 30)
            print_status(details)
            last_status = current_status
        
        # Check if completed
        if current_status in ['completed', 'cancelled']:
            print(f"\n🏁 Workflow {current_status}!")
            
            if details and details.get('conclusion') == 'success':
                print("🎉 SUCCESS! Job bot executed successfully!")
                print("\n📁 Check the following for results:")
                print("  • Artifacts in the Actions tab")
                print("  • application_proofs/ screenshots")
                print("  • enhanced_applications.txt log")
                print("  • job_bot.db analytics")
            elif details and details.get('conclusion') == 'failure':
                print("❌ FAILED! Check the logs for errors.")
                print("🔗 View logs:", details.get('url', ''))
            
            break
        
        # Wait before next check
        time.sleep(10)

def main():
    """Main function"""
    try:
        monitor_workflow()
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
