import os
import django
import time
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

def run_sync():
    try:
        from tata_integration.management.commands.auto_sync import Command
        cmd = Command()
        cmd.handle()
        print(f"[{datetime.now()}] Sync completed")
    except Exception as e:
        print(f"[{datetime.now()}] Sync error: {e}")

if __name__ == "__main__":
    print("Starting auto-sync every 5 minutes...")
    while True:
        run_sync()
        time.sleep(300)  # 5 minutes