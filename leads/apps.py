from django.apps import AppConfig
import threading
import time
import subprocess
import sys
import os

class LeadsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'leads'
    
    def ready(self):
        from . import auto_assign_signal
        # Start Google Sheets auto-sync when Django starts
        if os.environ.get('RUN_MAIN') == 'true':  # Only run in main process
            self.start_google_sheets_auto_sync()
    
    def start_google_sheets_auto_sync(self):
        def run_auto_sync():
            time.sleep(10)  # Wait for Django to fully start
            while True:
                try:
                    from django.core.management import call_command
                    print(f"🔄 Auto-syncing Google Sheets at {time.strftime('%H:%M:%S')}")
                    call_command('auto_sync_google_sheets')
                    time.sleep(60)  # 1 minute
                except Exception as e:
                    print(f"❌ Auto-sync error: {e}")
                    time.sleep(60)  # Wait 1 minute on error
        
        # Start in background thread
        thread = threading.Thread(target=run_auto_sync, daemon=True)
        thread.start()
        print("🚀 Google Sheets Auto-Sync started automatically (every 1 minute)")
