#!/usr/bin/env python
"""
Manual script to sync Meta leads from a specific date
Run this to sync leads from 16th onwards
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from datetime import datetime, timedelta
from leads.meta_sync import sync_meta_leads

# Sync from 16th of current month to now
today = datetime.now()
start_date = datetime(today.year, today.month, 16, 0, 0, 0)

print(f"Syncing Meta leads from {start_date} to {today}")
print("=" * 60)

result = sync_meta_leads(start_date=start_date, end_date=today)

print(f"\nSync Results:")
print(f"  Synced: {result['synced']} leads")
print(f"  Success: {result['success']}")
print(f"  Message: {result['message']}")

if result['errors']:
    print(f"\nErrors:")
    for error in result['errors']:
        print(f"  - {error}")
else:
    print("\n✓ No errors!")

print("=" * 60)