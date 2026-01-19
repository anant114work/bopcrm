import schedule
import time
import subprocess
import os
import sys

def run_auto_sync():
    """Run the auto-sync management command"""
    try:
        # Change to project directory
        os.chdir('d:/AI-proto/CRM/drip')
        
        # Run the management command
        result = subprocess.run([
            sys.executable, 'manage.py', 'auto_sync_google_sheets'
        ], capture_output=True, text=True)
        
        print(f"Auto-sync result: {result.stdout}")
        if result.stderr:
            print(f"Auto-sync error: {result.stderr}")
            
    except Exception as e:
        print(f"Auto-sync scheduler error: {str(e)}")

# Schedule auto-sync every 5 minutes
schedule.every(5).minutes.do(run_auto_sync)

print("🔄 Google Sheets Auto-Sync Scheduler Started")
print("📅 Running every 5 minutes")
print("⏰ Press Ctrl+C to stop")

# Keep the scheduler running
while True:
    schedule.run_pending()
    time.sleep(1)