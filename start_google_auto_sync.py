#!/usr/bin/env python
import os
import sys
import django
import threading
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

def auto_sync_loop():
    """Run Google Sheets auto-sync every 5 minutes"""
    while True:
        try:
            from django.core.management import call_command
            print(f"🔄 Running Google Sheets auto-sync at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            call_command('auto_sync_google_sheets')
            time.sleep(60)  # 1 minute
        except Exception as e:
            print(f"❌ Auto-sync error: {e}")
            time.sleep(60)  # Wait 1 minute on error

if __name__ == "__main__":
    print("🚀 Starting Google Sheets Auto-Sync Service")
    print("📅 Syncing every 1 minute")
    print("⏰ Press Ctrl+C to stop")
    
    try:
        auto_sync_loop()
    except KeyboardInterrupt:
        print("\n🛑 Auto-sync service stopped")
        sys.exit(0)