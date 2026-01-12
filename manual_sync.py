import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.meta_sync import sync_recent_meta_leads
from datetime import datetime

print(f"[{datetime.now()}] Starting manual Meta sync...")
result = sync_recent_meta_leads()
print(f"Result: {result}")

# Also try syncing last 3 days
from leads.meta_sync import sync_meta_leads
from datetime import timedelta
end_date = datetime.now()
start_date = end_date - timedelta(days=3)
print(f"\n[{datetime.now()}] Syncing last 3 days...")
result2 = sync_meta_leads(start_date, end_date)
print(f"Result: {result2}")