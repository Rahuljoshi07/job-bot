#!/usr/bin/env python3
"""
🚀 FIXED JOB BOT STARTER SCRIPT
Launches the fixed job application bot with enhanced verification
"""

import os
import sys
import time
import traceback
from datetime import datetime

def main():
    """Start the fixed job bot"""
    print("=" * 60)
    print("🚀 STARTING FIXED JOB BOT WITH ENHANCED VERIFICATION")
    print("=" * 60)
    print(f"🕐 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🖥️  Environment: {'GitHub Actions' if os.getenv('GITHUB_ACTIONS') == 'true' else 'Local'}")
    print("=" * 60)
    
    try:
        # Import and run the fixed job bot
        from fixed_job_bot import FixedJobBot
        
        # Create bot instance
        print("🔧 Initializing Fixed Job Bot...")
        bot = FixedJobBot()
        
        # Run the bot
        print("🚀 Starting job application process...")
        
        # Add run method call
        success = bot.run()
        
        if success:
            print("\n🎉 FIXED JOB BOT COMPLETED SUCCESSFULLY!")
            print("✅ Job applications submitted with verification")
            return 0
        else:
            print("\n⚠️ Bot completed with some issues")
            print("⚠️ Check verification logs for details")
            return 1
            
    except Exception as e:
        print(f"\n❌ STARTUP ERROR: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
